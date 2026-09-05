# Bot de control de Quini 6

Controla automáticamente 2 jugadas fijas contra el último sorteo del Quini 6
(Tradicional, La Segunda, Revancha, Siempre Sale y Pozo Extra) y avisa por
Telegram. Corre gratis en GitHub Actions los **lunes y jueves a las 9:00 (ART)**,
revisando el sorteo del domingo/miércoles anterior.

## 1. Crear el bot de Telegram

1. Hablale a **@BotFather** en Telegram.
2. Mandale `/newbot`, elegí un nombre y un username (debe terminar en "bot").
3. Te va a dar un **token** con este formato: `123456789:ABCdefGhIJKlmNoPQRstuVwxYZ`. Guardalo.

## 2. Obtener tu Chat ID

1. Mandale cualquier mensaje a tu bot recién creado (buscalo por el username que le pusiste).
2. Abrí en el navegador (reemplazando `<TOKEN>`):
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Buscá `"chat":{"id":` en la respuesta — ese número es tu `TELEGRAM_CHAT_ID`.

## 3. Subir el proyecto a GitHub

1. Creá un repositorio nuevo (puede ser privado) en GitHub.
2. Subí todos los archivos de esta carpeta a ese repositorio.

## 4. Configurar los Secrets

En el repositorio: **Settings → Secrets and variables → Actions → New repository secret**

- `TELEGRAM_BOT_TOKEN`: el token que te dio BotFather
- `TELEGRAM_CHAT_ID`: el chat ID que obtuviste en el paso 2

## 5. Probarlo

En la pestaña **Actions** del repo, elegí el workflow "Control Quini 6" y usá
**"Run workflow"** para probarlo manualmente antes de esperar al lunes/jueves.

## Modificar las jugadas

Las jugadas están hardcodeadas al principio de `quini6_bot.py`, en el
diccionario `JUGADAS`. Para cambiarlas o agregar una jugada nueva, editá esa
sección directamente.

## Nota importante sobre el scraping

El bot obtiene los resultados scrapeando la home de
`quini-6-resultados.com.ar`, buscando el bloque de "Último Sorteo" por medio
de expresiones regulares. Si en algún momento el sitio cambia su estructura
HTML, el regex podría dejar de encontrar los datos — en ese caso el bot manda
un mensaje de error por Telegram en vez de quedarse en silencio, así te
enterás de que hay que ajustar el parsing.
