using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Scraper
{
    public static class Hltb
    {
        // Devuelve las horas de la historia principal, o null si no hay dato
        public static async Task<double?> Consultar(JuegoRepo juego)
        {
            if (juego.HltbId == null)
                return null;

            string html = await Http.Get("hltb", "https://howlongtobeat.com/game/" + juego.HltbId);
            if (html == null)
                return null;

            Match m = Regex.Match(html, "<script id=\"__NEXT_DATA__\"[^>]*>(.*?)</script>", RegexOptions.Singleline);
            if (!m.Success)
                throw new Exception("No se encontro __NEXT_DATA__ en la pagina");

            // comp_main viene en segundos
            JToken compMain = JObject.Parse(m.Groups[1].Value).SelectTokens("$..comp_main").FirstOrDefault();
            if (compMain == null || compMain.Type != JTokenType.Integer || (int)compMain == 0)
                return null;
            return Math.Round((int)compMain / 3600.0, 1);
        }

        // Solo se usa al generar el REPO
        public static async Task<int?> BuscarId(string nombre)
        {
            var encabezados = new Dictionary<string, string>
            {
                { "Referer", "https://howlongtobeat.com/" },
                { "Origin", "https://howlongtobeat.com" }
            };

            // La pagina pide primero un token para poder buscar
            string inicio = await Http.Get("hltb", "https://howlongtobeat.com/api/search/site/init?t=" + DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(), encabezados);
            if (inicio == null)
                return null;
            encabezados["x-auth-token"] = (string)JObject.Parse(inicio)["token"];

            var filtroVacio = new { mode = "include", values = new string[0] };
            var cuerpo = new
            {
                searchType = "games",
                searchTerms = Eshop.Normalizar(nombre).Split(' '),
                searchPage = 1,
                size = 20,
                searchOptions = new
                {
                    games = new
                    {
                        userId = 0,
                        platform = "",
                        sortCategory = "popular",
                        rangeCategory = "main",
                        rangeTime = new { min = (int?)null, max = (int?)null },
                        gameplay = new { perspective = filtroVacio, flow = filtroVacio, genre = filtroVacio },
                        year = "",
                        modifier = ""
                    },
                    users = new { sortCategory = "postcount" },
                    lists = new { sortCategory = "follows" },
                    filter = "",
                    sort = 0,
                    randomizer = 0
                },
                useCache = true
            };

            string texto = await Http.Post("hltb", "https://howlongtobeat.com/api/search/site", JsonConvert.SerializeObject(cuerpo), encabezados);
            if (texto == null)
                return null;

            foreach (JToken juego in JObject.Parse(texto)["data"])
            {
                if (Eshop.Normalizar((string)juego["game_name"]) == Eshop.Normalizar(nombre))
                    return (int)juego["game_id"];
            }
            return null;
        }
    }
}
