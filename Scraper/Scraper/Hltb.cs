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
        // Devuelve los tres tiempos del juego, o null si no tiene pagina en HowLongToBeat
        public static async Task<TiemposHltb> Consultar(JuegoRepo juego)
        {
            if (juego.HltbId == null)
                return null;

            string html = await Http.Get("hltb", "https://howlongtobeat.com/game/" + juego.HltbId);
            if (html == null)
                return null;

            Match m = Regex.Match(html, "<script id=\"__NEXT_DATA__\"[^>]*>(.*?)</script>", RegexOptions.Singleline);
            if (!m.Success)
                throw new Exception("No se encontro __NEXT_DATA__ en la pagina");

            JObject datos = JObject.Parse(m.Groups[1].Value);
            return new TiemposHltb
            {
                Principal = Horas(datos, "comp_main"),
                Extras = Horas(datos, "comp_plus"),
                Completo = Horas(datos, "comp_100")
            };
        }

        // Los tiempos vienen en segundos; 0 significa que no hay dato
        static double? Horas(JObject datos, string campo)
        {
            JToken valor = datos.SelectTokens("$.." + campo).FirstOrDefault();
            if (valor == null || (valor.Type != JTokenType.Integer && valor.Type != JTokenType.Float) || (double)valor == 0)
                return null;
            return Math.Round((double)valor / 3600.0, 1);
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
