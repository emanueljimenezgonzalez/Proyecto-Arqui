using System;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;

namespace Scraper
{
    class Program
    {
        // Uso:
        //   Scraper.exe                 paralelo con todos los nucleos
        //   Scraper.exe --workers 4     paralelo con 4 hilos en el nivel 1
        //   Scraper.exe --secuencial    version secuencial de referencia
        //   --limite K                  procesa solo los primeros K juegos del REPO
        //   Scraper.exe --generar-repo  arma el REPO (200 juegos, o K con --limite)
        // Devuelve 1 si no pudo correr, para que GitHub Actions lo marque como fallo
        static int Main(string[] args)
        {
            Console.OutputEncoding = Encoding.UTF8;

            bool secuencial = args.Contains("--secuencial");
            int workers = LeerNumero(args, "--workers", Environment.ProcessorCount);
            int limite = LeerNumero(args, "--limite", 0);

            if (Datos.Clave("ESHOP_APP_ID") == null || Datos.Clave("ESHOP_API_KEY") == null)
            {
                Console.WriteLine("Faltan ESHOP_APP_ID y ESHOP_API_KEY en " + Path.Combine(Datos.Raiz, ".env") + " (ver .env.example)");
                return 1;
            }

            if (args.Contains("--generar-repo"))
            {
                // No se sobreescribe un REPO que ya existe (puede tener cambios a mano)
                if (File.Exists(Datos.RutaRepo))
                {
                    Console.WriteLine("Ya existe el REPO. Si quiere generarlo de nuevo, borre primero " + Datos.RutaRepo);
                    return 1;
                }
                GenerarRepo.Ejecutar(limite > 0 ? limite : 200);
                return 0;
            }

            if (!File.Exists(Datos.RutaRepo))
            {
                Console.WriteLine("No existe el REPO: " + Datos.RutaRepo);
                return 1;
            }

            var repo = Datos.LeerRepo();
            var juegos = limite > 0 ? repo.Take(limite).ToList() : repo;
            Scraping.Anteriores = Datos.LeerAnteriores();

            if (secuencial)
                Console.WriteLine("Modo secuencial, " + juegos.Count + " juegos");
            else
                Console.WriteLine("Modo paralelo con " + workers + " hilos, " + juegos.Count + " juegos");

            var reloj = Stopwatch.StartNew();
            Juego[] resultados = secuencial ? Scraping.Secuencial(juegos) : Scraping.Paralelo(juegos, workers);
            reloj.Stop();

            Datos.Guardar(repo, resultados, Scraping.Anteriores);

            Console.WriteLine("Errores registrados: " + Datos.CantidadErrores + " (ver " + Datos.RutaErrores + ")");
            Console.WriteLine("Resultados en: " + Datos.RutaSalida);
            Console.WriteLine("Tiempo total: " + reloj.Elapsed.TotalSeconds.ToString("0.000", CultureInfo.InvariantCulture) + " s");
            return 0;
        }

        static int LeerNumero(string[] args, string nombre, int porDefecto)
        {
            int i = Array.IndexOf(args, nombre);
            int valor;
            if (i >= 0 && i + 1 < args.Length && int.TryParse(args[i + 1], out valor) && valor > 0)
                return valor;
            return porDefecto;
        }
    }
}
