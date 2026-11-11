import pathlib, json, re
from urllib.parse import quote

BASE = pathlib.Path(__file__).parent
P = BASE / "partes"

# --------------------------------------------------------------- datos
# nombre, clave de ícono, superficie pastel, descripción, precio visible, precio, mensual, servicios
def S(nombre, precio=0, mensual=False, unidad="", fuente="propuesto", grupo=""):
    """Un servicio del catálogo.
       fuente='tarifario' = la cifra ya estaba en lqs-comercial.md.
       fuente='propuesto' = la propuse yo y falta que Motta la confirme.
       grupo  = servicios que son alternativas entre sí: marcar uno desmarca los otros,
                y «el área completa» toma solo el más amplio del grupo."""
    return {"n": nombre, "p": precio, "m": mensual, "u": unidad, "f": fuente, "g": grupo}

# nombre, clave de ícono, superficie pastel, descripción corta, servicios
MODULOS = [
 ("Video", "video", "#F2975A", "Reels, video de marca, comerciales", [
   S("Reels y contenido vertical",        150000, unidad="por pieza"),
   S("Video de marca o empresa",          900000),
   S("Comercial para pauta",              600000),
   S("Entrevista o podcast",              450000),
 ]),
 ("Foto", "foto", "#58B6D8", "Producto, retrato, equipo", [
   S("Foto de producto",                  250000),
   S("Retrato y marca personal",          200000, unidad="45 min, 10 fotos"),
   S("Foto de equipo",                    400000),
   S("Retoque y edición",                  40000, unidad="por foto"),
 ]),
 ("Marca", "marca", "#E7B544", "Identidad, cartas, empaques", [
   S("Identidad de marca",                400000),   # solo logo → completa ~1.2M (en la ficha)
   S("Estrategia y ADN de marca",         300000),
   S("Papelería y piezas de marca",       250000),
   S("Empaques y etiquetas",              350000),
   S("Carta o menú",                      300000),
 ]),
 ("Redes", "redes", "#79C257", "Contenido, calendario, community", [
   S("Piezas para redes",                 210000, unidad="paquete de 6"),
   S("Calendario y publicación",          250000, mensual=True),
   S("Community: respuestas y mensajes",  290000, mensual=True),
   S("Gestión de cuenta",                1100000, mensual=True, unidad="3 planes"),
 ]),
 ("Digital", "web", "#EC6F6F", "Sitios, catálogos, menús", [
   S("Página web",                       1300000),
   S("Landing de campaña",                700000),
   S("Catálogo en línea",               1000000),
   S("Menú digital con código QR",        450000),
 ]),
 ("Eventos", "eventos", "#D879B4", "Gráfica, registro, cobertura", [
   S("Piezas gráficas del evento",        350000),
   S("Registro y control de invitados",   600000),
   S("Cobertura en foto y video",         800000),
   S("Logística del día",                1800000),
 ]),
 ("Automatización", "automatizacion", "#4CB0A4", "Meta, n8n, documentos", [
   S("Automatización con Meta (básico)",  400000, unidad="montaje"),
   S("Automatización con n8n (avanzado)",1550000, unidad="montaje + operación"),
   S("Reportes automáticos de resultados",300000, mensual=True),
   S("Programa · Operaciones y Logística",900000, unidad="app descargable"),
   S("Programa · Talento Humano",         900000, unidad="app descargable"),
   S("Programa · Legal y Contractual",   1100000, unidad="app descargable"),
   S("Programa · Financiera y Compras",  1100000, unidad="app descargable"),
 ]),
 ("Ilustración y diseño", "ilustracion", "#8B6FE0", "Ilustración, personajes, producción", [
   S("Ilustración y portadas",            180000, unidad="varía con el detalle"),
   S("Diseño de personaje o mascota",     250000),
   S("Diseño de tatuaje",                      0),
   S("Comisiones abiertas",                    0),
   S("Íconos y stickers",                  70000),
   S("Producción física con aliados",          0, unidad="variable · aliados"),
 ]),
]

APERTURA = [("Música","Grabación, mezcla"),
            ("Producción física","Prototipo, corte láser"),
            ("Joyería","Diseño y 3D")]

# Express: encargos chicos que no pasan por cotizador. Se piden y se entregan.
EXPRESS = ["Panfletos", "Carteles", "Avisos", "Presentaciones", "Edición de fotos", "Arreglos de costura"]

# Muestras en vivo: cuatro páginas demo de una sola pantalla que viven en
# demos/ (carpeta autocontenida, rutas relativas, sin librerías). Cada una va
# ATADA al servicio que le corresponde: al abrir ese cuadro en su área, la
# ventana flotante muestra la muestra en vivo con su portada y un enlace para
# abrirla (pantalla completa, pestaña nueva). El resto de cuadros siguen «en
# camino» y se van llenando. Clave = nombre del servicio en español (el de
# MODULOS). (archivo, portada, color propio de la demo, marca)
# Las portadas son miniaturas reales de cada página (captura de su contenido),
# en demos/img/portadas/, no una foto suelta: así el cuadro muestra lo que se
# va a abrir. (archivo, portada, color propio de la demo, marca)
DEMOS = {
 # tiendas.html/bodegas.html: muestras nuevas de digitalización (catálogo real
 # con tallas/stock/envío y catálogo por presentación con precio por unidad).
 # Reemplazan a tienda-ropa.html como catálogo y estrenan «Página web».
 "Catálogo en línea":          ("tiendas.html",      "img/portadas/tiendas.webp",     "#b4512f", "Tienda modelo"),
 # Página web: bodegas es la demo en vivo; revista-moda (blog) y mezcal (portafolio)
 # entran como enlaces de galería (ver GALERIA), que absorbió esas dos fichas.
 "Página web":                 ("bodegas.html",      "img/portadas/bodegas.webp",     "#4a5d3a", "Bodega modelo"),
 "Menú digital con código QR": ("restaurante.html",  "img/portadas/restaurante.webp", "#E0531C", "Rescoldo"),
 # LQS mostrándose a sí misma, su video y su trabajo de redes para Vita Nova
 "Reels y contenido vertical": ("video-lqs.html",    "img/portadas/video.webp",       "#8B5CF6", "LQS"),
 "Identidad de marca":         ("marca-lqs.html",    "img/portadas/marca.webp",       "#8B5CF6", "LQS"),
 "Piezas para redes":          ("redes-lqs.html",    "img/portadas/redes.webp",       "#6D5AE6", "Vita Nova"),
 # Operación de un restaurante: parrilla + bots de WhatsApp/Instagram + reporte
 "Automatización con Meta (básico)": ("automatizacion.html", "img/portadas/automatizacion.webp", "#1f8a4c", "Turno"),
}

# Galerías de muestra: trabajo real (imagen y video) que NO es una página en vivo
# —marcas, cartas, ilustración, video— metido en la ficha del servicio que le toca.
# Conviven con DEMOS: una ficha puede tener demo en vivo Y galería (p.ej. «Diseño
# de marca desde cero» trae la demo marca-lqs + el caso GLATOS). Clave = nombre del
# servicio en español. Rutas relativas a demos/ (se les antepone {{RAIZ}}demos/).
# Cada media: {"t":"img"|"vid","src":…, poster?, ar?, "cap":(es,en)}. Los textos
# bilingües van como (es, en); la marca es un nombre propio, igual en los dos.
GALERIA = {
 "Catálogo en línea": {  # junto a la demo en vivo tiendas.html
   "media": [
     {"t": "vid", "src": "muestras/clips/ceramica-catalogo.mp4", "poster": "muestras/img/ceramica-catalogo-poster.webp",
      "ar": "16/9", "cap": ("Catálogo editorial de cerámica", "Editorial ceramics catalog")},
   ],
 },
 "Página web": {  # bodegas es la demo en vivo; blog y portafolio entran como enlaces
   "media": [
     {"t": "img", "src": "img/portadas/revista.webp", "href": "revista-moda.html",
      "cap": ("Blog · Tendido (abrir)", "Blog · Tendido (open)")},
     {"t": "img", "src": "img/portadas/mezcal.webp", "href": "mezcal.html",
      "cap": ("Portafolio · Casa Tepemete (abrir)", "Portfolio · Casa Tepemete (open)")},
   ],
 },
 "Identidad de marca": {  # GLATOS (la demo en vivo de esta ficha es marca-lqs)
   "marca": "GLATOS", "tono": "#C9102C", "cover": "muestras/img/glatos-cv.webp",
   "media": [
     {"t": "vid", "src": "muestras/clips/glatos-logo.mp4", "poster": "muestras/img/glatos-logo-poster.webp",
      "ar": "16/9", "cap": ("Identidad en movimiento", "Identity in motion")},
     {"t": "vid", "src": "muestras/clips/glatos-carta.mp4", "poster": "muestras/img/glatos-carta-poster.webp",
      "ar": "16/9", "cap": ("Carta animada", "Animated menu")},
   ],
   "ver": {"href": "muestras/glatos.pdf", "lbl": ("Ficha de marca (PDF) →", "Brand sheet (PDF) →")},
 },
 "Papelería y piezas de marca": {  # Alquimia Herbal
   "marca": "Alquimia Herbal", "tono": "#A33A2B", "cover": "muestras/img/alquimia-tablero-cv.webp",
   "media": [
     {"t": "img", "src": "muestras/img/alquimia-tablero.webp", "cap": ("Tablero de identidad", "Identity board")},
     {"t": "vid", "src": "muestras/clips/alquimia-carta.mp4", "poster": "muestras/img/alquimia-carta-poster.webp",
      "ar": "9/16", "cap": ("Carta ilustrada en movimiento", "Illustrated card in motion")},
   ],
 },
 "Carta o menú": {  # cartas de restaurante (diseño editorial + foto de comida)
   "marca": "Carta de autor", "tono": "#C0552F", "cover": "muestras/img/carta-brusquetas-cv.webp",
   "media": [
     {"t": "img", "src": "muestras/img/carta-brusquetas.webp", "cap": ("Brusquetas", "Bruschetta")},
     {"t": "img", "src": "muestras/img/carta-sushi.webp",      "cap": ("Sushi y gunkan", "Sushi & gunkan")},
     {"t": "img", "src": "muestras/img/carta-tartares.webp",   "cap": ("Tartares y tatakis", "Tartares & tatakis")},
     {"t": "img", "src": "muestras/img/carta-pasta.webp",      "cap": ("Pasta italiana", "Italian pasta")},
     {"t": "img", "src": "muestras/img/carta-sopas.webp",      "cap": ("Sopas", "Soups")},
     {"t": "img", "src": "muestras/img/carta-cafe.webp",       "cap": ("Café helado", "Iced coffee")},
   ],
 },
 "Video de marca o empresa": {  # video corporativo Vita Nova
   "marca": "Vita Nova", "tono": "#1F5C44", "cover": "muestras/img/vitanova-cv.webp",
   "media": [
     {"t": "vid", "src": "muestras/clips/vitanova-empresa.mp4", "poster": "muestras/img/vitanova-empresa-poster.webp",
      "ar": "16/9", "cap": ("Video para empresa · Vita Nova", "Brand film · Vita Nova")},
   ],
 },
 "Diseño de personaje o mascota": {  # hojas de personaje
   "marca": "Diseño de personaje", "tono": "#8B6FE0", "cover": "muestras/img/ilu-zarigueya-cv.webp",
   "media": [
     {"t": "img", "src": "muestras/img/ilu-zarigueya.webp", "cap": ("Hoja de personaje", "Character sheet")},
     {"t": "img", "src": "muestras/img/ilu-to.webp",        "cap": ("«TO.» · variaciones y paleta", "«TO.» · variants & palette")},
   ],
 },
}

