# Contrato de datos entre integrantes

Cada juego usa estas claves:
- `id`: identificador estable
- `name`: nombre
- `platforms`: lista de plataformas
- `release_date`: fecha de lanzamiento
- `reference_price`: precio de referencia
- `image_url`: imagen
- `metacritic_score`: puntuación
- `hltb_main_hours`: tiempo principal de juego en horas
- `offers`: lista de ofertas de tiendas
- `updated_at`: fecha/hora de actualización

Cada oferta usa:
- `store`
- `current_price`
- `regular_price`
- `format`
- `platform`
- `url`

Los precios deben tener una moneda definida por el equipo y mostrarse de forma consistente. No mezclen monedas al escoger el mejor precio sin convertirlas.
