# LQS — sitio oficial

Sitio de **LQS**, agencia creativa modular. Estamos donde nos necesiten.

**En línea:** https://motta-bit.github.io/lqs/

Una sola página, sin dependencias ni build: se abre `index.html` y funciona.
Las únicas peticiones externas son las tipografías de Google Fonts.

---

## Las páginas

| Archivo | Qué es |
|---|---|
| `index.html` | Inicio — el hero, el problema y las tres rutas |
| `nosotros.html` | Quiénes somos, cómo trabajamos y los casos |
| `muestras.html` | La galería: 40 fichas filtrables por área y con buscador · antes/después · Express |
| `cotizador.html` | El picker de servicios con precio, los descuentos, el estimado, la asesoría y contacto |
| `legal.html` | Términos, tratamiento de datos y cookies |
| `404.html` | Página de error |
| `en/*.html` | Las mismas seis, en inglés |

Más `favicon.svg`, `og.jpg` y `fuente/` con las piezas.

### `fuente/`

Las páginas **no se editan a mano: se generan.** Editar un `.html` de la raíz y después
regenerar pierde el cambio.

| Archivo | Qué contiene |
|---|---|
| `cab.html` | Todo el CSS y los tokens del sistema |
| `partes/*.html` | Una sección por archivo, en español |
| `partes-en/*.html` | Las mismas secciones, en inglés — **toda copia se edita dos veces** |
| `guion.html` | La lógica: selección de áreas, cotizador, antes/después, envíos |
| `carita.js` | Las caritas de interfaz — 6 ojos × 6 bocas con gesticulación |
| `iconos.js` | Los siete íconos de área, cada uno con su movimiento |
| `build.py` | Compone las páginas en `fuente/dist/` |
| `publicar.py` | Genera las páginas finales en la raíz, con metadatos |

```bash
py fuente/publicar.py     # regenera las cuatro páginas
```

**Qué se toca dónde:** las áreas, sus precios y su lista de servicios están en `MODULOS`,
arriba de `build.py`.
El teléfono y el correo, en `CONTACTO`, ahí mismo. Qué secciones lleva cada página, en
`PAGINAS`. Nada de eso se busca dentro del HTML.

---

## Cómo fluye

`index` presenta y reparte · `nosotros` explica · `modulos` muestra y deja elegir ·
`cotizador` calcula y envía.

Cada área trae un desplegable con lo que se puede pedir adentro. Marcar un servicio
elige el área sola — nadie tiene que acordarse de hacer las dos cosas.

La selección **viaja entre páginas por la URL**: al elegir en `modulos.html` aparece una
barra que lleva a `cotizador.html?areas=Marca,Digital&det=marca.2.3,web.0`. El segundo
parámetro son los servicios: `slug` del área y los índices dentro de su lista `servicios`
en `build.py` — por eso **reordenar esa lista invalida los enlaces viejos**; agregar al
final, no. Ese enlace se copia y se manda por chat con todo adentro.

Los servicios **no tienen precio propio**: afinan el brief, no la cifra. La tarifa sigue
siendo la «desde» del área.

**Express va aparte y no pasa por el cotizador.** Encargos chicos que se piden y se
entregan: el botón abre WhatsApp directo. Se edita en `EXPRESS`, en `build.py`.

La pieza central es la pared del cotizador: cuando dos o más áreas entran al mismo
contenedor, dejan de ser servicios sueltos. Es lo que explica el modelo sin que nadie
lo cuente.

### Idioma

**El inglés vive en páginas reales bajo `en/`, no en un interruptor.** No se guarda nada en el
navegador: la política de cookies promete que el sitio no guarda nada, y un ajuste de idioma no
vale romperla. La pregunta flotante **solo aparece si el navegador no está en español** — quien ya
navega en español nunca la ve. El enlace `ES · EN` del menú está siempre.

Los textos de interfaz que viven en el JS están en `UI` (build.py), uno por idioma. Los nombres de
servicio y área, en `EN_SERV` y `EN_AREAS`.

**Las solicitudes no se guardan en ninguna parte.** Tanto el cotizador como el
formulario arman el mensaje y lo abren directo en WhatsApp o en el correo. No hay
bandeja intermedia que alguien tenga que revisar.

### Cómo cuenta el cotizador

1. Se suman los servicios elegidos, cada uno con su precio
2. Un solo descuento, el mayor de tres mecánicas que **no se acumulan**:
   escalera por número de áreas (2=8% … 7=35%) · planes armados (12–20%) · área completa (10%)

No hay multiplicador de plazo: el recargo por urgencia se habla con el cliente, no lo calcula el sitio.

**Redes va aparte, siempre.** Es mensual y los demás son por proyecto: no se
suman en un mismo total, y el descuento por conectar no toca la mensualidad.
Lo que Redes gana al conectarse es el arranque de $290.000 condonado cuando ya
hay módulo Marca.

---

## Lo que falta

- [ ] **Fotos del antes/después.** El mecanismo funciona (dedo, mouse y teclado), pero sin material no prueba nada — y es la sección que más vende
- [ ] **Casos 02 y 03.** Uno de módulo suelto, para mostrar que empezar chico también sirve
- [ ] **Política de datos y términos.** La casilla de Ley 1581 ya está; el documento al que apunta, no
- [ ] **Dominio propio y correo institucional.** Sigue apareciendo un Gmail en el pie
- [ ] **Redibujo del logo** y versión favicon simplificada — a 16 y 24px los bigotes se empastan
- [ ] **Llenar los cinco datos legales** (`LEGAL` en build.py): sin ellos la página legal sale marcada en rojo
- [ ] **Llenar la galería**: hoy las 40 fichas dicen «sin muestra todavía». Ver `lqs-material-visual.md`
- [ ] **Agente de voz.** Pedido pero no construido: no se ofrece hasta que exista uno andando

---

## Reglas que no se rompen

- **Nada que no sea verificable.** Ni premios, ni tamaño de equipo, ni cifras inventadas
- **Cuando usamos IA en una pieza, se declara**
- **Móvil primero.** Los referidos abren desde el celular
- **Una carita por pantalla**, y reacciona a un estado real
- **Nunca «próximamente».** Los módulos que no están activos se dicen *en apertura* y *a pedido*
- **Sin versión oscura.** Los pasteles con texto en tinta no sobreviven una inversión automática
- El sitio respeta `prefers-reduced-motion`: sin parpadeos, sin animación de entrada, sin seguimiento del cursor

---

Estamos donde nos necesiten.