# Tono propio de cada área SOLO para las tarjetas de «explora por área» en Muestras.
# Los pasteles de MODULOS tienen dos pares repetidos (Video/Eventos en lila, Foto/
# Automatización en azul) y el lila es además el morado de la página: ahí las áreas
# se confundían entre sí y con el fondo. Para que la modularidad se lea como autonomía,
# cada área lleva aquí un matiz distinto y ninguno morado. Se indexa por el slug del
# icono, que no cambia con el idioma. No toca el cotizador: eso sigue con MODULOS.
AREA_TONO = {
    "video":          "#F2975A",  # naranja
    "foto":           "#58B6D8",  # cian
    "marca":          "#E7B544",  # ámbar
    "redes":          "#79C257",  # verde
    "web":            "#EC6F6F",  # coral
    "eventos":        "#D879B4",  # magenta
    "automatizacion": "#4CB0A4",  # teal
    "ilustracion":    "#8B6FE0",  # violeta
}

# Ficha de cada servicio para la ventana flotante de Muestras: «qué es» en una
# frase y una «recomendación de uso» concreta. Indexada por el nombre en español
# (el que vive en MODULOS/EXPRESS), así no depende del idioma de visualización.
# El hueco de imagen/video queda vacío a propósito: se llena cuando haya muestra.
FICHA = {
 # Video
 "Reels y contenido vertical": ("Clips verticales (9:16) para Reels, TikTok y Shorts, con edición ágil y texto en pantalla.",
   "Sube 2–4 al mes para que el algoritmo te muestre; los primeros 3 segundos deciden si se quedan."),
 "Entrevistas": ("Grabación de una conversación a una o dos cámaras, con audio limpio y cortes listos.",
   "Deja la versión larga en YouTube y saca 3–4 cortes verticales para redes: una grabación, varias piezas."),
 "Video para YouTube, acabado cinematográfico": ("Pieza más larga con color, sonido y ritmo tratados como cine.",
   "Úsala como pieza ancla de un lanzamiento o historia de marca; luego se despieza en cortos."),
 "Podcast: grabación y cortes": ("Montaje del episodio a varias cámaras y audio, más los cortes para promocionarlo.",
   "Mantén una frecuencia fija (semanal o quincenal); los cortes son los que traen oyentes nuevos."),
 "Comerciales y piezas de publicidad": ("Comercial con guion, producción y post, pensado para pauta o campaña.",
   "Hazlo cuando vayas a invertir en pauta: una buena pieza baja el costo por resultado."),
 # Foto
 "Retoque y edición": ("Ajuste de luz, color y limpieza sobre una foto que ya tienes.",
   "Úsalo para unificar el feed o rescatar material viejo antes de reinvertir en una sesión."),
 "Sesión a una persona": ("45 minutos, 10 fotos finales: retrato para perfil, marca personal o equipo.",
   "Perfecto para LinkedIn, el «sobre nosotros» y prensa; agéndala cuando cambies de cargo o de imagen."),
 "Foto de producto": ("Fotos limpias del producto, con fondo y luz controlados.",
   "Son la base de tu catálogo y tu pauta; un buen set rinde meses en redes y tienda."),
 "Foto para portafolio": ("Set con intención editorial para mostrar tu trabajo o tu oferta.",
   "Vale más mostrar 6 fotos fuertes que 30 flojas; úsalas en tu web y propuestas."),
 "Foto para publicidad": ("Imágenes con dirección de arte para una campaña o pauta.",
   "Resérvala cuando tengas el mensaje claro: la foto trabaja con el copy, no sola."),
 "Sesión al equipo": ("Retratos coherentes de todo el equipo, mismo estilo y luz.",
   "Dan confianza en la web y en propuestas; repítela cada vez que entre gente nueva."),
 # Marca
 "Solo el logo": ("El símbolo y el logotipo en sus versiones y formatos de uso.",
   "Es el punto de partida, no el final; acompáñalo de color y tipografía para que se sostenga."),
 "Diseño de accesorios de marca": ("Piezas aplicadas: tarjetas, firmas, plantillas, merch.",
   "Pídelo cuando ya tengas el logo; es lo que hace que la marca se vea «armada»."),
 "Consultoría de ADN y orientación de marca": ("Sesión de estrategia: qué dices, a quién y cómo suenas.",
   "Hazla antes de diseñar nada: ahorra rediseños y decisiones al azar."),
 "Empaques": ("Diseño del empaque listo para imprimir, con medidas y troquel.",
   "Clave en producto físico: el empaque es tu vendedor en el punto de venta."),
 "Rediseño de una marca que ya existe": ("Actualización de una identidad que ya tienes, sin perder lo reconocible.",
   "Cuando la marca «ya no te representa» pero no quieres empezar de cero."),
 "Diseño de marca desde cero": ("Identidad completa: estrategia, logo, color, tipografía y aplicaciones.",
   "Para arrancar bien o para un giro grande; es la base de todo lo demás."),
 # Redes
 "Publicaciones sueltas": ("Piezas individuales a demanda, para una fecha o un anuncio.",
   "Úsalas para tapar huecos puntuales; para crecer conviene un plan con calendario."),
 "Comercial corto para pauta": ("Pieza breve y directa pensada para anuncios pagos.",
   "Acompáñala de presupuesto de pauta: sin inversión no despega."),
 "Paquete de publicaciones": ("6 piezas coherentes entre sí, listas para programar.",
   "Ideal para sostener presencia un mes sin improvisar cada día."),
 "Respuesta de comentarios y mensajes": ("Gestión diaria de comentarios, DMs y dudas.",
   "Responder rápido vende; actívalo si recibes preguntas que se quedan sin contestar."),
 "Plan Básico — presencia viva": ("Para que la cuenta no se muera: calendario de 8–10 publicaciones, 2 reels, diseño y respuesta de mensajes al mes.",
   "El piso para mantener presencia constante en 1 red; ideal para emprendimientos o cuentas pequeñas."),
 "Plan Estándar — cuenta activa": ("Todo para sostener y hacer crecer la cuenta: 16–20 publicaciones, 4–6 reels/videos, 1 sesión de contenido, community y reporte al mes.",
   "El recomendado: incluye crear video y foto, no solo publicar. Para 1–2 redes que quieren moverse de verdad."),
 "Plan Pro — operación completa": ("Para empresas con más volumen, varias áreas o multicuenta: más video y piezas, pauta gestionada y social manager dedicado.",
   "Se arma a la medida según tamaño, áreas y número de cuentas; integra web, marca y automatización si hace falta."),
 "Portada y destacados de temporada": ("Portadas, banners y destacados de Instagram al estilo de la temporada o campaña.",
   "Es lo primero que ve quien entra a tu perfil; cámbialo por fecha para que siempre se sienta al día."),
 # Temporada (skins): refrescos opcionales de la marca para una fecha, personalizables
 "Skin de logo de temporada": ("Una variación de tu logo a tono de la fecha, sin perder la identidad.",
   "Refresca sin rehacer la marca: Navidad, aniversario, lanzamiento. Se revierte al logo normal después."),
 "Mini sesión de fotos de temporada": ("Sesión corta y temática, lista para las piezas de la fecha.",
   "Súmala al paquete de temporada para que fotos y diseño hablen el mismo idioma."),
 "Set de íconos y stickers de temporada": ("Íconos, stickers y adornos a tono de la fecha para tus piezas y stories.",
   "Dan aire festivo a la cuenta sin rediseñar todo; combinan con la skin de logo."),
 "Skin de temporada para la página": ("Adapta la temática del sitio a la fecha —colores, banner, detalles— y se revierte después.",
   "Para cuando quieres que la web también se sienta en temporada, sin rehacerla."),
 # Digital
 "Menú digital con código QR": ("Menú web que se abre con un QR, fácil de actualizar.",
   "Perfecto para restaurantes y cafés: cambias precios sin reimprimir nada."),
 "Landing para una campaña": ("Una sola página enfocada en una acción (comprar, registrarse, escribir).",
   "Úsala con pauta y manda todo el tráfico ahí para medir mejor."),
 "Blog": ("Sitio con artículos, pensado para aparecer en Google.",
   "Juega a largo plazo: suma visitas que no pagas, pero necesita publicar seguido."),
 "Portafolio web": ("Web para mostrar tu trabajo con orden y jerarquía.",
   "Tu mejor propuesta vive en un link, no en un PDF; ideal para freelancers y estudios."),
 "Catálogo en línea": ("Catálogo navegable de productos o servicios, con fichas.",
   "Cuando tienes muchos productos y quieres que te escriban con el producto ya claro."),
 "Página web": ("Sitio completo de varias secciones, hecho a tu medida.",
   "La casa propia de tu marca; todo lo demás (redes, pauta) debería llevar aquí."),
 # Eventos
 "Diseño de accesorios del evento": ("Piezas gráficas del evento: señalética, escarapelas, pantallas.",
   "Dan la sensación de «evento cuidado»; defínelos con tiempo para imprimir."),
 "Fondos y carruseles para conferencia": ("Plantillas y fondos para las pantallas y presentaciones.",
   "Unifican la imagen en tarima: todo se ve de la misma marca."),
 "Registro y control de invitados": ("Registro de asistentes y control en puerta, con contacto después del evento.",
   "Clave si quieres volver a hablarle a quien asistió: el evento no termina ese día."),
 "Cobertura en foto y video": ("Registro del evento en foto y video, con entrega editada.",
   "Es el material que alimenta tus redes los meses siguientes; no lo dejes por fuera."),
 "Insta foto: la foto llega el mismo día": ("Los asistentes reciben su foto el mismo día del evento.",
   "Genera que compartan en el momento; ideal para activaciones de marca."),
 "Logística completa del día": ("Nos encargamos del montaje, los tiempos y la operación del día.",
   "Para cuando quieres estar en tu evento, no corriendo detrás de él."),
 # Automatización
 "Reporte automático de números cada semana": ("Un resumen de tus métricas llega solo cada semana.",
   "Para decidir con datos sin perder horas armando reportes."),
 "WhatsApp Business: catálogo y respuestas": ("Montaje de WhatsApp Business con catálogo y respuestas rápidas.",
   "Si vendes por WhatsApp, ordena el caos y responde más rápido."),
 "Solicitudes que llegan directo, sin bandeja": ("Los pedidos caen directo donde los atiendes, sin formularios perdidos.",
   "Úsalo si se te traspapelan solicitudes: menos fricción, menos ventas perdidas."),
 "Respuestas automáticas en Instagram": ("Respuestas automáticas a mensajes y comentarios frecuentes.",
   "Para no dejar a nadie en visto cuando llega una ola de mensajes."),
 "Agente de WhatsApp que responde y cotiza": ("Un asistente que responde dudas y arma cotizaciones por WhatsApp.",
   "Cuando el volumen te supera: atiende 24/7 y te pasa solo lo que importa."),
 # Express
 "Panfletos": ("Volantes informativos o promocionales, listos para imprimir o compartir.",
   "Para una promo o un evento puntual; claros y con una sola acción."),
 "Carteles": ("Afiches para pared, vitrina o redes.",
   "Un mensaje grande y legible a distancia; no los llenes de texto."),
 "Avisos": ("Piezas de aviso: horarios, cambios, anuncios cortos.",
   "Para comunicar algo puntual rápido y que se vea ordenado."),
 "Presentaciones": ("Diapositivas con tu marca, ordenadas y claras.",
   "Para vender, enseñar o pitchear: una buena presentación sostiene la reunión."),
 "Edición de fotos": ("Ajustes rápidos sobre fotos que ya tienes.",
   "Para salir del paso con buen material sin montar una sesión."),
 "Arreglos de costura": ("Ajustes y arreglos de prendas.",
   "Lo pequeño que nadie más te resuelve el mismo día."),
 # Ilustración y diseño
 "Portadas e ilustración": ("Ilustración original para portadas de disco, libro, single o evento.",
   "Una imagen propia dice más que un banco de fotos: pídela cuando no quieras parecerte a nadie."),
 "Ilustración de personajes": ("Creación de un personaje o mascota, con sus poses y expresiones.",
   "Un personaje propio le pone cara a tu marca y viaja a stickers, merch y redes."),
 "Diseño de tatoo": ("Diseño de tatuaje a medida, listo para que tu tatuador lo calque.",
   "Llévalo afinado al estudio: ahorras tiempo de silla y sale justo como lo pensaste."),
 "Comisiones abiertas": ("Encargos de arte a tu idea: lo que imagines, lo ilustramos.",
   "Si no está en la lista, cuéntanoslo. El límite es tu imaginación."),
 # --- servicios reformulados (nueva estructura) ---
 "Video de marca o empresa": ("Pieza más larga para empresa o lanzamiento, con color, sonido y ritmo tratados como cine.",
   "Úsala como pieza ancla de la marca; luego se despieza en cortos para redes."),
 "Comercial para pauta": ("Pieza breve y directa pensada para anuncios pagos.",
   "Acompáñala de presupuesto de pauta: sin inversión no despega."),
 "Entrevista o podcast": ("Grabación de una conversación a una o dos cámaras, audio limpio y cortes listos.",
   "Deja la versión larga en YouTube y saca 3–4 cortes verticales: una grabación, varias piezas."),
 "Retrato y marca personal": ("45 minutos, 10 fotos finales: retrato para perfil, marca personal o prensa.",
   "Perfecto para LinkedIn y el «sobre nosotros»; agéndalo cuando cambies de cargo o imagen."),
 "Foto de equipo": ("Retratos coherentes de todo el equipo, mismo estilo y luz.",
   "Dan confianza en la web y en propuestas; repítela cuando entre gente nueva."),
 "Identidad de marca": ("La identidad completa: desde solo el logo hasta logo + color + tipografía + aplicaciones y manual. El alcance decide el precio.",
   "Arranca aquí si empiezas o das un giro grande; es la base de todo. Completa, desde ~$1.200.000."),
 "Estrategia y ADN de marca": ("Sesión de estrategia: qué dices, a quién y cómo suenas, antes de diseñar nada.",
   "Hazla primero: ahorra rediseños y decisiones al azar."),
 "Papelería y piezas de marca": ("Piezas aplicadas de la marca: tarjetas, firmas, plantillas, sellos, merch.",
   "Pídelo cuando ya tengas la identidad; es lo que hace que la marca se vea «armada»."),
 "Empaques y etiquetas": ("Diseño de empaque y etiqueta listo para imprimir, con medidas y troquel.",
   "Clave en producto físico: el empaque es tu vendedor en el punto de venta."),
 "Carta o menú": ("Diseño de tu carta o menú —impreso o digital— con tus platos, fotos y precios, en un sistema que se ve de restaurante serio.",
   "Una buena carta vende los platos de más margen. Combínala con el menú digital con QR."),
 "Piezas para redes": ("Piezas para tus redes, sueltas o en paquete de 6, coherentes y listas para programar.",
   "Suelta desde $40.000; el paquete rinde para sostener un mes sin improvisar."),
 "Calendario y publicación": ("Armamos el calendario del mes y publicamos por ti, a tiempo y en orden.",
   "Lo mensual que mantiene la cuenta viva sin que tengas que estar encima."),
 "Community: respuestas y mensajes": ("Gestión diaria de comentarios, DMs y dudas.",
   "La atención rápida convierte seguidores en clientes; no la dejes sin responder."),
 "Gestión de cuenta": ("El manejo completo de tus redes en un plan mensual, en tres niveles: Básico ($1.1M), Estándar ($2.2M) y Pro ($2.6M).",
   "Elige el nivel por cuánto quieres publicar y crecer; incluye contenido, calendario y community."),
 "Landing de campaña": ("Una sola página enfocada en una campaña: un mensaje, un formulario, lista para pauta.",
   "Úsala cuando vayas a invertir en anuncios: concentra el clic en una sola acción."),
 "Piezas gráficas del evento": ("Toda la gráfica del evento: invitaciones, señalética, fondos y carruseles.",
   "Un evento que se ve cuidado empieza por su gráfica; pídela con tiempo."),
 "Logística del día": ("Producción y logística del día: montaje, equipo en sitio y que todo corra.",
   "Para eventos grandes; nos encargamos del día para que tú solo recibas."),
 "Automatización con Meta (básico)": ("Respuestas automáticas y catálogo en WhatsApp e Instagram, sobre la API oficial de Meta: rápido de montar y sin servidor propio.",
   "Para responder al instante y vender por WhatsApp. Costo de operar: Meta cobra por conversación iniciada por plantilla (centavos); lo demás es gratis."),
 "Automatización con n8n (avanzado)": ("Flujos de varios pasos que conectan tus apps (CRM, Airtable, correo, IA) y hacen lo que Meta sola no puede: lógica, cruces y un agente que responde y cotiza.",
   "Para operaciones de verdad. Costo de operar: necesita un n8n corriendo (desde ~$60.000/mes en la nube) o lo alojamos; lo dejamos andando y lo mantenemos."),
 "Reportes automáticos de resultados": ("Un reporte de tus números que llega solo cada semana o mes, sin que lo pidas.",
   "Ver los números seguido es lo que hace que mejoren; lo dejamos andando."),
 "Programa · Operaciones y Logística": ("App descargable que genera actas de entrega y devolución de activos: blinda a la organización cuando asigna equipos, dotación o materiales.",
   "Para equipos con inventario y personal en campo. Se instala en PC o móvil y queda tuya."),
 "Programa · Talento Humano": ("App que emite certificados laborales, constancias de ingresos/retenciones y memorandos con firma digital, desde tus datos de contrato.",
   "El colaborador los pide por un portal o bot y salen al instante. Menos papeleo, todo trazable."),
 "Programa · Legal y Contractual": ("App que arma contratos de prestación de servicios y actas de reunión desde una base de datos: plantillas que autocompletan cláusulas, montos y plazos.",
   "Para quien firma seguido. Un clic y el documento sale listo y uniforme."),
 "Programa · Financiera y Compras": ("App de órdenes de compra, requisiciones y legalización de viáticos: valida presupuesto por centro de costos y encadena aprobaciones.",
   "Ordena el gasto de punta a punta y lo deja listo para contabilidad."),
 "Ilustración y portadas": ("Ilustración a tu idea: portadas, piezas editoriales, lo que imagines.",
   "El precio varía con el detalle; cuéntanos la idea y te decimos."),
 "Diseño de personaje o mascota": ("Creación de un personaje o mascota, con sus poses y expresiones.",
   "Un personaje propio le pone cara a tu marca y viaja a stickers, merch y redes."),
 "Diseño de tatuaje": ("Diseño de tatuaje a tu medida, listo para llevar al estudio.",
   "Tráenos la idea o la referencia; lo dejamos limpio para tatuar."),
 "Íconos y stickers": ("Set de íconos o stickers con un estilo propio, para tu app, web o redes.",
   "Pequeños pero marcan; le dan identidad a cada detalle."),
 "Producción física con aliados": ("Mandamos a hacer tus piezas físicas —pines, esculturas, pinturas, adaptación de locales— con nuestra red de aliados, para que la idea se vuelva objeto.",
   "El precio es de cada aliado, así que varía con la pieza y el material. Te conseguimos el proveedor y coordinamos."),
}
EN_FICHA = {
 "Reels y contenido vertical": ("Vertical clips (9:16) for Reels, TikTok and Shorts, with snappy edits and on-screen text.",
   "Post 2–4 a month so the algorithm shows you; the first 3 seconds decide if they stay."),
 "Entrevistas": ("A conversation shot on one or two cameras, clean audio and ready-to-post cuts.",
   "Leave the long version on YouTube and pull 3–4 vertical cuts for social: one shoot, many pieces."),
 "Video para YouTube, acabado cinematográfico": ("A longer piece with color, sound and pacing treated like film.",
   "Use it as the anchor of a launch or brand story; then break it into shorts."),
 "Podcast: grabación y cortes": ("Episode edit on several cameras and audio, plus the clips to promote it.",
   "Keep a fixed cadence (weekly or biweekly); the clips are what bring new listeners."),
 "Comerciales y piezas de publicidad": ("A commercial with script, production and post, built for paid media.",
   "Do it when you'll invest in ads: a good piece lowers your cost per result."),
 "Retoque y edición": ("Light, color and clean-up on a photo you already have.",
   "Use it to unify your feed or rescue old material before reinvesting in a shoot."),
 "Sesión a una persona": ("45 minutes, 10 final photos: portrait for profile, personal brand or team.",
   "Perfect for LinkedIn, the «about us» and press; book it when you change role or image."),
 "Foto de producto": ("Clean product shots with controlled background and light.",
   "They're the base of your catalogue and ads; a good set lasts months in social and store."),
 "Foto para portafolio": ("An editorial set to show your work or your offer.",
   "Six strong photos beat thirty weak ones; use them on your site and proposals."),
 "Foto para publicidad": ("Images with art direction for a campaign or paid media.",
   "Book it once the message is clear: the photo works with the copy, not alone."),
 "Sesión al equipo": ("Consistent portraits of the whole team, same style and light.",
   "They build trust on the site and in proposals; repeat whenever new people join."),
 "Solo el logo": ("The symbol and wordmark in their versions and usage formats.",
   "It's the starting point, not the end; pair it with color and type so it holds up."),
 "Diseño de accesorios de marca": ("Applied pieces: cards, signatures, templates, merch.",
   "Ask for it once you have the logo; it's what makes a brand look «put together»."),
 "Consultoría de ADN y orientación de marca": ("A strategy session: what you say, to whom and how you sound.",
   "Do it before designing anything: it saves redesigns and random decisions."),
 "Empaques": ("Packaging design ready to print, with measurements and die-cut.",
   "Key for physical products: packaging is your salesperson at the point of sale."),
 "Rediseño de una marca que ya existe": ("An update of an identity you already have, without losing what's recognizable.",
   "When the brand «no longer represents you» but you don't want to start from scratch."),
 "Diseño de marca desde cero": ("Full identity: strategy, logo, color, type and applications.",
   "To start right or for a big pivot; it's the base of everything else."),
 "Publicaciones sueltas": ("Individual pieces on demand, for a date or an announcement.",
   "Use them to fill specific gaps; to grow, a plan with a calendar works better."),
 "Comercial corto para pauta": ("A short, direct piece built for paid ads.",
   "Pair it with an ad budget: without investment it won't take off."),
 "Paquete de publicaciones": ("6 pieces that hang together, ready to schedule.",
   "Ideal to sustain presence for a month without improvising every day."),
 "Respuesta de comentarios y mensajes": ("Daily handling of comments, DMs and questions.",
   "Replying fast sells; turn it on if questions pile up unanswered."),
 "Plan Básico — presencia viva": ("So the account doesn't die: a calendar of 8–10 posts, 2 reels, design and message replies a month.",
   "The baseline to keep steady presence on 1 network; ideal for small businesses or small accounts."),
 "Plan Estándar — cuenta activa": ("Everything to sustain and grow the account: 16–20 posts, 4–6 reels/videos, 1 content session, community and report a month.",
   "The recommended one: it includes creating video and photo, not just posting. For 1–2 networks that want to really move."),
 "Plan Pro — operación completa": ("For companies with more volume, several areas or multiple accounts: more video and pieces, managed ads and a dedicated social manager.",
   "Built to measure by size, areas and number of accounts; folds in web, brand and automation if needed."),
 "Portada y destacados de temporada": ("Covers, banners and Instagram highlights in the season's or campaign's style.",
   "It's the first thing people see on your profile; swap it per date so it always feels current."),
 "Skin de logo de temporada": ("A variation of your logo in the season's mood, without losing the identity.",
   "Refresh without redoing the brand: Christmas, anniversary, a launch. Reverts to the normal logo afterwards."),
 "Mini sesión de fotos de temporada": ("A short, themed session, ready for the date's pieces.",
   "Add it to the seasonal pack so photos and design speak the same language."),
 "Set de íconos y stickers de temporada": ("Icons, stickers and ornaments in the date's mood for your pieces and stories.",
   "They give the account a festive air without redesigning everything; they match the logo skin."),
 "Skin de temporada para la página": ("Adapts the site's theme to the date —colors, banner, details— and reverts afterwards.",
   "For when you want the website to feel seasonal too, without rebuilding it."),
 "Menú digital con código QR": ("A web menu that opens with a QR, easy to update.",
   "Perfect for restaurants and cafés: change prices without reprinting anything."),
 "Landing para una campaña": ("A single page focused on one action (buy, sign up, message).",
   "Use it with ads and send all the traffic there to measure better."),
 "Blog": ("A site with articles, built to show up on Google.",
   "A long game: it adds visits you don't pay for, but needs regular posting."),
 "Portafolio web": ("A site to show your work with order and hierarchy.",
   "Your best proposal lives in a link, not a PDF; ideal for freelancers and studios."),
 "Catálogo en línea": ("A browsable catalogue of products or services, with detail pages.",
   "When you have many products and want people to write with the product already clear."),
 "Página web": ("A full multi-section site, built to measure.",
   "Your brand's own house; everything else (social, ads) should lead here."),
 "Diseño de accesorios del evento": ("The event's graphics: signage, badges, screens.",
   "They give the feel of a «well-run event»; define them early to print in time."),
 "Fondos y carruseles para conferencia": ("Templates and backdrops for the screens and presentations.",
   "They unify the image on stage: everything looks like the same brand."),
 "Registro y control de invitados": ("Guest check-in and door control, with contact after the event.",
   "Key if you want to reach out again to who attended: the event doesn't end that day."),
 "Cobertura en foto y video": ("A record of the event in photo and video, delivered edited.",
   "It's the material that feeds your social for months; don't leave it out."),
 "Insta foto: la foto llega el mismo día": ("Guests get their photo the same day of the event.",
   "It gets them sharing in the moment; ideal for brand activations."),
 "Logística completa del día": ("We handle the set-up, the timing and the running of the day.",
   "For when you want to be at your event, not chasing after it."),
 "Reporte automático de números cada semana": ("A summary of your metrics arrives on its own each week.",
   "To decide with data without losing hours building reports."),
 "WhatsApp Business: catálogo y respuestas": ("WhatsApp Business set up with catalogue and quick replies.",
   "If you sell on WhatsApp, it tidies the chaos and replies faster."),
 "Solicitudes que llegan directo, sin bandeja": ("Requests land straight where you handle them, no lost forms.",
   "Use it if requests slip through the cracks: less friction, fewer lost sales."),
 "Respuestas automáticas en Instagram": ("Automatic replies to frequent messages and comments.",
   "So no one is left on read when a wave of messages arrives."),
 "Agente de WhatsApp que responde y cotiza": ("An assistant that answers questions and builds quotes on WhatsApp.",
   "When volume overwhelms you: it works 24/7 and passes you only what matters."),
 "Panfletos": ("Informational or promotional flyers, ready to print or share.",
   "For a promo or a specific event; clear and with a single action."),
 "Carteles": ("Posters for wall, window or social.",
   "One big, legible-from-afar message; don't fill them with text."),
 "Avisos": ("Notice pieces: hours, changes, short announcements.",
   "To communicate something specific fast and have it look tidy."),
 "Presentaciones": ("Slides in your brand, ordered and clear.",
   "To sell, teach or pitch: a good deck holds the meeting together."),
 "Edición de fotos": ("Quick adjustments on photos you already have.",
   "To get by with good material without setting up a shoot."),
 "Arreglos de costura": ("Adjustments and repairs on garments.",
   "The small thing no one else solves for you the same day."),
 "Portadas e ilustración": ("Original illustration for album, book, single or event covers.",
   "Your own image says more than stock: ask for it when you don't want to look like anyone else."),
 "Ilustración de personajes": ("A character or mascot, with its poses and expressions.",
   "Your own character gives your brand a face and travels to stickers, merch and social."),
 "Diseño de tatoo": ("Custom tattoo design, ready for your artist to trace.",
   "Take it dialed-in to the studio: you save chair time and it comes out just as you pictured it."),
 "Comisiones abiertas": ("Art commissions to your idea: whatever you imagine, we illustrate.",
   "If it's not on the list, tell us. The limit is your imagination."),
 # --- reformulated services (new structure) ---
 "Video de marca o empresa": ("A longer piece for a company or launch, with color, sound and pacing treated like film.",
   "Use it as the brand's anchor piece; then break it into shorts for social."),
 "Comercial para pauta": ("A short, direct piece built for paid ads.",
   "Pair it with an ad budget: without spend it won't take off."),
 "Entrevista o podcast": ("A conversation shot on one or two cameras, clean audio and ready cuts.",
   "Leave the long version on YouTube and pull 3–4 vertical cuts: one shoot, many pieces."),
 "Retrato y marca personal": ("45 minutes, 10 final photos: portrait for profile, personal brand or press.",
   "Perfect for LinkedIn and the «about us»; book it when you change role or image."),
 "Foto de equipo": ("Consistent portraits of the whole team, same style and light.",
   "They build trust on the site and in proposals; repeat when new people join."),
 "Identidad de marca": ("The full identity: from logo only to logo + color + type + applications and guidelines. Scope sets the price.",
   "Start here when you launch or make a big turn; it's the base for everything. Full, from ~$1,200,000."),
 "Estrategia y ADN de marca": ("A strategy session: what you say, to whom and how you sound, before designing anything.",
   "Do it first: it saves redesigns and random decisions."),
 "Papelería y piezas de marca": ("Applied brand pieces: cards, signatures, templates, stamps, merch.",
   "Ask for it once you have the identity; it's what makes a brand look «put together»."),
 "Empaques y etiquetas": ("Print-ready packaging and label design, with sizes and die-cut.",
   "Key for physical products: packaging is your salesperson at the point of sale."),
 "Carta o menú": ("Your menu designed —print or digital— with your dishes, photos and prices, in a system that looks like a serious restaurant.",
   "A good menu sells the higher-margin dishes. Pair it with the digital QR menu."),
 "Piezas para redes": ("Pieces for your social, single or in a pack of 6, consistent and ready to schedule.",
   "Single from $40,000; the pack keeps a month going without improvising."),
 "Calendario y publicación": ("We build the month's calendar and post for you, on time and in order.",
   "The monthly work that keeps the account alive without you on top of it."),
 "Community: respuestas y mensajes": ("Daily handling of comments, DMs and questions.",
   "Fast replies turn followers into customers; don't leave them unanswered."),
 "Gestión de cuenta": ("Full management of your social on a monthly plan, in three tiers: Basic ($1.1M), Standard ($2.2M) and Pro ($2.6M).",
   "Pick the tier by how much you want to post and grow; includes content, calendar and community."),
 "Landing de campaña": ("A single page focused on one campaign: one message, one form, ready for ads.",
   "Use it when you'll invest in ads: it concentrates the click on one action."),
 "Piezas gráficas del evento": ("All the event's graphics: invitations, signage, backdrops and carousels.",
   "A polished event starts with its graphics; ask early."),
 "Logística del día": ("Production and logistics for the day: setup, on-site team, and keeping it all running.",
   "For big events; we handle the day so you just host."),
 "Automatización con Meta (básico)": ("Automatic replies and catalog on WhatsApp and Instagram, on Meta's official API: quick to set up and no server of your own.",
   "To reply instantly and sell over WhatsApp. Running cost: Meta charges per template-initiated conversation (cents); the rest is free."),
 "Automatización con n8n (avanzado)": ("Multi-step flows connecting your apps (CRM, Airtable, email, AI) that do what Meta alone can't: logic, cross-checks and an agent that answers and quotes.",
   "For real operations. Running cost: it needs an n8n running (from ~$60,000/mo in the cloud) or we host it; we keep it running and maintained."),
 "Reportes automáticos de resultados": ("A report of your numbers that arrives on its own every week or month, unprompted.",
   "Seeing the numbers often is what makes them improve; we leave it running."),
 "Programa · Operaciones y Logística": ("A downloadable app that generates asset handover and return records: it protects the organization when it assigns gear, kit or materials.",
   "For teams with inventory and field staff. Installs on PC or mobile and it's yours."),
 "Programa · Talento Humano": ("An app that issues employment certificates, income/withholding statements and memos, digitally signed, from your contract data.",
   "Staff request them from a portal or bot and they come out instantly. Less paperwork, all traceable."),
 "Programa · Legal y Contractual": ("An app that builds service contracts and meeting minutes from a database: templates that autofill clauses, amounts and terms.",
   "For whoever signs often. One click and the document comes out ready and uniform."),
 "Programa · Financiera y Compras": ("An app for purchase orders, requisitions and travel-expense reconciliation: it validates budget by cost center and chains approvals.",
   "It orders spending end to end and leaves it ready for accounting."),
 "Ilustración y portadas": ("Illustration to your idea: covers, editorial pieces, whatever you imagine.",
   "Price varies with the detail; tell us the idea and we'll say."),
 "Diseño de personaje o mascota": ("Creating a character or mascot, with its poses and expressions.",
   "A character of your own gives your brand a face and travels to stickers, merch and social."),
 "Diseño de tatuaje": ("A custom tattoo design, ready to take to the studio.",
   "Bring us the idea or reference; we leave it clean to tattoo."),
 "Íconos y stickers": ("A set of icons or stickers with a style of their own, for your app, site or social.",
   "Small but they count; they give identity to every detail."),
 "Producción física con aliados": ("We get your physical pieces made —pins, sculptures, paintings, venue adaptations— through our partner network, so the idea becomes an object.",
   "The price is each partner's, so it varies with the piece and material. We find the supplier and coordinate."),
}

