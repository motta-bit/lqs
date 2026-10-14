# Muestras

Cinco muestras, cada una de **un solo archivo HTML**. Sirven para enseñar hasta
dónde llega una página sin librerías ni build.

| Archivo | Qué es | Mecánica |
|---|---|---|
| `tienda-ropa.html` | **Atelier Norte** · marroquinería | Mosaico que se arma con muelle; la pieza aparece donde pone el cursor |
| `restaurante.html` | **Rescoldo** · cocina de brasa | La carta es una rueda que gira con el scroll; el fuego del fondo cambia de temperatura con cada plato |
| `revista-moda.html` | **Tendido** · moda e ilustración | Tendido que se arma solo, campos de degradé que respiran, seis ilustraciones con su halo |
| `mezcal.html` | **Casa Tepemete** · mezcal de olla | Degradé de horno y rosetas de agave dibujadas al azar: cada visita ve una planta distinta |
| `automatizacion.html` | **Turno** · contenido y bots | La parrilla de publicaciones, los dos bots y el reporte de cierre. Los bots son una máquina de estados: lo que se toca decide la conversación |
| `index.html` | Índice de las cinco | — |

## Cómo se monta

Se copia la carpeta entera y se abre. No hay build, ni npm, ni dependencias.

    demos/
      index.html
      tienda-ropa.html  restaurante.html  revista-moda.html  mezcal.html
      automatizacion.html
      img/
        bolsos/  mesa/  agave/  moda/

**La carpeta `img/` tiene que viajar con los HTML.** Las rutas son relativas
(`img/mesa/carbon.webp`), así que la estructura se respeta tal cual y funciona
en cualquier subcarpeta del sitio, sin tocar nada.

Lo único que sale a la red son las tipografías de Google Fonts, y solo en las
cuatro páginas de marca: `automatizacion.html` usa la letra del sistema y no
pide nada. Si algún día hay que cortar esa dependencia en las otras, se
descargan los `.woff2` a una carpeta `fuentes/` y se cambia el `<link>` por un
`@font-face`; mientras tanto no se rompe nada, porque cada una declara su
familia de respaldo.

## Lo que hay que saber antes de tocarlas

- **El estado por defecto es el legible.** Sin JavaScript las cinco se leen
  enteras: la carta de Rescoldo sale apilada, el mosaico de Atelier sale
  colocado. El movimiento lo monta el script añadiendo `html.js`. Si se
  invierte eso, un fallo de script deja la página en blanco.
- **`prefers-reduced-motion` está atendido en las cinco.** Se apaga el
  movimiento; el color y el contenido se quedan. No es lo mismo apagar el
  movimiento que castigar a quien lo pidió.
- **Rescoldo se desmonta solo** cuando la ventana es tan corta que no queda
  banda para un plato legible (un 320×568): ahí vuelve la carta apilada. Es
  deliberado, no un fallo.
- **Los avisos de Picante y Vegano son afirmaciones sobre la comida.** Si se
  cambian los ingredientes de un plato, hay que revisar su aviso. La berenjena
  es vegana porque ningún ingrediente suyo es de origen animal; si entra yogur
  o mantequilla, el aviso sale. Aparecen en dos sitios: la carta del
  restaurante y la que manda el bot.
- **Las cifras del reporte cuadran entre sí** y conviene que sigan cuadrando:
  143 resueltos por el bot más 41 derivados son los 184 mensajes, y el 78 / 22
  por ciento de la barra sale de ahí. Si se cambia una, se cambian todas.
- **Las plataformas se nombran, no se imitan.** Los glifos de WhatsApp e
  Instagram son geométricos propios; no son sus logos. Si esto se publica con
  la marca de un cliente, conviene dejarlo así.

## Fotografía

Las 55 imágenes están optimizadas a WebP con el lado largo en 1300px. Quedan 12
sin usar en `img/`, listas por si se quiere cambiar alguna: `bolsos/nacar`,
`bolsos/tienda`, `mesa/foco-oscuro`, `mesa/mesa-cenital`, `moda/brocado` y
siete de mezcal (`barra`, `botellas`, `brindis`, `cristal`, `pencas`,
`pintura`, `planta`).

**Son material de referencia, no activos del proyecto.** Se recopilaron en
Cosmos, que es un tablero de curaduría: ahí la gente guarda imágenes de toda
la web, así que no es la fuente ni el titular de los derechos de ninguna. La
autoría sigue siendo de cada fotógrafo, ilustrador o marca, y Cosmos no otorga
ninguna licencia sobre lo que se guarda en él.

Dos cosas concretas antes de que esto salga de una demostración:

- **Los bolsos son productos de una marca identificable** —formas registradas
  de una casa real—. Presentarlos como catálogo de «Atelier Norte», con
  nombres y precios propios, es lo más delicado del paquete: no es solo
  derecho de autor sobre la foto, es la forma del producto y la marca. Esas
  diez van sustituidas sí o sí antes de cualquier publicación.
- **Las seis ilustraciones son obra de autor individual.** Si alguna se
  quisiera conservar, hay que localizar a quien la hizo y pedir permiso; no
  basta con acreditar.

El resto —platos, mezcal, editorial de moda— también es de terceros, pero son
fotografías sin marca identificable, así que sustituirlas es solo cuestión de
conseguir sesión propia.
