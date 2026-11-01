# Git y colaboración

## Primera configuración
Una persona crea el repositorio remoto y los demás lo clonan.

```bash
git clone URL_DEL_REPOSITORIO
cd Proyecto_Web_Scraping_Multinucleo
git checkout -b feature/nombre-del-modulo
```

## Antes de empezar a trabajar
```bash
git pull origin main
git checkout -b feature/mi-tarea
```

## Guardar cambios
```bash
git add .
git commit -m "Describe el cambio"
git push -u origin feature/mi-tarea
```

Después, crear un Pull Request hacia `main` y pedir que otro integrante revise los cambios.

## Ramas sugeridas
- `feature/scraping-repo`
- `feature/web-interfaz`
- `feature/benchmark-documentacion`

## Evitar conflictos
- Integrante 1 modifica principalmente `app/repo/`, `app/scrapers/` y `app/services/scraping_service.py`.
- Integrante 2 modifica principalmente `app/main.py`, `app/templates/` y `app/static/`.
- Integrante 3 modifica principalmente `app/benchmark.py` y `docs/`.
- Los cambios en `app/models.py`, `requirements.txt` y el contrato de datos deben acordarse entre los tres.
