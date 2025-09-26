# MegaSource

## English — Project Briefing for Codex

### 1. Initial context
- The goal is to avoid adding 22 separate AltStore sources on the iPhone.
- MegaSource.json acts as a single "master" feed that merges all upstream apps.
- Everything lives in this repository so Codex can maintain and publish the feed easily.

### 2. First approach (and why it failed)
- We originally tried to expose a `sources` array with the 22 URLs.
- AltStore only understands the `apps` array, so the JSON was ignored.
- After reviewing the official "Make a Source" guide, we confirmed AltStore expects full app objects, not chained sources.

### 3. Key takeaway from the docs
A valid AltStore source must provide:
- Metadata (`name`, `subtitle`, `description`, `tintColor`, `iconURL`, etc.).
- An `apps` array with fully described apps (bundle identifier, developer name, versions, download URL, size, date, notes).
- Optionally a `news` array for announcements.
- Therefore, we have to merge every upstream feed into a single list of apps instead of linking to their URLs.

### 4. Final technical solution
The repository includes a builder that automates the merge:
1. `sources.txt` lists the 22 AltStore feeds (one URL per line).
2. `build.py` downloads each JSON, reads its `apps`, filters supported keys, and deduplicates apps by bundle identifier + version.
3. The script outputs a single `MegaSource.json` with curated metadata and the combined `apps` array.
4. A GitHub Actions workflow (`.github/workflows/build-megasource.yml`) runs the builder on every push or manual dispatch and commits the new JSON with `[skip ci]`.

### 5. Expected MegaSource.json format
```json
{
  "name": "MegaSource",
  "subtitle": "Todas tus fuentes en una sola",
  "description": "Repositorio agregador que combina 22 de las mejores fuentes de AltStore en un único JSON. Contiene emuladores, herramientas de jailbreak, juegos y utilidades.",
  "iconURL": "https://m264921.github.io/MegaSource/icon.png",
  "headerURL": "https://m264921.github.io/MegaSource/header.png",
  "website": "https://github.com/M264921/MegaSource",
  "tintColor": "#00AAFF",
  "featuredApps": [],
  "apps": [ /* merged apps */ ],
  "news": []
}
```
Update the metadata or artwork URLs when branding changes.

### 6. Repository layout
- `sources.txt` – master list of source URLs.
- `build.py` – merges the feeds into `MegaSource.json`.
- `MegaSource.json` – published output served via GitHub Pages.
- `icon.png` & `header.png` – artwork displayed in AltStore (upload custom assets).
- `.github/workflows/build-megasource.yml` – automation that keeps the feed updated.

### 7. Publishing through GitHub Pages
1. Confirm `MegaSource.json` exists in the repository root. For testing, drop in a provisional file such as:
   ```json
   {
     "name": "MegaSource",
     "subtitle": "Test",
     "description": "Provisional JSON for GitHub Pages",
     "apps": []
   }
   ```