# Datos que la ley exige y que hay que llenar antes de publicar la página legal.
# Lo que quede con FALTA sale marcado en rojo en la página y publicar.py avisa.
FALTA = '<mark class="falta">FALTA: %s</mark>'
LEGAL = {
    "RAZON":       "Caleb Parra Vargas",
    "NIT":         "",
    "DOMICILIO":   "Medellín, Antioquia",
    "DIRECCION":   "Calle 61 #48-7, Medellín",
    "RESPONSABLE": "Caleb Parra Vargas — loqueseaproductionsp1@gmail.com",
    "VIGENCIA":    "4 de octubre de 2026",
}

CONTACTO = {
    "whatsapp": "573332791710",          # +57 333 279 1710
    "tel_visible": "333 279 1710",
    "correo": "loqueseaproductionsp1@gmail.com",
}

# --------------------------------------------------------------- idiomas
# El inglés vive en páginas reales bajo en/ — nada se guarda en el navegador,
# porque la política de cookies promete que el sitio no guarda nada. Ver partes-en/.
EN_AREAS = {
  "Video": ("Video", "Reels, YouTube, commercials"),
  "Foto": ("Photo", "Product, advertising, sessions"),
  "Marca": ("Brand", "Identity, packaging, consulting"),
  "Redes": ("Social", "Content, calendar, community"),
  "Digital": ("Digital", "Sites, catalogues, menus"),
  "Eventos": ("Events", "Logistics, check-in, coverage"),
  "Automatización": ("Automation", "WhatsApp, Instagram, follow-up"),
  "Ilustración y diseño": ("Illustration & design", "Covers, illustration, tattoos, commissions"),
}
EN_SERV = {
  "Reels y contenido vertical": "Reels and vertical content",
  "Entrevistas": "Interviews",
  "Video para YouTube, acabado cinematográfico": "YouTube video, cinematic finish",
  "Podcast: grabación y cortes": "Podcast: recording and clips",
  "Comerciales y piezas de publicidad": "Commercials and ad pieces",
  "Retoque y edición": "Retouching and editing",
  "Sesión a una persona": "One-person session",
  "Foto de producto": "Product photography",
  "Foto para portafolio": "Portfolio photography",
  "Foto para publicidad": "Advertising photography",
  "Sesión al equipo": "Team session",
  "Solo el logo": "Logo only",
  "Diseño de accesorios de marca": "Brand merchandise design",
  "Consultoría de ADN y orientación de marca": "Brand DNA and positioning consulting",
  "Empaques": "Packaging",
  "Rediseño de una marca que ya existe": "Redesign of an existing brand",
  "Diseño de marca desde cero": "Brand design from scratch",
  "Publicaciones sueltas": "Single posts",
  "Comercial corto para pauta": "Short ad for paid media",
  "Paquete de publicaciones": "Post bundle",
  "Respuesta de comentarios y mensajes": "Comment and message replies",
  "Plan Básico — presencia viva": "Basic plan — living presence",
  "Plan Estándar — cuenta activa": "Standard plan — active account",
  "Plan Pro — operación completa": "Pro plan — full operation",
  "Portada y destacados de temporada": "Seasonal cover and highlights",
  "Skin de logo de temporada": "Seasonal logo skin",
  "Mini sesión de fotos de temporada": "Seasonal mini photo session",
  "Set de íconos y stickers de temporada": "Seasonal icon and sticker set",
  "Skin de temporada para la página": "Seasonal skin for the website",
  "Menú digital con código QR": "Digital menu with QR code",
  "Landing para una campaña": "Campaign landing page",
  "Blog": "Blog",
  "Portafolio web": "Portfolio site",
  "Catálogo en línea": "Online catalogue",
  "Página web": "Website",
  "Diseño de accesorios del evento": "Event collateral design",
  "Fondos y carruseles para conferencia": "Backdrops and conference slides",
  "Registro y control de invitados": "Guest check-in and management",
  "Cobertura en foto y video": "Photo and video coverage",
  "Insta foto: la foto llega el mismo día": "Insta photo: guests get theirs same day",
  "Logística completa del día": "Full event-day logistics",
  "Reporte automático de números cada semana": "Automatic weekly numbers report",
  "WhatsApp Business: catálogo y respuestas": "WhatsApp Business: catalogue and replies",
  "Solicitudes que llegan directo, sin bandeja": "Requests that arrive directly, no inbox",
  "Respuestas automáticas en Instagram": "Automatic replies on Instagram",
  "Agente de WhatsApp que responde y cotiza": "WhatsApp agent that answers and quotes",
  "Portadas e ilustración": "Covers & illustration",
  "Ilustración de personajes": "Character illustration",
  "Diseño de tatoo": "Tattoo design",
  "Comisiones abiertas": "Open commissions",
  # --- servicios reformulados (nueva estructura) ---
  "Video de marca o empresa": "Brand or company video",
  "Comercial para pauta": "Ad for paid media",
  "Entrevista o podcast": "Interview or podcast",
  "Retrato y marca personal": "Portrait & personal brand",
  "Foto de equipo": "Team photo",
  "Identidad de marca": "Brand identity",
  "Estrategia y ADN de marca": "Brand strategy & DNA",
  "Papelería y piezas de marca": "Brand stationery & collateral",
  "Empaques y etiquetas": "Packaging & labels",
  "Carta o menú": "Menu design",
  "Piezas para redes": "Social posts",
  "Calendario y publicación": "Calendar & posting",
  "Community: respuestas y mensajes": "Community: replies & messages",
  "Gestión de cuenta": "Account management",
  "Landing de campaña": "Campaign landing",
  "Piezas gráficas del evento": "Event graphics",
  "Logística del día": "Event-day logistics",
  "Automatización con Meta (básico)": "Automation with Meta (basic)",
  "Automatización con n8n (avanzado)": "Automation with n8n (advanced)",
  "Reportes automáticos de resultados": "Automatic results reports",
  "Programa · Operaciones y Logística": "App · Operations & Logistics",
  "Programa · Talento Humano": "App · HR & People",
  "Programa · Legal y Contractual": "App · Legal & Contracts",
  "Programa · Financiera y Compras": "App · Finance & Purchasing",
  "Ilustración y portadas": "Illustration & covers",
  "Diseño de personaje o mascota": "Character or mascot design",
  "Diseño de tatuaje": "Tattoo design",
  "Íconos y stickers": "Icons & stickers",
  "Producción física con aliados": "Physical production with partners",
}
EN_UNIDAD = {
  "por foto": "per photo", "45 min, 10 fotos": "45 min, 10 photos", "por pieza": "per piece",
  "6 piezas": "6 pieces", "plan Básico": "Basic plan",
  "plan Estándar · recomendado": "Standard plan · recommended", "desde · a la medida": "from · tailored",
  "con contacto post evento": "with post-event follow-up", "montaje": "setup",
  "mensajes y comentarios": "messages and comments", "varía con el detalle": "varies with detail",
}
EN_APERTURA = [("Music", "Recording, mixing"),
               ("Physical production", "Prototype, laser cutting"),
               ("Jewellery", "Design and 3D")]
