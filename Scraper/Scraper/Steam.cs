using System;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

namespace Scraper
{
    public static class Steam
    {
        public static async Task<Oferta> Consultar(JuegoRepo juego)
        {
            var oferta = new Oferta
            {
                Tienda = "Steam",
                Formato = "digital",
                Plataforma = "PC",
                Url = "https://store.steampowered.com/app/" + juego.SteamAppId
            };

            JToken datos = await Detalles(juego.SteamAppId);
            if (datos == null)
                throw new Exception("No se encontro el juego en Steam");

            // Steam da los precios en centavos de dolar (cc=us)
            JToken precio = datos["price_overview"];
            if (precio != null)
            {
                oferta.PrecioActual = (int)precio["final"] / 100.0;
                oferta.PrecioRegular = (int)precio["initial"] / 100.0;
            }
            else if ((bool?)datos["is_free"] == true)
            {
                oferta.PrecioActual = 0;
                oferta.PrecioRegular = 0;
            }
            return oferta;
        }

        // Datos del juego en Steam, o null si no existe
        public static async Task<JToken> Detalles(int appId)
        {
            string texto = await Http.Get("steam", "https://store.steampowered.com/api/appdetails?cc=us&l=en&appids=" + appId);
            if (texto == null)
                return null;

            JToken datos = JObject.Parse(texto)[appId.ToString()];
            if (datos == null || (bool?)datos["success"] != true)
                return null;
            return datos["data"];
        }

        // Solo devuelve el appid si el nombre coincide
        public static async Task<int?> BuscarAppId(string nombre)
        {
            string url = "https://store.steampowered.com/api/storesearch/?cc=us&l=en&term=" + System.Uri.EscapeDataString(nombre);
            string texto = await Http.Get("steam", url);
            if (texto == null)
                return null;

            foreach (JToken item in JObject.Parse(texto)["items"])
            {
                if ((string)item["type"] == "app" && Eshop.Normalizar((string)item["name"]) == Eshop.Normalizar(nombre))
                    return (int)item["id"];
            }
            return null;
        }
    }
}
