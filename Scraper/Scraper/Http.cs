using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Scraper
{
    public static class Http
    {
        const int Intentos = 3;
        const int PausaMs = 300;

        static readonly HttpClient cliente = CrearCliente();

        // Limite de solicitudes al mismo tiempo por sitio
        static readonly Dictionary<string, SemaphoreSlim> limites = new Dictionary<string, SemaphoreSlim>
        {
            { "steam", new SemaphoreSlim(4) },
            { "eshop", new SemaphoreSlim(4) },
            { "metacritic", new SemaphoreSlim(2) },
            { "hltb", new SemaphoreSlim(2) }
        };

        static HttpClient CrearCliente()
        {
            // .NET Framework solo abre 2 conexiones por host si no se cambia
            ServicePointManager.DefaultConnectionLimit = 100;

            var manejador = new HttpClientHandler();
            manejador.AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate;

            var c = new HttpClient(manejador);
            c.Timeout = TimeSpan.FromSeconds(20);
            c.DefaultRequestHeaders.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36");
            c.DefaultRequestHeaders.Add("Accept-Language", "en-US,en;q=0.9");
            return c;
        }

        public static Task<string> Get(string sitio, string url, Dictionary<string, string> encabezados = null)
        {
            return Pedir(sitio, () =>
            {
                var mensaje = new HttpRequestMessage(HttpMethod.Get, url);
                if (encabezados != null)
                    foreach (var e in encabezados)
                        mensaje.Headers.Add(e.Key, e.Value);
                return mensaje;
            });
        }

        public static Task<string> Post(string sitio, string url, string json, Dictionary<string, string> encabezados)
        {
            return Pedir(sitio, () =>
            {
                var mensaje = new HttpRequestMessage(HttpMethod.Post, url);
                mensaje.Content = new StringContent(json, Encoding.UTF8, "application/json");
                foreach (var e in encabezados)
                    mensaje.Headers.Add(e.Key, e.Value);
                return mensaje;
            });
        }

        // Devuelve el texto de la respuesta, o null si la pagina no existe (404).
        // Si falla despues de los intentos lanza una excepcion.
        static async Task<string> Pedir(string sitio, Func<HttpRequestMessage> crearMensaje)
        {
            SemaphoreSlim limite = limites[sitio];
            for (int intento = 1; ; intento++)
            {
                int esperaMs = 1000 * (int)Math.Pow(2, intento - 1);
                string error;

                await limite.WaitAsync();
                try
                {
                    using (var respuesta = await cliente.SendAsync(crearMensaje()))
                    {
                        if (respuesta.IsSuccessStatusCode)
                            return await respuesta.Content.ReadAsStringAsync();
                        if (respuesta.StatusCode == HttpStatusCode.NotFound)
                            return null;

                        error = "HTTP " + (int)respuesta.StatusCode;
                        if ((int)respuesta.StatusCode == 429 && respuesta.Headers.RetryAfter != null && respuesta.Headers.RetryAfter.Delta.HasValue)
                            esperaMs = (int)respuesta.Headers.RetryAfter.Delta.Value.TotalMilliseconds;
                    }
                }
                catch (HttpRequestException ex)
                {
                    error = ex.Message;
                }
                catch (TaskCanceledException)
                {
                    error = "Tiempo de espera agotado";
                }
                finally
                {
                    await Task.Delay(PausaMs);
                    limite.Release();
                }

                if (intento >= Intentos)
                    throw new Exception(error + " (" + Intentos + " intentos)");
                await Task.Delay(esperaMs);
            }
        }
    }
}
