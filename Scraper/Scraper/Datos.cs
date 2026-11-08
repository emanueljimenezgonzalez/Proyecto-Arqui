using System;
using System.Collections.Generic;
using System.Data.SQLite;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;

namespace Scraper
{
    public static class Datos
    {
        public static readonly string Raiz = BuscarRaiz();
        public static readonly string RutaRepo = Path.Combine(Raiz, "Proyecto_Web_Scraping_Multinucleo", "app", "repo", "repo.db");
        public static readonly string RutaSalida = Path.Combine(Raiz, "Proyecto_Web_Scraping_Multinucleo", "app", "repo", "games.json");
        public static readonly string RutaErrores = Path.Combine(Raiz, "Scraper", "logs", "errores.csv");

        static readonly object candadoErrores = new object();
        public static int CantidadErrores = 0;

        // Sube carpetas desde el .exe hasta encontrar la raiz del repo
        static string BuscarRaiz()
        {
            var carpeta = new DirectoryInfo(AppDomain.CurrentDomain.BaseDirectory);
            while (carpeta != null && !Directory.Exists(Path.Combine(carpeta.FullName, "Proyecto_Web_Scraping_Multinucleo")))
                carpeta = carpeta.Parent;
            if (carpeta == null)
                throw new Exception("No se encontro la carpeta Proyecto_Web_Scraping_Multinucleo");
            return carpeta.FullName;
        }

        // Lee un valor del archivo .env de la raiz del repo (no se sube a GitHub)
        public static string Clave(string nombre)
        {
            string ruta = Path.Combine(Raiz, ".env");
            if (!File.Exists(ruta))
                return null;

            foreach (string linea in File.ReadAllLines(ruta))
            {
                int igual = linea.IndexOf('=');
                if (igual > 0 && linea.Substring(0, igual).Trim() == nombre)
                {
                    string valor = linea.Substring(igual + 1).Trim();
                    return valor == "" ? null : valor;
                }
            }
            return null;
        }

        // El REPO es una base de datos SQLite (repo.db) con una tabla "juegos"
        static SQLiteConnection AbrirRepo()
        {
            var conexion = new SQLiteConnection("Data Source=" + RutaRepo);
            conexion.Open();
            return conexion;
        }

        public static List<JuegoRepo> LeerRepo()
        {
            var juegos = new List<JuegoRepo>();
            using (var conexion = AbrirRepo())
            using (var comando = new SQLiteCommand("SELECT * FROM juegos ORDER BY rowid", conexion))
            using (var lector = comando.ExecuteReader())
            {
                while (lector.Read())
                {
                    // Una fila sin id no se puede usar (puede pasar si se agrega a mano y queda incompleta)
                    if (lector["id"] is DBNull)
                    {
                        Console.WriteLine("Se ignoro una fila del REPO sin id");
                        continue;
                    }
                    juegos.Add(new JuegoRepo
                    {
                        Id = Texto(lector["id"]),
                        Nombre = Texto(lector["name"]),
                        Plataformas = (Texto(lector["platforms"]) ?? "").Split(',').Select(p => p.Trim()).Where(p => p != "").ToList(),
                        FechaLanzamiento = Texto(lector["release_date"]),
                        PrecioReferencia = lector["reference_price"] is DBNull ? (double?)null : Convert.ToDouble(lector["reference_price"]),
                        Imagen = Texto(lector["image_url"]),
                        SteamAppId = lector["steam_appid"] is DBNull ? 0 : Convert.ToInt32(lector["steam_appid"]),
                        EshopTitulo = Texto(lector["eshop_titulo"]),
                        MetacriticSlug = Texto(lector["metacritic_slug"]),
                        HltbId = lector["hltb_id"] is DBNull ? (int?)null : Convert.ToInt32(lector["hltb_id"])
                    });
                }
            }
            return juegos;
        }

        public static void CrearRepo()
        {
            string sql = "CREATE TABLE IF NOT EXISTS juegos (" +
                         "id TEXT PRIMARY KEY, name TEXT NOT NULL, platforms TEXT, release_date TEXT, " +
                         "reference_price REAL, image_url TEXT, steam_appid INTEGER, eshop_titulo TEXT, " +
                         "metacritic_slug TEXT, hltb_id INTEGER)";
            using (var conexion = AbrirRepo())
            using (var comando = new SQLiteCommand(sql, conexion))
                comando.ExecuteNonQuery();
        }