EN_EXPRESS = ["Flyers", "Posters", "Notices", "Presentations", "Photo editing", "Sewing repairs"]
EN_PAGINAS = {
  "index.html": ("LQS — Your ideas' best friend",
    "Your ideas' best friend. LQS is not just a creative agency: it is a modular creative agency. "
    "Seven independent areas, hired on their own or connected. We are wherever we are needed."),
  "nosotros.html": ("Who we are — LQS",
    "Not just a creative agency: a modular creative agency. Why LQS exists and how we work."),
  "muestras.html": ("Work — LQS",
    "What we have done, by area. Filter by category and tap a sample to open it."),
  "cotizador.html": ("Quote builder — LQS",
    "Pick service by service and the total builds itself. Each item priced, whole areas discounted."),
  "legal.html": ("Terms, data and cookies — LQS",
    "Terms of service, personal data policy (Colombian Law 1581 of 2012) and cookie policy. "
    "This site uses no cookies."),
  "404.html": ("This does not exist — LQS", "The page you are looking for is not here."),
}
EN_ENCAB = {
 "encab-nosotros": ("Who we are", "We bring your ideas to life",
   "A modular creative agency: take the front you need today and add the rest when you want. The limit is your imagination."),
 "encab-muestras": ("Work", "What we have done",
   "Spin through the areas and pick one to unfold its work. Tap a sample to open it."),
 "encab-legal": ("Legal", "The legal part, in plain words",
   "Terms, data and cookies. Written to be understood on one read, without leaving out what the "
   "law requires. The Spanish version is the one that governs."),
 "encab-cotizador": ("Quote builder", "Let's build the number",
   "The price of each service, area by area, and a free 20-minute call to sort out where to start. "
   "It goes straight to our WhatsApp, no forms nobody reads."),
}
# textos de interfaz que viven en el guion
UI = {
 "es": {"verServ":"Ver los %d servicios","servElegido":"servicio elegido","servElegidos":"servicios elegidos",
        "tomarArea":"Tomar el área completa · −%d%%","quitarArea":"Quitar el área completa",
        "alternativa":"una alternativa, no se suman","servicio":"servicio","servicios":"servicios",
        "area":"área","areas":"áreas","completa":"completa","todas":"Todas",
        "sinMuestra":"sin muestra todavía","cotizarEsto":"Cotizar esto →","en":"en","para":"para",
        "nada":"Todavía no has elegido nada. Abre un área arriba y marca lo que necesitas.",
        "porAlcance":"por alcance","mes":"/mes","yaLoTienes":"Ya lo tienes","tomarPlan":"Tomar este plan",
        "falta":"Falta","areasN":"áreas","sumaAreas":"Sumando áreas","areaCompleta":"Área completa",
        "plan":"Plan","ahorro":"Ahorro por conectar","marcaDos":"Marca dos o más servicios para que los bloques compartan pared.",
        "razonBase":"Es un estimado sobre tarifas «desde». El número final sale de una conversación corta.",
        "razonSube":"Con %d áreas el descuento sube a %d%%. ","razonMensual":" La mensualidad va aparte y el descuento no la toca.",
        "razonArea":"Tomaste un área entera. <b>Baja un %d%%</b> porque se hace de una sola vez, con un brief y una entrega, en vez de por pedazos.",
        "razonConectar":"Un brief, un interlocutor, activos que se reutilizan. Por eso baja, no por rebaja.",
        "hola":"Hola LQS, quiero cotizar.","loQueNecesito":"Lo que necesito:","areaCompletaMsg":"(área completa)",
        "paraQuien":"Para: ","invInicial":"Inversión inicial estimada: ","mensualEst":"Mensualidad estimada: ",
        "descAplicado":"Descuento aplicado: ","sinCifra":"Por alcance (sin cifra): ",
        "noLoTengo":"Áreas: todavía no lo tengo claro","asuntoCot":"Cotización LQS",
        "seCotiza":"se cotiza por alcance: no entra en las cifras de arriba.",
        "seCotizanN":"se cotizan por alcance: no entran en las cifras de arriba.",
        "nadaEncontrado":"Hola LQS, busqué «%s» en el sitio y no encontré nada. ¿Lo hacen?",
        "autoriza":"Autorizo el tratamiento de mis datos personales conforme a la política publicada en %s y a la Ley 1581 de 2012. Fecha: %s.",
        "soy":"Hola LQS, soy %s.","contacto":"Contacto: ",
        "faltanTres":"Completa los tres campos para poder enviarlo.","faltaLegal":"Falta autorizar el tratamiento de datos.",
        "asuntoContacto":"Contacto desde el sitio — "},
 "en": {"verServ":"See the %d services","servElegido":"service picked","servElegidos":"services picked",
        "tomarArea":"Take the whole area · −%d%%","quitarArea":"Drop the whole area",
        "alternativa":"an alternative, they do not add up","servicio":"service","servicios":"services",
        "area":"area","areas":"areas","completa":"whole","todas":"All",
        "sinMuestra":"no sample yet","cotizarEsto":"Quote this →","en":"in","para":"for",
        "nada":"Nothing picked yet. Open an area above and tick what you need.",
        "porAlcance":"by scope","mes":"/mo","yaLoTienes":"You already have it","tomarPlan":"Take this plan",
        "falta":"Missing","areasN":"areas","sumaAreas":"Adding areas","areaCompleta":"Whole area",
        "plan":"Plan","ahorro":"Savings for connecting","marcaDos":"Pick two or more services so the blocks share a wall.",
        "razonBase":"This is an estimate on «from» rates. The final number comes out of a short conversation.",
        "razonSube":"With %d areas the discount rises to %d%%. ","razonMensual":" The monthly fee is separate and the discount does not touch it.",
        "razonArea":"You took a whole area. <b>It drops %d%%</b> because it is done in one go, with one brief and one delivery, instead of piece by piece.",
        "razonConectar":"One brief, one contact, assets that get reused. That is why it drops — it is not a markdown.",
        "hola":"Hi LQS, I would like a quote.","loQueNecesito":"What I need:","areaCompletaMsg":"(whole area)",
        "paraQuien":"For: ","invInicial":"Estimated initial investment: ","mensualEst":"Estimated monthly: ",
        "descAplicado":"Discount applied: ","sinCifra":"By scope (no figure): ",
        "noLoTengo":"Areas: I am not sure yet","asuntoCot":"LQS quote",
        "seCotiza":"is quoted by scope: it is not in the figures above.",
        "seCotizanN":"are quoted by scope: they are not in the figures above.",
        "nadaEncontrado":"Hi LQS, I searched for «%s» on your site and found nothing. Do you do it?",
        "autoriza":"I authorise the processing of my personal data under the policy published at %s and Colombian Law 1581 of 2012. Date: %s.",
        "soy":"Hi LQS, I am %s.","contacto":"Contact: ",
        "faltanTres":"Fill in the three fields to send it.","faltaLegal":"You still need to authorise data processing.",
        "asuntoContacto":"Contact from the site — "},
}
ESCALA = {"es": ["Emprendedor", "Empresa", "Evento"], "en": ["Solo / startup", "Company", "Event"]}

