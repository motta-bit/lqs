# Muestras · cuatro páginas de una pantalla

Cuatro sitios de muestra, cada uno de **un solo archivo HTML**. Sirven para
enseñar hasta dónde llega una página sin librerías ni build.

| Archivo | Qué es | Mecánica |
|---|---|---|
| `tienda-ropa.html` | **Atelier Norte** · marroquinería | Mosaico que se arma con muelle; la pieza aparece donde pone el cursor |
| `restaurante.html` | **Rescoldo** · cocina de brasa | La carta es una rueda que gira con el scroll; el fuego del fondo cambia de temperatura con cada plato |
| `revista-moda.html` | **Tendido** · moda e ilustración | Tendido que se arma solo, campos de degradé que respiran, seis ilustraciones con su halo |
| `mezcal.html` | **Casa Tepemete** · mezcal de olla | Degradé de horno y rosetas de agave dibujadas al azar: cada visita ve una planta distinta |
| `index.html` | Índice de las cuatro | — |

## Cómo se monta

Se copia la carpeta entera y se abre. No hay build, ni npm, ni dependencias.

    demos/
      index.html
      tienda-ropa.html  restaurante.html  revista-moda.html  mezcal.html
      img/
        bolsos/  mesa/  agave/  moda/

**La carpeta `img/` tiene que viajar con los HTML.** Las rutas son relativas
(`img/mesa/carbon.webp`), así que la estructura se respeta tal cual y funciona
en cualquier subcarpeta del sitio, sin tocar nada.

Lo único que sale a la red son las tipografías de Google Fonts. Si algún día
hay que cortar esa dependencia, se descargan los `.woff2` a `img/../fuentes/`
y se cambia el `<link>` por un `@font-face`; la página no se rompe mientras
tanto porque cada una declara su familia de respaldo.

## Lo que hay que saber antes de tocarlas

- **El estado por defecto es el legible.** Sin JavaScript las cuatro se leen
  enteras: la carta de Rescoldo sale apilada, el mosaico de Atelier sale
  colocado. El movimiento lo monta el script añadiendo `html.js`. Si se
  invierte eso, un fallo de script deja la página en blanco.
- **`prefers-reduced-motion` está atendido en las cuatro.** Se apaga el
  movimiento; el color y el contenido se quedan. No es lo mismo apagar el
  movimiento que castigar a quien lo pidió.
- **Rescoldo se desmonta solo** cuando la ventana es tan corta que no queda
  banda para un plato legible (un 320×568): ahí vuelve la carta apilada. Es
  deliberado, no un fallo.
- **Los avisos de Picante y Vegano son afirmaciones sobre la comida.** Si se
  cambian los ingredientes de un plato, hay que revisar su aviso. La berenjena
  es vegana porque ningún ingrediente suyo es de origen animal; si entra yogur
  o mantequilla, el aviso sale.

## Fotografía

Las 55 imágenes son de muestra, optimizadas a WebP con el lado largo en
1300px. Hay unas 19 sin usar en `img/`, listas por si se quiere cambiar
alguna: platos (`ostras`, `caviar`, `mesa-cenital`…), mezcal (`botellas`,
`brindis`, `pencas`, `pintura`), `bolsos/nacar`, `bolsos/tienda` y
`moda/brocado`.

Antes de publicarlas fuera de una muestra hay que confirmar los derechos de
cada una.
