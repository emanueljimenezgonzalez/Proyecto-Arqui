# Contrato de datos compartido

Todos los módulos deben usar estos nombres de campo. Si se necesita un cambio, coordinarlo entre los tres integrantes.

## Videojuego
```json
{
  "id": "game-001",
  "name": "Nombre del juego",
  "platforms": ["PC", "PS5"],
  "release_date": "2024-01-01",
  "reference_price": 59.99,
  "image_url": null,
  "metacritic_score": null,
  "hltb_main_hours": null,
  "offers": [],
  "updated_at": null
}
```

## Oferta de tienda
```json
{
  "store": "Nombre de tienda",
  "current_price": 39.99,
  "regular_price": 59.99,
  "format": "digital",
  "platform": "PC",
  "url": "https://example.com/producto"
}
```

## Reglas
- `id` debe identificar el juego de forma estable.
- Los precios deben tener una moneda definida por el equipo.
- No comparar precios de monedas diferentes sin conversión.
- Si una fuente no responde, conservar el dato previo válido cuando exista y registrar el fallo.
- `updated_at` indica cuándo se consultaron los datos.
- `discount_percent` y `best_price` se calculan a partir de las ofertas válidas, no se escriben manualmente en cada registro.
