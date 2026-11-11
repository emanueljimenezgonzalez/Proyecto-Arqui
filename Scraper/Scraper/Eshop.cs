using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Scraper
{
    public static class Eshop
    {
        // Es el buscador (Algolia) que usa la pagina de nintendo.com
        static readonly string AppId = Datos.Clave("ESHOP_APP_ID");
        static readonly string UrlBusqueda = "https://" + (AppId ?? "").ToLowerInvariant() + "-dsn.algolia.net/1/indexes/store_game_en_us/query";
        static readonly Dictionary<string, string> encabezados = new Dictionary<string, string>
        {
            { "X-Algolia-Application-Id", AppId },
            { "X-Algolia-API-Key", Datos.Clave("ESHOP_API_KEY") }
        };

        public static async Task<Oferta> Consultar(JuegoRepo juego)
        {
            var oferta = new Oferta { Tienda = "Nintendo eShop", Formato = "digital", Plataforma = "Switch" };

            JArray hits = await Buscar(new { query = juego.EshopTitulo, hitsPerPage = 10 });
            foreach (JToken hit in hits)
            {
                if ((string)hit["platform"] != "Nintendo Switch")
                    continue;
                if (Normalizar((string)hit["title"]) != Normalizar(juego.EshopTitulo))
                    continue;

                oferta.PrecioActual = (double?)hit["price"]?["finalPrice"];
                oferta.PrecioRegular = (double?)hit["price"]?["regPrice"];
                oferta.Url = "https://www.nintendo.com" + (string)hit["url"];
                return oferta;
            }
            // Si no aparece se cuenta como error, asi se conserva el precio anterior
            throw new Exception("No se encontro el juego en el eShop");
        }

        // Pagina del catalogo por popularidad, para generar el REPO
        // Se quitan los juegos de Nintendo porque no estan en Steam
        public static Task<JArray> Listar(int pagina)
        {
            string filtro = "platform:\"Nintendo Switch\" AND topLevelCategory:Games AND NOT softwarePublisher:Nintendo";
            return Buscar(new { query = "", hitsPerPage = 100, page = pagina, filters = filtro });
        }

        static async Task<JArray> Buscar(object cuerpo)
        {
            string texto = await Http.Post("eshop", UrlBusqueda, JsonConvert.SerializeObject(cuerpo), encabezados);
            // Un 404 aqui significa que el buscador cambio, no que falte un juego
            if (texto == null)
                throw new Exception("El buscador del eShop respondio 404");
            return (JArray)JObject.Parse(texto)["hits"];
        }

        // Quita simbolos como ™ y ® para comparar nombres
        public static string Normalizar(string titulo)
        {
            if (titulo == null)
                return "";
            string limpio = Regex.Replace(titulo.ToLowerInvariant(), "[^a-z0-9]+", " ");
            return limpio.Trim();
        }
    }
}
