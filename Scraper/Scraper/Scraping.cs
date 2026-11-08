using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Scraper
{
    public static class Scraping
    {
        static readonly string[] Tiendas = { "Steam", "Nintendo eShop" };

        public static Dictionary<string, Juego> Anteriores = new Dictionary<string, Juego>();

        // Version paralela. Nivel 1: N hilos toman juegos de una cola compartida
        public static Juego[] Paralelo(List<JuegoRepo> juegos, int workers)
        {
            var resultados = new Juego[juegos.Count];
            var cola = new ConcurrentQueue<int>();
            for (int i = 0; i < juegos.Count; i++)
                cola.Enqueue(i);

            var hilos = new List<Thread>();
            for (int w = 0; w < workers; w++)
            {
                var hilo = new Thread(() =>
                {
                    int i;
                    while (cola.TryDequeue(out i))
                        resultados[i] = ProcesarParalelo(juegos[i]).GetAwaiter().GetResult();
                });
                hilos.Add(hilo);
                hilo.Start();
            }

            foreach (var hilo in hilos)
                hilo.Join();
            return resultados;
        }

        // Nivel 2: cada fuente del juego corre en su propia tarea del ThreadPool,
        // que reparte las tareas entre los nucleos
        static async Task<Juego> ProcesarParalelo(JuegoRepo juego)
        {
            var tiendas = Task.Run(() => ConsultarTiendas(juego));
            var metacritic = Task.Run(() => Intentar(() => Metacritic.Consultar(juego)));
            var hltb = Task.Run(() => Intentar(() => Hltb.Consultar(juego)));
            await Task.WhenAll(tiendas, metacritic, hltb);
            return Unir(juego, tiendas.Result, metacritic.Result, hltb.Result);
        }

        // Nivel 3: cada tienda corre en su propia tarea del ThreadPool
        static async Task<Respuesta<Oferta>[]> ConsultarTiendas(JuegoRepo juego)
        {
            var steam = Task.Run(() => Intentar(() => Steam.Consultar(juego)));
            var eshop = Task.Run(() => Intentar(() => Eshop.Consultar(juego)));
            return await Task.WhenAll(steam, eshop);
        }

        // Version secuencial de referencia: un juego, una fuente y una tienda a la vez
        public static Juego[] Secuencial(List<JuegoRepo> juegos)
        {
            var resultados = new Juego[juegos.Count];
            for (int i = 0; i < juegos.Count; i++)
                resultados[i] = ProcesarSecuencial(juegos[i]).GetAwaiter().GetResult();
            return resultados;
        }

        static async Task<Juego> ProcesarSecuencial(JuegoRepo juego)
        {
            var steam = await Intentar(() => Steam.Consultar(juego));
            var eshop = await Intentar(() => Eshop.Consultar(juego));
            var metacritic = await Intentar(() => Metacritic.Consultar(juego));
            var hltb = await Intentar(() => Hltb.Consultar(juego));
            return Unir(juego, new[] { steam, eshop }, metacritic, hltb);
        }

        static async Task<Respuesta<T>> Intentar<T>(Func<Task<T>> consulta)
        {
            try
            {
                return new Respuesta<T> { Ok = true, Valor = await consulta() };
            }
            catch (Exception ex)
            {
                return new Respuesta<T> { Ok = false, Error = ex.Message };
            }
        }

        // Arma el registro final. Si una fuente fallo se usa el dato de la corrida anterior
        static Juego Unir(JuegoRepo repo, Respuesta<Oferta>[] tiendas, Respuesta<int?> metacritic, Respuesta<double?> hltb)
        {
            Juego anterior;
            Anteriores.TryGetValue(repo.Id, out anterior);

            var juego = new Juego
            {
                Id = repo.Id,
                Nombre = repo.Nombre,
                Plataformas = repo.Plataformas,
                FechaLanzamiento = repo.FechaLanzamiento,
                PrecioReferencia = repo.PrecioReferencia,
                Imagen = repo.Imagen,
                Ofertas = new List<Oferta>()
            };
            bool algunaBien = false;

            for (int t = 0; t < tiendas.Length; t++)
            {
                if (tiendas[t].Ok)
                {
                    juego.Ofertas.Add(tiendas[t].Valor);
                    algunaBien = true;
                    continue;
                }
                Oferta previa = anterior == null || anterior.Ofertas == null ? null : anterior.Ofertas.Find(o => o.Tienda == Tiendas[t]);
                Datos.RegistrarError(repo, Tiendas[t], tiendas[t].Error, previa != null);
                juego.Ofertas.Add(previa ?? new Oferta { Tienda = Tiendas[t] });
            }

            if (metacritic.Ok)
            {
                juego.Metacritic = metacritic.Valor;
                algunaBien = true;
            }
            else
            {
                juego.Metacritic = anterior == null ? null : anterior.Metacritic;
                Datos.RegistrarError(repo, "Metacritic", metacritic.Error, juego.Metacritic != null);
            }

            if (hltb.Ok)
            {
                juego.HorasHltb = hltb.Valor;
                algunaBien = true;
            }
            else
            {
                juego.HorasHltb = anterior == null ? null : anterior.HorasHltb;
                Datos.RegistrarError(repo, "HowLongToBeat", hltb.Error, juego.HorasHltb != null);
            }

            if (algunaBien)
                juego.Actualizado = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ");
            else
                juego.Actualizado = anterior == null ? null : anterior.Actualizado;
            return juego;
        }
    }
}