2. In GitHub open **Settings → Pages**.
3. Choose **Branch: main** and **Folder: /** (root), then click **Save**.
4. Wait 1–2 minutes and visit `https://m264921.github.io/MegaSource/MegaSource.json`.
5. Once the JSON is visible, add the same URL inside AltStore (**Settings → Sources → Add Source**) to confirm the merged apps appear.

### 8. Workflow checklist for Codex
- Review `build.py` to ensure it normalises the app fields correctly.
- Provide final metadata (name, subtitle, description) before publishing.
- Upload `icon.png` and `header.png` so the source looks polished in AltStore.
- Verify the GitHub Actions run and commit the regenerated JSON.
- Inspect the published JSON in a browser to ensure `apps` is populated.
- Test the feed in AltStore; multiple upstream apps should appear.
- Optionally fill out `featuredApps` and `news` for highlights.

### 9. Troubleshooting & resilience
- If an upstream source is down, the builder skips it and still produces a JSON with the remaining feeds.
- Check the GitHub Actions logs when a build fails or when the JSON is missing data.
- Validate the generated JSON with a linter or by opening it in a browser before sharing the URL.

---

## Español — Briefing Técnico para Codex

### 1. Contexto inicial
- Queríamos evitar añadir 22 fuentes de AltStore una por una en el iPhone.
- MegaSource.json funciona como una "fuente maestra" con todas las apps fusionadas.
- Todo está en este repositorio para que Codex pueda mantener y publicar el feed sin complicaciones.

### 2. Primer intento (y por qué falló)
- Probamos con un `sources` que contenía las 22 URLs originales.
- AltStore solo procesa el array `apps`, así que ignoró el JSON.
- Tras revisar la guía oficial "Make a Source", confirmamos que AltStore exige objetos de apps completos, no cadenas de fuentes.

### 3. Aprendizaje clave de la documentación
Un source válido debe incluir:
- Metadatos (`name`, `subtitle`, `description`, `tintColor`, `iconURL`, etc.).
- Un array `apps` con las apps detalladas (bundleIdentifier, developerName, versions con downloadURL, tamaño, fecha, notas).
- Opcionalmente un array `news` para novedades.
- Por tanto, hay que fusionar todas las fuentes en un único listado de apps.

### 4. Solución técnica definitiva
El repositorio incorpora un generador automatizado:
1. `sources.txt` guarda las 22 fuentes (una URL por línea).
2. `build.py` descarga cada JSON, lee su `apps`, filtra las claves compatibles y elimina duplicados por bundleIdentifier + versión.
3. El script crea un único `MegaSource.json` con metadatos cuidados y todas las apps combinadas.
4. Un workflow de GitHub Actions (`.github/workflows/build-megasource.yml`) ejecuta el generador en cada push o ejecución manual y comitea el JSON con `[skip ci]`.

### 5. Formato esperado para MegaSource.json
```json
{
  "name": "MegaSource",
  "subtitle": "Todas tus fuentes en una sola",
  "description": "Repositorio agregador que combina 22 de las mejores fuentes de AltStore en un único JSON. Contiene emuladores, herramientas de jailbreak, juegos y utilidades.",
  "iconURL": "https://m264921.github.io/MegaSource/icon.png",
  "headerURL": "https://m264921.github.io/MegaSource/header.png",
  "website": "https://github.com/M264921/MegaSource",
  "tintColor": "#00AAFF",
  "featuredApps": [],
  "apps": [ /* apps fusionadas */ ],
  "news": []
}
```
Actualiza los metadatos o el arte cuando cambie el branding.

### 6. Estructura del repositorio
- `sources.txt` – lista maestra de URLs.
- `build.py` – fusiona las fuentes en `MegaSource.json`.
- `MegaSource.json` – salida publicada mediante GitHub Pages.
- `icon.png` y `header.png` – recursos gráficos para AltStore (sube tus propios archivos).
- `.github/workflows/build-megasource.yml` – automatización que mantiene el feed al día.

### 7. Publicación con GitHub Pages
1. Comprueba que `MegaSource.json` exista en la raíz. Para pruebas puedes usar un archivo provisional como:
   ```json
   {
     "name": "MegaSource",
     "subtitle": "Test",
     "description": "JSON provisional para GitHub Pages",
     "apps": []
   }
   ```
2. En GitHub entra a **Settings → Pages**.
3. Selecciona **Branch: main** y **Folder: /** (root) y pulsa **Save**.
4. Espera 1–2 minutos y visita `https://m264921.github.io/MegaSource/MegaSource.json`.
5. Si ves el contenido, añade la misma URL en AltStore (**Settings → Sources → Add Source**) para confirmar que aparecen las apps fusionadas.

### 8. Checklist de tareas para Codex
- Revisa que `build.py` normalice correctamente los campos de cada app.
- Ajusta los metadatos (nombre, subtítulo, descripción) antes de publicar.
- Sube `icon.png` y `header.png` para que la fuente luzca profesional en AltStore.
- Comprueba que el workflow de GitHub Actions ejecuta y comitea el JSON regenerado.
- Abre el JSON publicado en el navegador para confirmar que `apps` no está vacío.
- Prueba la fuente en AltStore; deberían mostrarse apps de varias fuentes.
- Opcionalmente completa `featuredApps` y `news` con destacados.

### 9. Resolución de problemas y robustez
- Si una fuente falla temporalmente, el script la omite y continúa con las demás.
- Revisa los registros del workflow cuando falle un build o falten apps.
- Valida el JSON con un linter o en el navegador antes de compartir la URL.

---

Con este briefing Codex tiene toda la información para terminar de pulir MegaSource y publicarlo como una fuente única en AltStore.
