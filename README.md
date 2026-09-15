# LQS — sitio oficial

Sitio de **LQS**, agencia creativa modular con base en Medellín, para LatAm.

**En línea:** https://motta-bit.github.io/lqs/

Una sola página, sin dependencias ni build: se abre `index.html` y funciona.
Las únicas peticiones externas son las tipografías de Google Fonts.

---

## Qué hay acá

| Archivo | Qué es |
|---|---|
| `index.html` | El sitio completo — 95 KB, todo adentro |
| `favicon.svg` | El gato, vectorizado del dibujo original |
| `og.jpg` | Imagen para cuando alguien comparte el enlace |
| `fuente/` | Las piezas con las que se genera `index.html` |

### `fuente/`

`index.html` no se edita a mano: **se genera**. Editar el archivo grande y después
regenerarlo pierde el cambio.

| Archivo | Qué contiene |
|---|---|
| `cab.html` | Todo el CSS y los tokens del sistema |
| `cuerpo.html` | El marcado de las doce secciones |
| `pie.html` | La lógica: selección de módulos, cotizador, antes/después |
| `carita.js` | Las caritas de interfaz — 6 ojos × 6 bocas con gesticulación |
| `iconos.js` | Los siete íconos de módulo, cada uno con su movimiento |
| `build.py` | Arma la versión de trabajo |
| `publicar.py` | Arma `index.html` — quita la nota interna y añade metadatos |

```bash
cd fuente
python3 build.py       # genera lqs.html para revisar
python3 publicar.py    # genera ../index.html
```

Los siete módulos y sus precios viven en una lista de Python arriba de `build.py`.
Para cambiar una tarifa se toca ahí, no en el HTML.

---

## Las secciones

`00` Cabecera · `01` Hero · `02` El problema · `03` Los siete módulos ·
`04` Armá tu ecosistema · `05` Antes/después · `06` Casos · `07` Cómo trabajamos ·
`08` Tarifas · `09` Cotizador · `10` Contacto · `11` Pie

La pieza central es **04**: el visitante toca módulos y los bloques entran a una
pared compartida. Es lo que explica el modelo sin que nadie lo cuente.

### Cómo cuenta el cotizador

1. Tarifas base de los módulos elegidos
2. Descuento por conectar — el mayor que aplique, y **muestra su nombre**
3. Multiplicador de plazo: 5 días ×1.50 · 10 ×1.25 · 15 ×1.00 · 30 ×0.95

**Redes va aparte, siempre.** Es mensual y los demás son por proyecto: no se
suman en un mismo total, y el descuento por conectar no toca la mensualidad.
Lo que Redes gana al conectarse es el arranque de $290.000 condonado cuando ya
hay módulo Marca.

---

## Lo que falta

- [ ] **Fotos del antes/después.** El mecanismo funciona (dedo, mouse y teclado), pero sin material no prueba nada — y es la sección que más vende
- [ ] **Casos 02 y 03.** Uno de módulo suelto, para mostrar que empezar chico también sirve
- [ ] **Política de datos y términos.** La casilla de Ley 1581 ya está; el documento al que apunta, no
- [ ] **Backend del formulario.** Hoy el canal real es WhatsApp
- [ ] **Dominio propio y correo institucional.** Sigue apareciendo un Gmail en el pie
- [ ] **Redibujo del logo** y versión favicon simplificada — a 16 y 24px los bigotes se empastan
- [ ] **Revisar el descuento «Ultra completo» (20%).** Pide ≥$8.000.000 y cinco módulos a tarifa «desde» suman $1.550.000: hoy es un tramo que nunca se dispara

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

Medellín, Colombia.