        public static void AgregarAlRepo(JuegoRepo juego)
        {
            string sql = "INSERT INTO juegos (id, name, platforms, release_date, reference_price, image_url, " +
                         "steam_appid, eshop_titulo, metacritic_slug, hltb_id) VALUES " +
                         "(@id, @name, @platforms, @fecha, @precio, @imagen, @appid, @eshop, @slug, @hltb)";
            using (var conexion = AbrirRepo())
            using (var comando = new SQLiteCommand(sql, conexion))
            {
                comando.Parameters.AddWithValue("@id", juego.Id);
                comando.Parameters.AddWithValue("@name", juego.Nombre);
                comando.Parameters.AddWithValue("@platforms", string.Join(",", juego.Plataformas));
                comando.Parameters.AddWithValue("@fecha", (object)juego.FechaLanzamiento ?? DBNull.Value);
                comando.Parameters.AddWithValue("@precio", (object)juego.PrecioReferencia ?? DBNull.Value);
                comando.Parameters.AddWithValue("@imagen", (object)juego.Imagen ?? DBNull.Value);
                comando.Parameters.AddWithValue("@appid", juego.SteamAppId);
                comando.Parameters.AddWithValue("@eshop", juego.EshopTitulo);
                comando.Parameters.AddWithValue("@slug", juego.MetacriticSlug);
                comando.Parameters.AddWithValue("@hltb", (object)juego.HltbId ?? DBNull.Value);
                comando.ExecuteNonQuery();
            }
        }

        static string Texto(object valor)
        {
            return valor is DBNull ? null : valor.ToString();
        }

        // Resultados de la corrida anterior, para conservar datos si una fuente falla
        public static Dictionary<string, Juego> LeerAnteriores()
        {
            var anteriores = new Dictionary<string, Juego>();
            if (!File.Exists(RutaSalida))
                return anteriores;

            try
            {
                var lista = JsonConvert.DeserializeObject<List<Juego>>(File.ReadAllText(RutaSalida, Encoding.UTF8));
                foreach (var juego in lista)
                    if (juego.Id != null)
                        anteriores[juego.Id] = juego;
            }
            catch (JsonException ex)
            {
                Console.WriteLine("No se pudo leer games.json anterior: " + ex.Message);
            }
            return anteriores;
        }

        public static void Guardar(List<JuegoRepo> repo, Juego[] nuevos, Dictionary<string, Juego> anteriores)
        {
            var porId = new Dictionary<string, Juego>(anteriores);
            foreach (var juego in nuevos)
                porId[juego.Id] = juego;

            // Se guarda en el orden del REPO; los que no se procesaron mantienen su dato anterior
            var salida = new List<Juego>();
            foreach (var juego in repo)
            {
                Juego resultado;
                if (porId.TryGetValue(juego.Id, out resultado))
                    salida.Add(resultado);
            }

            // Primero a un temporal para que la web nunca lea un archivo a medias
            string temporal = RutaSalida + ".tmp";
            File.WriteAllText(temporal, JsonConvert.SerializeObject(salida, Formatting.Indented), new UTF8Encoding(false));
            if (File.Exists(RutaSalida))
                File.Replace(temporal, RutaSalida, null);
            else
                File.Move(temporal, RutaSalida);
        }

        public static void RegistrarError(JuegoRepo juego, string fuente, string error, bool datoConservado)
        {
            lock (candadoErrores)
            {
                CantidadErrores++;
                string linea = string.Join(",",
                    DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                    Csv(juego.Id + " " + juego.Nombre),
                    fuente,
                    Csv(error),
                    datoConservado ? "si" : "no");
                try
                {
                    Directory.CreateDirectory(Path.GetDirectoryName(RutaErrores));
                    if (!File.Exists(RutaErrores))
                        File.AppendAllText(RutaErrores, "fecha,juego,fuente,error,dato_previo_conservado" + Environment.NewLine, Encoding.UTF8);
                    File.AppendAllText(RutaErrores, linea + Environment.NewLine, Encoding.UTF8);
                }
                catch (IOException)
                {
                    // Si el archivo esta abierto en otro programa (por ejemplo Excel) no se detiene el lote
                    Console.WriteLine("No se pudo escribir en errores.csv: " + linea);
                }
            }
        }

        static string Csv(string texto)
        {
            return "\"" + (texto ?? "").Replace("\"", "\"\"") + "\"";
        }
    }
}
