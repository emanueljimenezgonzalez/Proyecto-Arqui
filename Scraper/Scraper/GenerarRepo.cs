using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

namespace Scraper
{
    // Arma el REPO con juegos que esten en el eShop y en Steam
    // Se corre una sola vez; despues repo.db se puede editar a mano
    public static class GenerarRepo
    {
        const int PausaEntreJuegosMs = 1000;

        public static void Ejecutar(int cantidad)
        {
            EjecutarAsync(cantidad).GetAwaiter().GetResult();
        }

        static async Task EjecutarAsync(int cantidad)
        {
            var repo = new List<JuegoRepo>();
            var appIds = new HashSet<int>();
            int revisados = 0;
            Datos.CrearRepo();

            for (int pagina = 0; pagina < 10 && repo.Count < cantidad; pagina++)
            {
                JArray hits = await Eshop.Listar(pagina);
                if (hits == null || hits.Count == 0)
                    break;

                foreach (JToken hit in hits)
                {
                    if (repo.Count >= cantidad)
                        break;

                    double? precio = (double?)hit["price"]?["regPrice"];
                    if ((string)hit["platform"] != "Nintendo Switch" || precio == null || precio <= 0)
                        continue;

                    string titulo = ((string)hit["title"]).Trim();
                    revisados++;
                    if (revisados % 25 == 0)
                        Console.WriteLine("Revisados " + revisados + " juegos del eShop, " + repo.Count + " en el REPO");
                    try
                    {
                        JuegoRepo juego = await Armar(titulo);
                        if (juego != null && !appIds.Contains(juego.SteamAppId))
                        {
                            appIds.Add(juego.SteamAppId);
                            repo.Add(juego);
                            Datos.AgregarAlRepo(juego);
                            Console.WriteLine(repo.Count + ". " + juego.Nombre + " (hltb: " + (juego.HltbId == null ? "no" : "si") + ")");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("Error con " + titulo + ": " + ex.Message);
                    }
                    await Task.Delay(PausaEntreJuegosMs);
                }
            }
            Console.WriteLine("REPO con " + repo.Count + " juegos en " + Datos.RutaRepo);
        }

        // Devuelve null si el juego no esta en Steam o no tiene precio ahi
        static async Task<JuegoRepo> Armar(string tituloEshop)
        {
            int? appId = await Steam.BuscarAppId(tituloEshop);
            if (appId == null)
                return null;

            JToken datos = await Steam.Detalles(appId.Value);
            if (datos == null || (string)datos["type"] != "game" || datos["price_overview"] == null)
                return null;

            string nombre = (string)datos["name"];
            return new JuegoRepo
            {
                Id = "steam-" + appId.Value,
                Nombre = nombre,
                Plataformas = new List<string> { "PC", "Switch" },
                FechaLanzamiento = Fecha((string)datos["release_date"]?["date"]),
                PrecioReferencia = (int)datos["price_overview"]["initial"] / 100.0,
                Imagen = (string)datos["header_image"],
                SteamAppId = appId.Value,
                EshopTitulo = tituloEshop,
                MetacriticSlug = SlugMetacritic(datos, nombre),
                HltbId = await Hltb.BuscarId(nombre)
            };
        }

        // Steam da la fecha como "Sep 17, 2020"
        static string Fecha(string texto)
        {
            string[] formatos = { "MMM d, yyyy", "d MMM, yyyy", "MMM yyyy" };
            DateTime fecha;
            if (texto != null && DateTime.TryParseExact(texto, formatos, CultureInfo.InvariantCulture, DateTimeStyles.None, out fecha))
                return fecha.ToString("yyyy-MM-dd");
            return null;
        }

        // Usa el enlace de Metacritic que trae Steam; si no hay, lo arma con el nombre
        static string SlugMetacritic(JToken datos, string nombre)
        {
            string url = (string)datos["metacritic"]?["url"];
            if (url != null)
            {
                Match m = Regex.Match(url, "/game/(?:pc/)?([^/?]+)");
                if (m.Success)
                    return m.Groups[1].Value;
            }
            // Metacritic quita apostrofes y puntos (Freddy's -> freddys)
            string limpio = Regex.Replace(nombre.ToLowerInvariant(), "['’.®™]", "");
            return Regex.Replace(limpio, "[^a-z0-9]+", "-").Trim('-');
        }
    }
}
