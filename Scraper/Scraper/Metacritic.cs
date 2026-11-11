using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

namespace Scraper
{
    public static class Metacritic
    {
        // Devuelve el score de cada plataforma del REPO (PC y Switch), o null si no hay pagina
        public static async Task<Dictionary<string, int>> Consultar(JuegoRepo juego)
        {
            string html = await Http.Get("metacritic", "https://www.metacritic.com/game/" + juego.MetacriticSlug + "/");
            if (html == null)
                return null;

            Match m = Regex.Match(html, "<script[^>]*id=\"__NUXT_DATA__\"[^>]*>(.*?)</script>", RegexOptions.Singleline);
            if (!m.Success)
                throw new Exception("No se encontro __NUXT_DATA__ en la pagina");

            // Los datos vienen en un arreglo donde los objetos apuntan a otras posiciones
            JArray datos = JArray.Parse(m.Groups[1].Value);
            foreach (JToken elemento in datos)
            {
                JObject item = elemento as JObject;
                if (item == null || item["title"] == null || item["platforms"] == null || item["criticScoreSummary"] == null)
                    continue;

                JArray plataformas = Buscar(datos, item["platforms"]) as JArray;
                if (plataformas == null)
                    return null;

                var scores = new Dictionary<string, int>();
                foreach (JToken referencia in plataformas)
                {
                    JObject plataforma = Buscar(datos, referencia) as JObject;
                    if (plataforma == null)
                        continue;
                    string nombre = (string)Buscar(datos, plataforma["name"]);
                    string clave = nombre == "Nintendo Switch" ? "Switch" : nombre;
                    if (!juego.Plataformas.Contains(clave))
                        continue;

                    JObject resumen = Buscar(datos, plataforma["criticScoreSummary"]) as JObject;
                    JToken score = resumen == null ? null : Buscar(datos, resumen["score"]);
                    if (score == null || score.Type != JTokenType.Integer)
                        continue;
                    scores[clave] = (int)score;
                }
                return scores;
            }
            throw new Exception("No se encontraron los datos del juego en la pagina");
        }

        static JToken Buscar(JArray datos, JToken referencia)
        {
            if (referencia == null || referencia.Type != JTokenType.Integer)
                return null;
            int i = (int)referencia;
            if (i < 0 || i >= datos.Count)
                return null;
            return datos[i];
        }
    }
}