# --------------------------------------------------------------- páginas
PAGINAS = {
    "index.html": {
        "titulo": "LQS — El mejor amigo de tus ideas",
        "desc": ("El mejor amigo de tus ideas. LQS no es solo una agencia creativa: es una agencia "
                 "creativa modular. Siete areas independientes que se contratan solas y se conectan "
                 "entre si. Estamos donde nos necesiten."),
        "partes": ["hero", "problema", "rutas"],
    },
    "nosotros.html": {
        "titulo": "Quiénes somos — LQS",
        "desc": ("No solo una agencia creativa: una agencia creativa modular. Por que existe LQS, "
                 "como trabajamos y que hemos hecho."),
        "partes": ["nosotros", "areas-bento", "trabajamos", "casos"],
    },
    "muestras.html": {
        "titulo": "Muestras — LQS",
        "desc": ("Lo que hemos hecho, por area: video, foto, marca, redes, digital, eventos, "
                 "automatizacion e ilustracion. Filtra por categoria y toca una muestra para abrirla."),
        "partes": ["encab-muestras", "areas", "antesdespues", "express"],
    },
    "legal.html": {
        "titulo": "Términos, datos y cookies — LQS",
        "desc": ("Terminos y condiciones, politica de tratamiento de datos personales (Ley 1581 de 2012) "
                 "y politica de cookies de LQS. Este sitio no usa cookies."),
        "partes": ["encab-legal", "legal"],
    },
    "404.html": {
        "titulo": "Esto no existe — LQS",
        "desc": "La pagina que buscas no esta. Aca estan las que si.",
        "partes": ["error"],
    },
    "cotizador.html": {
        "titulo": "Cotizador — LQS",
        "desc": ("Los precios de cada área, servicio por servicio, y una asesoría gratis para "
                 "ordenar por dónde empezar. Llega directo a nuestro WhatsApp o correo."),
        "partes": ["encab-cotizador", "asesoria", "tarifas", "faqs", "contacto"],
    },
}

