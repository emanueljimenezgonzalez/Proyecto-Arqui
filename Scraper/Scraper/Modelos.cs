using System.Collections.Generic;
using Newtonsoft.Json;

namespace Scraper
{
    // Un juego del REPO (una fila de la tabla juegos en repo.db)
    public class JuegoRepo
    {
        public string Id { get; set; }
        public string Nombre { get; set; }
        public List<string> Plataformas { get; set; }
        public string FechaLanzamiento { get; set; }
        public double? PrecioReferencia { get; set; }
        public string Imagen { get; set; }
        public int SteamAppId { get; set; }
        public string EshopTitulo { get; set; }
        public string MetacriticSlug { get; set; }
        public int? HltbId { get; set; }
    }

    // Oferta de una tienda, con los campos del contrato de datos
    public class Oferta
    {
        [JsonProperty("store")] public string Tienda { get; set; }
        [JsonProperty("current_price")] public double? PrecioActual { get; set; }
        [JsonProperty("regular_price")] public double? PrecioRegular { get; set; }
        [JsonProperty("format")] public string Formato { get; set; }
        [JsonProperty("platform")] public string Plataforma { get; set; }
        [JsonProperty("url")] public string Url { get; set; }
        [JsonProperty("updated_at")] public string Actualizado { get; set; }
    }

    // Horas de HowLongToBeat: historia principal, historia + extras y 100%
    public class TiemposHltb
    {
        public double? Principal { get; set; }
        public double? Extras { get; set; }
        public double? Completo { get; set; }
    }

    // Registro final de un juego (games.json, lo lee la web)
    public class Juego
    {
        [JsonProperty("id")] public string Id { get; set; }
        [JsonProperty("name")] public string Nombre { get; set; }
        [JsonProperty("platforms")] public List<string> Plataformas { get; set; }
        [JsonProperty("release_date")] public string FechaLanzamiento { get; set; }
        [JsonProperty("reference_price")] public double? PrecioReferencia { get; set; }
        [JsonProperty("image_url")] public string Imagen { get; set; }
        [JsonProperty("metacritic_score")] public int? Metacritic { get; set; }
        [JsonProperty("metacritic_scores")] public Dictionary<string, int> MetacriticPorPlataforma { get; set; }
        [JsonProperty("hltb_main_hours")] public double? HorasHltb { get; set; }
        [JsonProperty("hltb_extra_hours")] public double? HorasHltbExtras { get; set; }
        [JsonProperty("hltb_completionist_hours")] public double? HorasHltbCompleto { get; set; }
        [JsonProperty("offers")] public List<Oferta> Ofertas { get; set; }
        [JsonProperty("updated_at")] public string Actualizado { get; set; }
    }

    // Resultado de consultar una fuente: Ok = false si falló
    public class Respuesta<T>
    {
        public bool Ok { get; set; }
        public T Valor { get; set; }
        public string Error { get; set; }
    }
}
