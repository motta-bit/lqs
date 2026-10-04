# LQS — sitio

Sitio de **LQS (Lo Que Sea)**, agencia creativa modular en Medellín.
Estático, sin framework, sin dependencias en el navegador.

- **Repo:** `https://github.com/motta-bit/lqs.git` · rama `main`
- **En línea:** https://motta-bit.github.io/lqs/ (GitHub Pages desde la raíz)
- **Idiomas:** español en la raíz, inglés en `en/`
- **Python:** 3.10 en la máquina de Motta

---

## Lo único que hay que saber para no romper nada

**Las páginas de la raíz son GENERADAS. No se editan a mano.**

`index.html`, `nosotros.html`, `muestras.html`, `cotizador.html`, `legal.html`,
`404.html` y sus gemelas en `en/` salen de `fuente/`. Cualquier edición directa
se pierde en la siguiente publicación, sin aviso.

```
python3 fuente/publicar.py
```

Eso corre `fuente/build.py`, arma todo en `fuente/dist/` (ignorado por git) y
escribe las páginas finales **en la raíz del repo**, más `favicon.svg`,
`.nojekyll` y `lqs-trazo.js`.

### De dónde sale cada cosa

| Qué | Dónde se edita |
|---|---|
| Todo el CSS, el `<head>`, los `@font-face` | `fuente/cab.html` |
| Secciones en español | `fuente/partes/*.html` |
| Secciones en inglés | `fuente/partes-en/*.html` |
| Datos: módulos, precios, planes, encabezados, textos legales | `fuente/build.py` (arriba del archivo) |
| Metadatos, canónicas, OG, hreflang | `fuente/publicar.py` |
| Imágenes de preview (OG) | `fuente/og.py` — se corre aparte |

### Marcadores dentro de `partes/`

- `{{RAIZ}}` → `""` en español, `"../"` en inglés. **Todo enlace a un asset de
  la raíz lo necesita**, o la versión en inglés apunta a `en/marca/...` y falla.
- `{{OTRO}}` → la misma página en el otro idioma.

---

## Trampas reales, encontradas a los golpes

Están comentadas en el código donde corresponde. Resumen:

1. **`publicar.py` publica en `BASE.parent`**, o sea la raíz del repo. Antes
   decía `BASE.parent/"repo"`, de cuando `fuente/` vivía al lado del checkout y
   no dentro. Con la carpeta renombrada a `LQS-sitio` eso creaba un
   `LQS-sitio/repo/` nuevo en cada publicación y las páginas de verdad no se
   actualizaban nunca. Si algo "no se ve reflejado", mirar esto primero.

2. **`favicon.svg` se copia de `marca/favicon.svg`.** Antes se regeneraba desde
   `fuente/carita-inline.svg`, que es el monograma suelto —viewBox 1222×1238,
   ni cuadrado ni con fondo—. Como el nombre del archivo no cambia, cada
   publicación pisaba el icono diseñado y solo se notaba al abrir una pestaña.

3. **`fuente/carita-inline.svg` conserva el nombre viejo pero contiene el
   MONOGRAMA**, no la carita/gato original. La marca cambió y el archivo no se
   renombró. No asumir por el nombre.

4. **`<lqs-trazo>` se pinta entero por JavaScript** y reemplaza su propio
   `innerHTML`. El `<img>` que lleva dentro es el respaldo: si el script no
   llega, el elemento se quedaba en 0 px de alto y el hero y la barra salían
   SIN LOGO. Si se toca ese componente, verificar los tres casos: normal, con
   el script bloqueado y con JS desactivado.

5. **`legal.html` sale con 5 campos sin llenar** y `publicar.py` lo grita al
   final. Son datos que la ley colombiana exige. **No enlazar `legal.html` en
   una propuesta** hasta llenarlos en `LEGAL`, arriba de `build.py`.

6. **Git sobre la carpeta montada deja candados tirados.** Si aparece
   `Unable to create '.git/index.lock': File exists`, es eso: no un proceso de
   git corriendo. El repo ya tiene `core.fileMode false` para que los cambios
   de permisos del montaje no ensucien el diff.

---

## Tipografía

Dos familias en titulares, una de ellas propia:

- **LQS Display** (`tipos/LQS-Display.woff2`, 42 KB, servida desde el sitio).
  Derivada de Syne bajo SIL OFL, con el corte orgánico de la marca. Va en los
  H1, con Syne de respaldo. Es de **display**: por debajo de ~34 px los cortes
  se empastan. Se genera en el taller, no aquí (ver abajo).
- **Syne, Rubik, IBM Plex Mono, Newsreader** siguen viniendo de Google Fonts.
  Falta autoalojarlas.

El wordmark del hero va en minúscula con `text-transform`, **no escribiendo
«lqs» en el HTML**: el texto sigue siendo `LQS` para Google, para quien lo
copie y para un lector de pantalla.

---

## Cómo se escribe aquí

- **Comentarios en español, y explican POR QUÉ**, normalmente nombrando el
  fallo que obligó a escribir esa línea. Un comentario que repite lo que el
  código ya dice sobra.
- **Mensajes de commit en español**, con un asunto en forma de frase —sin
  prefijos tipo `feat:`— y un cuerpo que explica el razonamiento y lo que se
  midió. Mirar `git log` para el tono.
- Los colores y radios viven como tokens en `:root`, en `cab.html`.
- Antes de dar algo por bueno: medir. Las 6 páginas × 2 idiomas × 3 anchos
  (1440 / 768 / 390) con Playwright, mirando desborde horizontal y errores de
  consola. Es barato y ha pillado cosas varias veces.