ENCABEZADOS = {
 "encab-nosotros": ("Quiénes somos", "Hacemos vivir tus ideas",
   "Una agencia creativa modular: toma el frente que necesitas hoy y suma los demás cuando quieras. El límite es tu imaginación."),
 "encab-muestras": ("Muestras", "Lo que hemos hecho",
   "Gíralo por área y elige una para desplegar sus muestras. Toca una para abrirla."),
 "encab-legal": ("Legal", "Lo legal, en español",
   "Términos, datos y cookies. Escrito para que se entienda leyéndolo una vez, sin dejar de decir "
   "lo que la ley obliga a decir."),
 "encab-cotizador": ("Cotizador", "Armemos el número",
   "El precio de cada servicio, área por área, y una asesoría gratis de 20 minutos para ordenar por "
   "dónde empezar. Llega directo a nuestro WhatsApp, sin formularios que nadie revisa."),
}

TICK = "✓"

# --------------------------------------------------------------- piezas
def fmt(n):
    return "$" + "{:,}".format(int(n)).replace(",", ".")

def tr_area(n, idi):
    return EN_AREAS[n][0] if idi == "en" else n

def tr_serv(s, idi):
    if idi != "en":
        return s
    d = dict(s)
    d["n"] = EN_SERV.get(s["n"], s["n"])
    d["u"] = EN_UNIDAD.get(s["u"], s["u"]) if s["u"] else ""
    return d

def modulos_idioma(idi):
    """MODULOS con nombres, descripciones y unidades en el idioma pedido."""
    out = []
    for n, ico, color, desc, servs in MODULOS:
        nn, dd = (EN_AREAS[n] if idi == "en" else (n, desc))
        out.append((nn, ico, color, dd, [tr_serv(s, idi) for s in servs]))
    return out

def tarjeta(m, idi):
    nombre, ico, color, desc, servicios = m
    U = UI[idi]
    # el «desde» del área no lo marca un precio por unidad (un retoque suelto no es un proyecto)
    unit = ("por ", "per ")
    con_precio = [s for s in servicios if s["p"] and not s["u"].startswith(unit)]
    if not con_precio:
        con_precio = [s for s in servicios if s["p"]]
    minimo = min(s["p"] for s in con_precio) if con_precio else 0
    mensual_min = [s for s in con_precio if s["p"] == minimo][0]["m"] if con_precio else False
    desde = "desde " if idi == "es" else "from "
    precio = (desde + fmt(minimo) + (" " + U["mes"] if mensual_min else "")) if minimo else U["porAlcance"]
    items = "".join(
        '<button class="serv" type="button" data-area="%s" data-i="%d" aria-pressed="false">'
        '<span class="serv-tick" aria-hidden="true">%s</span>'
        '<span class="serv-txt">%s%s</span>'
        '<span class="serv-p mono">%s</span></button>'
        % (nombre, j, TICK, s["n"],
           ('<em class="serv-u">%s</em>' % (s["u"] or U["alternativa"])) if (s["u"] or s["g"]) else "",
           (fmt(s["p"]) + (" " + U["mes"] if s["m"] else "")) if s["p"] else U["porAlcance"])
        for j, s in enumerate(servicios))
    return ('<article class="mod apila" data-area="%s" style="--sf:%s">'
            '<div class="mod-cab">'
            '<span class="mod-top"><span class="ico" data-ico="%s"></span></span>'
            '<span class="mod-name">%s</span>'
            '<span class="mod-desc">%s</span>'
            '<span class="mod-price">%s</span>'
            '<span class="check" aria-hidden="true">%s</span></div>'
            '<button class="mod-abrir" type="button" aria-expanded="false" aria-controls="serv-%s">'
            '<span>%s</span><span class="mod-flecha" aria-hidden="true">+</span></button>'
            '<div class="mod-lista" id="serv-%s" hidden>%s'
            '</div></article>'
            % (nombre, color, ico, nombre, desc, precio, TICK,
               ico, U["verServ"] % len(servicios), ico, items))

def encabezado(clave, idi):
    eyebrow, titulo, bajada = (EN_ENCAB if idi == "en" else ENCABEZADOS)[clave]
    return ('<section class="seccion pagina-encab">'
            '<div class="eyebrow">%s</div>'
            '<h1 class="tit-pagina">%s</h1>'
            '<p class="dim bajada">%s</p>'
            '</section>' % (eyebrow, titulo, bajada))

def areas_bento(idi):
    """Bento colorido de las áreas para Nosotros: los montones de colores de la
       marca, uno por área + Express. Sin interacción pesada: muestra el ADN
       modular y de color. Tamaños variados para que se sienta bento."""
    # El logo de LQS va al centro exacto (grid-area:lqs, 2×2) y las áreas lo rodean
    # con tamaños variados hasta completar el cuadrado. La posición de cada cubo la
    # fija `grid-template-areas` en el CSS, no el orden del DOM. Cada cubo lleva su
    # ícono enorme, cortado y translúcido, como fondo: da profundidad y viveza.
    grandes = {"video", "marca", "eventos"}   # ocupan 2 celdas, texto más grande
    lema = "El mejor amigo de tus ideas" if idi == "es" else "Your ideas' best friend"
    logo_tile = ('<div class="ab-tile ab-lqs" style="grid-area:lqs">'
                 '<lqs-trazo class="ab-lqs-logo" tam="116" cuando="visible" '
                 'fondo="#FDFBF7" trazo="#8B3DF0" duracion="2400">'
                 '<img src="{{RAIZ}}marca/lqs-principal.svg" alt="LQS" '
                 'width="116" height="116"></lqs-trazo>'
                 '<span class="ab-tx"><span class="ab-n">LQS</span>'
                 '<span class="ab-d">%s</span></span></div>' % lema)
    tiles = [logo_tile]
    i = 0
    for n_es, ico, color_mod, desc_es, servs in MODULOS:
        color = AREA_TONO.get(ico, color_mod)
        nom = EN_AREAS[n_es][0] if idi == "en" else n_es
        desc = EN_AREAS[n_es][1] if idi == "en" else desc_es
        cls = " ab-grande" if ico in grandes else ""
        tiles.append('<div class="ab-tile%s" style="--c:%s;--i:%d;grid-area:%s">'
                     '<span class="ab-marca ico" data-ico="%s" aria-hidden="true"></span>'
                     '<span class="ab-ico ico" data-ico="%s"></span>'
                     '<span class="ab-tx"><span class="ab-n">%s</span>'
                     '<span class="ab-d">%s</span></span></div>'
                     % (cls, color, i, ico, ico, ico, nom, desc))
        i += 1
    exd = "Lo urgente, el mismo día" if idi == "es" else "The urgent stuff, same day"
    tiles.append('<div class="ab-tile ab-xp" style="--c:#F4D000;--i:%d;grid-area:expr">'
                 '<span class="ab-marca ico" data-ico="reloj" aria-hidden="true"></span>'
                 '<span class="ab-ico ico" data-ico="reloj"></span>'
                 '<span class="ab-tx"><span class="ab-n">Express</span>'
                 '<span class="ab-d">%s</span></span></div>' % (i, exd))
    return '<div class="ab-rej">%s</div>' % "".join(tiles)

logo = (P.parent / "carita-inline.svg")
if not logo.exists():
    logo = P.parent.parent / "maqueta" / "carita-inline.svg"
logo = logo.read_text(encoding="utf-8")
logo = re.sub(r'\s(width|height)="[^"]*"', '', logo, count=2)
if 'style=' not in logo.split('>')[0]:
    logo = logo.replace('<svg', '<svg style="width:100%;height:100%;display:block"', 1)

cab = (BASE / "cab.html").read_text(encoding="utf-8")

def armar(idi):
    carpeta = P if idi == "es" else (BASE / "partes-en")
    mods_i = modulos_idioma(idi)
    U = UI[idi]
    mods = "\n".join(tarjeta(m, idi) for m in mods_i)
    mas = (('<span class="mod-name">¿No ves lo tuyo?</span>'
            '<p class="mod-desc">Estas listas son lo que más nos piden, no un catálogo cerrado. '
            'Si lo que necesitas no aparece, escríbenos y lo miramos.</p>'
            '<a class="btn ghost sm" href="https://wa.me/{{WHATSAPP}}?text='
            'Hola%20LQS%2C%20necesito%20algo%20que%20no%20est%C3%A1%20en%20la%20lista%3A">'
            'Preguntar por WhatsApp</a>')
           if idi == "es" else
           ('<span class="mod-name">Not seeing yours?</span>'
            '<p class="mod-desc">These lists are what we get asked for most, not a closed catalogue. '
            'If what you need is not there, write to us and we will look at it.</p>'
            '<a class="btn ghost sm" href="https://wa.me/{{WHATSAPP}}?text='
            'Hi%20LQS%2C%20I%20need%20something%20that%20is%20not%20on%20the%20list%3A">'
            'Ask on WhatsApp</a>'))
    mods += '\n<div class="mod-mas apila">' + mas + '</div>'

    ap = EN_APERTURA if idi == "en" else APERTURA
    pedido = "a pedido" if idi == "es" else "on request"
    apert = "\n".join('<div class="apertura"><span class="mod-name">%s</span>'
                      '<span class="mod-desc">%s</span><span class="mod-price">%s</span></div>'
                      % (n, d, pedido) for n, d in ap)
    expr = "".join('<span class="ex-item">%s</span>' % e
                   for e in (EN_EXPRESS if idi == "en" else EXPRESS))

    # Exploración por área en Muestras: una tarjeta <details> por área, con su
    # color e icono. Van en acordeón (name=) para que solo una esté abierta a la
    # vez —así, cuando haya muestras pesadas, no se despliegan todas juntas—.
    # Dentro, cada servicio es un «cuadro»: al tocarlo abre una ventana flotante
    # que crece desde el cuadro (la lógica vive en partes/areas.html). Los datos
    # de cada cuadro (qué es, recomendación de uso) salen en {{FICHAS}} como JSON.
    FICHA_I = EN_FICHA if idi == "en" else FICHA
    def areas_explora():
        fichas = []
        es = idi == "es"
        def precio_corto(p, m):
            return (fmt(p) + (" " + U["mes"] if m else "")) if p else U["porAlcance"]

        def ficha_demo(nombre_es):
            d = DEMOS.get(nombre_es)
            if not d:
                return None
            return {"arch": "{{RAIZ}}demos/" + d[0], "img": "{{RAIZ}}demos/" + d[1],
                    "tono": d[2], "marca": d[3]}

        # Galería de la ficha: lista de media (imagen/video) ya con ruta e idioma
        # resueltos, más el enlace «ver» (p.ej. el PDF) y la portada de la tarjeta.
        def ficha_media(nombre_es):
            g = GALERIA.get(nombre_es)
            if not g:
                return [], None, None
            items = []
            for m in g["media"]:
                it = {"t": m["t"], "src": "{{RAIZ}}demos/" + m["src"]}
                if m.get("poster"):
                    it["poster"] = "{{RAIZ}}demos/" + m["poster"]
                if m.get("href"):   # imagen que abre una página en vivo (blog, portafolio)
                    it["href"] = "{{RAIZ}}demos/" + m["href"]
                if m.get("ar"):
                    it["ar"] = m["ar"]
                cap = m.get("cap")
                if cap:
                    it["cap"] = cap[1] if idi == "en" else cap[0]
                items.append(it)
            ver = None
            if g.get("ver"):
                v = g["ver"]
                ver = {"href": "{{RAIZ}}demos/" + v["href"],
                       "lbl": v["lbl"][1] if idi == "en" else v["lbl"][0]}
            cover = ("{{RAIZ}}demos/" + g["cover"]) if g.get("cover") else None
            return items, ver, cover

        # Campos del bloque de precio de la ficha: separa lo que al cliente le
        # importa —cuánto y de qué tipo—. Cuatro tipos: pago único (proyecto),
        # plan mensual (continuo), por alcance (se cotiza) y a pedido (Express).
        def modal_campos(p, m, express=False):
            if express:
                return {"pnum": "A pedido" if es else "On request", "mes": "", "tag": "",
                        "nota": "Sin cotizador · mismo día." if es else "No quote · same-day.",
                        "plan": False, "cta": "Pedir por WhatsApp →" if es else "Ask on WhatsApp →"}
            if not p:
                return {"pnum": "Por alcance" if es else "By scope", "mes": "", "tag": "",
                        "nota": "Se cotiza según lo que necesites." if es else "Quoted to fit your need.",
                        "plan": False, "cta": "Cotizar por WhatsApp →" if es else "Get a quote →"}
            if m:
                return {"pnum": fmt(p), "mes": "/mes" if es else "/mo",
                        "tag": "Plan mensual" if es else "Monthly plan",
                        "nota": "Continuo, mes a mes." if es else "Ongoing, month to month.",
                        "plan": True, "cta": "Empezar el plan →" if es else "Start the plan →"}
            return {"pnum": fmt(p), "mes": "", "tag": "Pago único" if es else "One-time",
                    "nota": "Un brief, una entrega." if es else "One brief, one delivery.",
                    "plan": False, "cta": "Cotizar por WhatsApp →" if es else "Get a quote →"}

        # Dos vistas sobre los mismos datos. Paseo: cada ÁREA es una carta de un
        # coverflow horizontal (profundidad 3D, la del centro al frente). Al elegir
        # un área, esa carta se despliega en una reja en zigzag con SUS muestras,
        # cada una con su nombre y un número grande de fondo. Tocar una muestra
        # abre la misma ventana flotante con precio y cotizar. El estado 3D y el
        # despliegue los pone el JS (partes/areas.html); sin JS el coverflow queda
        # como fila deslizable y las rejas visibles —se lee igual—.
        sel_lab = "Selección" if es else "Selected"
        unidad_ct = ("muestra", "muestras") if es else ("sample", "samples")
        cue_lab = ("Desplegar" if es else "Open") + " →"

        def cf_card(idx, nom, ico, color, nserv):
            return ('<button class="cf-card" type="button" data-area="%d" style="--c:%s" '
                    'aria-label="%s">'
                    '<span class="cf-cover"><span class="cf-ico ico" data-ico="%s"></span>'
                    '<span class="cf-sel">%s</span></span>'
                    '<span class="cf-meta"><span class="cf-nom">%s</span>'
                    '<span class="cf-cnt">%d %s</span>'
                    '<span class="cf-cue">%s</span></span></button>'
                    % (idx, color, nom, ico, sel_lab, nom, nserv,
                       unidad_ct[0] if nserv == 1 else unidad_ct[1], cue_lab))

        def zz_cel(ficha_idx, nom, ico, color, cover_src, k):
            if cover_src:
                cover = ('<span class="zz-cover">'
                         '<img class="zz-img" src="%s" alt="" loading="lazy"></span>'
                         % cover_src)
            else:
                cover = ('<span class="zz-cover zz-ph">'
                         '<span class="zz-ico ico" data-ico="%s"></span></span>' % ico)
            return ('<button class="zz-cel" type="button" data-f="%d" style="--c:%s;--i:%d" '
                    'aria-label="%s">%s'
                    '<span class="zz-lado"><span class="zz-num" aria-hidden="true">%02d</span>'
                    '<span class="zz-nom">%s</span></span></button>'
                    % (ficha_idx, color, k, nom, cover, k, nom))

        volver = "← Áreas" if es else "← Areas"
        def zz_panel(idx, nom, desc, ico, color, celdas):
            return ('<section class="zz" data-panel="%d" style="--c:%s" hidden>'
                    '<header class="zz-head">'
                    '<button class="zz-volver" type="button">%s</button>'
                    '<div class="zz-tit"><span class="zz-chip ico" data-ico="%s"></span>'
                    '<h3>%s</h3></div><p class="zz-desc">%s</p></header>'
                    '<div class="zz-rej">%s</div></section>'
                    % (idx, color, volver, ico, nom, desc, "".join(celdas)))

        cf_cards, zz_panels, ai = [], [], 0
        for n_es, ico, color_mod, desc_es, servs_es in MODULOS:
            color = AREA_TONO.get(ico, color_mod)
            nom_a = EN_AREAS[n_es][0] if idi == "en" else n_es
            desc_a = EN_AREAS[n_es][1] if idi == "en" else desc_es
            celdas = []
            for k, s in enumerate(servs_es, 1):
                n_disp = EN_SERV.get(s["n"], s["n"]) if idi == "en" else s["n"]
                que, uso = FICHA_I.get(s["n"], ("", ""))
                demo = DEMOS.get(s["n"])
                media, ver, gcover = ficha_media(s["n"])
                f = {"n": n_disp, "area": nom_a, "ico": ico, "color": color,
                     "p": precio_corto(s["p"], s["m"]), "que": que, "uso": uso,
                     "demo": ficha_demo(s["n"]), "media": media}
                if ver:
                    f["ver"] = ver
                f.update(modal_campos(s["p"], s["m"]))
                fichas.append(f)
                # portada de la tarjeta: la demo manda; si no hay demo, la de la galería
                cover_src = ("{{RAIZ}}demos/" + demo[1]) if demo else gcover
                celdas.append(zz_cel(len(fichas) - 1, n_disp, ico, color, cover_src, k))
            cf_cards.append(cf_card(ai, nom_a, ico, color, len(servs_es)))
            zz_panels.append(zz_panel(ai, nom_a, desc_a, ico, color, celdas))
            ai += 1

        # Express: una carta más, de encargos inmediatos (sin cotizador).
        ex_src = EN_EXPRESS if idi == "en" else EXPRESS
        ex_desc = ("Encargos chicos, el mismo día. Se piden y se entregan, sin cotizador."
                   if es else "Small jobs, same day. Asked and delivered, no quote.")
        celdas = []
        for k, e_es in enumerate(EXPRESS, 1):
            que, uso = FICHA_I.get(e_es, ("", ""))
            f = {"n": ex_src[k - 1], "area": "Express", "ico": "reloj", "color": "#F4D000",
                 "p": "A pedido" if es else "On request", "que": que, "uso": uso, "demo": None, "media": []}
            f.update(modal_campos(None, False, express=True))
            fichas.append(f)
            celdas.append(zz_cel(len(fichas) - 1, ex_src[k - 1], "reloj", "#F4D000", None, k))
        cf_cards.append(cf_card(ai, "Express", "reloj", "#F4D000", len(EXPRESS)))
        zz_panels.append(zz_panel(ai, "Express", ex_desc, "reloj", "#F4D000", celdas))

        puntos = "".join('<button class="cf-punto" type="button" data-ir="%d" '
                         'aria-label="%s %d">%02d</button>' % (j, sel_lab, j + 1, j + 1)
                         for j in range(len(cf_cards)))
        head_r = (("Áreas (%d)" if es else "Areas (%d)") % len(cf_cards))
        nav_prev = "Anterior" if es else "Previous"
        nav_next = "Siguiente" if es else "Next"
        html = ('<div class="cf" aria-label="%s">'
                '<div class="cf-top"><span>%s</span><span>%s</span></div>'
                '<div class="cf-escena"><div class="cf-pista">%s</div></div>'
                '<div class="cf-barra">'
                '<button class="cf-nav cf-prev" type="button" aria-label="%s">&lsaquo;</button>'
                '<div class="cf-puntos">%s</div>'
                '<button class="cf-nav cf-next" type="button" aria-label="%s">&rsaquo;</button>'
                '</div></div>'
                '<div class="zz-wrap">%s</div>'
                % (("Muestras por área" if es else "Work by area"),
                   sel_lab, head_r, "".join(cf_cards),
                   nav_prev, puntos, nav_next, "".join(zz_panels)))
        return html, json.dumps(fichas, ensure_ascii=False)
    areas_html, fichas_json = areas_explora()
    ab_html = areas_bento(idi)

    datos = json.dumps([{"nombre": m[0], "ico": m[1], "color": m[2], "desc": m[3],
                         "serv": [{"n": s["n"], "p": s["p"], "m": s["m"], "u": s["u"], "g": s["g"]}
                                  for s in m[4]]} for m in mods_i], ensure_ascii=False)
    def parte(nombre):
        if nombre.startswith("encab-"):
            return encabezado(nombre, idi)
        t = (carpeta / (nombre + ".html")).read_text(encoding="utf-8")
        return (t.replace("{{MODULOS}}", mods).replace("{{APERTURA}}", apert)
                 .replace("{{EXPRESS}}", expr).replace("{{AREAS}}", areas_html)
                 .replace("{{FICHAS}}", fichas_json)
                 .replace("{{AREABENTO}}", ab_html))

    guion = ((BASE / "guion.html").read_text(encoding="utf-8")
             .replace("/*CARITA_JS*/", (BASE / "carita.js").read_text(encoding="utf-8"))
             .replace("/*ICONOS_JS*/", (BASE / "iconos.js").read_text(encoding="utf-8"))
             .replace("{{DATOS}}", datos)
             .replace("{{LOGO}}", json.dumps(logo))
             .replace("{{CONTACTO}}", json.dumps(CONTACTO, ensure_ascii=False))
             .replace("{{ESCALERA}}", "[]")       # descuentos retirados: datos vacíos
             .replace("{{PLANES}}", "[]")         # (el cotizador ya no calcula ni descuenta)
             .replace("{{RECOMENDADO}}", '""')
             .replace("{{AREACOMPLETA}}", "0")
             .replace("{{UI}}", json.dumps(U, ensure_ascii=False))
             .replace("{{IDIOMA}}", json.dumps(idi)))

    salida = BASE / "dist" / ("" if idi == "es" else "en")
    salida.mkdir(parents=True, exist_ok=True)
    nav, pie = parte("nav"), parte("footer")
    for archivo, cfg in PAGINAS.items():
        titulo, desc = (EN_PAGINAS[archivo] if idi == "en" else (cfg["titulo"], cfg["desc"]))
        cuerpo = "\n\n".join(parte(p) for p in cfg["partes"])
        activa = archivo.replace(".html", "")
        html = (cab.replace("<title>LQS — El mejor amigo de tus ideas</title>",
                            "<title>%s</title>" % titulo)
                + "\n" + nav.replace('data-pag="%s"' % activa,
                                     'data-pag="%s" aria-current="page"' % activa)
                + '\n<main class="wrap" id="inicio" data-pagina="%s">\n' % activa
                + cuerpo + "\n</main>\n" + pie
                # El trazo: SVG + JS sin dependencias. Va antes del guión
                # porque define el custom element que el HTML ya usa.
                + '\n<script src="{{RAIZ}}lqs-trazo.js"></script>\n'
                + guion)
        for k, v in LEGAL.items():
            html = html.replace("{{%s}}" % k, v)
        html = (html.replace("{{CORREO}}", CONTACTO["correo"])
                    .replace("{{WHATSAPP}}", CONTACTO["whatsapp"])
                    .replace("{{TEL}}", CONTACTO["tel_visible"])
                    .replace("{{OTRO}}", ("en/" + archivo) if idi == "es" else ("../" + archivo))
                    .replace("{{RAIZ}}", "" if idi == "es" else "../"))
        (salida / archivo).write_text(html, encoding="utf-8")
        print("  %-3s %-16s %7d bytes" % (idi, archivo, len(html)))
    return {a: (EN_PAGINAS[a][1] if idi == "en" else c["desc"]) for a, c in PAGINAS.items()}

DESCS = {"es": armar("es"), "en": armar("en")}
print("ok")
