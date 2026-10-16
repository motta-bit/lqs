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
 ("Video", "video", "#C4A8F5", "Reels, YouTube, comerciales", [
   S("Reels y contenido vertical",                   150000, fuente="tarifario"),
   S("Entrevistas",                                  350000),
   S("Video para YouTube, acabado cinematográfico",  600000),
   S("Podcast: grabación y cortes",                  500000),
   S("Comerciales y piezas de publicidad",           700000),
 ]),
 ("Foto", "foto", "#A8CBF5", "Producto, publicidad, sesiones", [
   S("Retoque y edición",                             40000, unidad="por foto", fuente="tarifario"),
   S("Sesión a una persona",                         200000, unidad="45 min, 10 fotos", fuente="tarifario"),
   S("Foto de producto",                             250000),
   S("Foto para portafolio",                         300000),
   S("Foto para publicidad",                         400000),
   S("Sesión al equipo",                             400000),
 ]),
 ("Marca", "marca", "#F7D9A6", "Identidad, empaques, consultoría", [
   S("Solo el logo",                                 150000, grupo="identidad"),
   S("Diseño de accesorios de marca",                250000),
   S("Consultoría de ADN y orientación de marca",    300000),
   S("Empaques",                                     350000),
   S("Rediseño de una marca que ya existe",          650000, grupo="identidad"),
   S("Diseño de marca desde cero",                   750000, grupo="identidad"),
 ]),
 ("Redes", "redes", "#BFE0A8", "Contenido, calendario, community", [
   S("Publicaciones sueltas",                         40000, unidad="por pieza", fuente="tarifario", grupo="piezas"),
   S("Comercial corto para pauta",                   250000),
   S("Paquete de publicaciones",                     210000, unidad="6 piezas", grupo="piezas"),
   S("Respuesta de comentarios y mensajes",          290000, mensual=True),
   S("Social manager",                               650000, mensual=True, unidad="plan Base", fuente="tarifario", grupo="plan"),
   S("Plan mensual con calendario de publicación",  1290000, mensual=True, unidad="plan Activo", fuente="tarifario", grupo="plan"),
 ]),
 ("Digital", "web", "#F7B2AB", "Sitios, catálogos, menús", [
   S("Menú digital con código QR",                   450000),
   S("Landing para una campaña",                     600000),
   S("Blog",                                         700000),
   S("Portafolio web",                               900000),
   S("Catálogo en línea",                           1000000),
   S("Página web",                                  1300000),
 ]),
 ("Eventos", "eventos", "#C4A8F5", "Logística, registro, cobertura", [
   S("Diseño de accesorios del evento",              350000),
   S("Fondos y carruseles para conferencia",         250000),
   S("Registro y control de invitados",              600000, unidad="con contacto post evento"),
   S("Cobertura en foto y video",                    800000, fuente="tarifario"),
   S("Insta foto: la foto llega el mismo día",       800000),
   S("Logística completa del día",                  1800000),
 ]),
 ("Automatización", "automatizacion", "#A8CBF5", "WhatsApp, Instagram, seguimiento", [
   S("Reporte automático de números cada semana",    300000),
   S("WhatsApp Business: catálogo y respuestas",     350000),
   S("Solicitudes que llegan directo, sin bandeja",  400000),
   S("Respuestas automáticas en Instagram",          400000, unidad="mensajes y comentarios"),
   S("Agente de WhatsApp que responde y cotiza",    1550000, unidad="montaje"),
 ]),
]

APERTURA = [("Música","Grabación, mezcla"),
            ("Producción física","Prototipo, corte láser"),
            ("Joyería","Diseño y 3D")]

# --- descuentos ---------------------------------------------------------------
# A) escalera: cada área que entra baja más. B) planes armados. NO se acumulan: aplica la mayor.
ESCALERA = [(2, 8), (3, 14), (4, 20), (5, 25), (6, 30), (7, 35)]
PLANES = [
    ("Arranque",        ["Marca", "Foto"],              12, "Identidad y con qué mostrarla"),
    ("Presencia",       ["Marca", "Digital", "Redes"],  20, "La cara, la casa y quien la mantiene"),
    ("Evento completo", ["Eventos", "Foto", "Video"],   18, "Montaje, registro y cobertura"),
]
RECOMENDADO = "Presencia"
AREA_COMPLETA = 10   # tomar todos los servicios de una sola área

# Express: encargos chicos que no pasan por cotizador. Se piden y se entregan.
EXPRESS = ["Panfletos", "Carteles", "Avisos", "Presentaciones", "Edición de fotos", "Arreglos de costura"]

# Paquetes por sector: en Muestras, en vez de un buscador vacío, mostramos
# combos «starter» con los servicios más necesarios de cada sector, como
# recomendación para empezar. Cada servicio listado existe ya en MODULOS, así
# que el nombre coincide y el botón de WhatsApp lo nombra tal cual.
# (nombre, slug de icono, color propio, para quién, [servicios recomendados])
PAQUETES = [
 ("Artistas emergentes", "foto", "#E7B544",
  "Para mostrar tu obra y que se vea profesional desde el primer vistazo.",
  ["Foto para portafolio", "Portafolio web", "Reels y contenido vertical"]),
 ("Músicos emergentes", "video", "#EC6F6F",
  "Lo mínimo para sonar y verse como artista: imagen, video y presencia.",
  ["Sesión a una persona", "Reels y contenido vertical",
   "Diseño de accesorios de marca", "Paquete de publicaciones"]),
 ("Creadores de contenido", "redes", "#7C6BE6",
  "Para youtubers y bloggers: subir seguido, verse pro y tener casa propia.",
  ["Video para YouTube, acabado cinematográfico", "Reels y contenido vertical",
   "Sesión a una persona", "Blog"]),
 ("Marcas emergentes", "marca", "#58B6D8",
  "Nace con identidad, con qué venderte y con quién sostenga tus redes.",
  ["Diseño de marca desde cero", "Foto de producto", "Paquete de publicaciones"]),
 ("Transición digital para empresas", "automatizacion", "#4CB0A4",
  "Pasa tu operación a digital: presencia, orden y procesos que corren solos.",
  ["Página web", "WhatsApp Business: catálogo y respuestas",
   "Reporte automático de números cada semana", "Respuestas automáticas en Instagram"]),
]
EN_PAQUETES = {
 "Artistas emergentes": ("Emerging artists",
   "To show your work and have it look professional at first glance."),
 "Músicos emergentes": ("Emerging musicians",
   "The minimum to sound and look like an artist: image, video and presence."),
 "Creadores de contenido": ("Content creators",
   "For youtubers and bloggers: post often, look pro, and have a home of your own."),
 "Marcas emergentes": ("Emerging brands",
   "Born with identity, with something to sell you and someone to keep your social up."),
 "Transición digital para empresas": ("Digital transition for companies",
   "Move your operation to digital: presence, order and processes that run on their own."),
}

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
 "Catálogo en línea":          ("tienda-ropa.html",  "img/portadas/tienda.webp",      "#1b35ff", "Atelier Norte"),
 "Menú digital con código QR": ("restaurante.html",  "img/portadas/restaurante.webp", "#E0531C", "Rescoldo"),
 "Blog":                       ("revista-moda.html", "img/portadas/revista.webp",     "#7b5cff", "Tendido"),
 "Portafolio web":             ("mezcal.html",       "img/portadas/mezcal.webp",      "#C65A16", "Casa Tepemete"),
 # LQS mostrándose a sí misma, su video y su trabajo de redes para Vita Nova
 "Reels y contenido vertical": ("video-lqs.html",    "img/portadas/video.webp",       "#8B5CF6", "LQS"),
 "Diseño de marca desde cero": ("marca-lqs.html",    "img/portadas/marca.webp",       "#8B5CF6", "LQS"),
 "Publicaciones sueltas":      ("redes-lqs.html",    "img/portadas/redes.webp",       "#6D5AE6", "Vita Nova"),
 # Operación de un restaurante: parrilla + bots de WhatsApp/Instagram + reporte
 "WhatsApp Business: catálogo y respuestas": ("automatizacion.html", "img/portadas/automatizacion.webp", "#1f8a4c", "Turno"),
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
 "Social manager": ("Plan Base: alguien lleva tus redes de forma constante.",
   "Para cuando ya no te da la vida publicar; la constancia es lo que mueve la aguja."),
 "Plan mensual con calendario de publicación": ("Plan Activo: estrategia, calendario y producción cada mes.",
   "El paso completo: deja de pensar qué subir y enfócate en tu negocio."),
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
 "Social manager": ("Base plan: someone runs your social media consistently.",
   "For when you no longer have time to post; consistency is what moves the needle."),
 "Plan mensual con calendario de publicación": ("Active plan: strategy, calendar and production every month.",
   "The full step: stop thinking about what to post and focus on your business."),
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
  "Social manager": "Social manager",
  "Plan mensual con calendario de publicación": "Monthly plan with posting calendar",
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
}
EN_UNIDAD = {
  "por foto": "per photo", "45 min, 10 fotos": "45 min, 10 photos", "por pieza": "per piece",
  "6 piezas": "6 pieces", "plan Base": "Base plan", "plan Activo": "Active plan",
  "con contacto post evento": "with post-event follow-up", "montaje": "setup",
  "mensajes y comentarios": "messages and comments",
}
EN_APERTURA = [("Music", "Recording, mixing"),
               ("Physical production", "Prototype, laser cutting"),
               ("Jewellery", "Design and 3D")]
EN_EXPRESS = ["Flyers", "Posters", "Notices", "Presentations", "Photo editing", "Sewing repairs"]
EN_PLANES = {"Arranque": ("Starter", "Identity, and something to show it with"),
             "Presencia": ("Presence", "The face, the house, and whoever keeps it up"),
             "Evento completo": ("Full event", "Set-up, check-in and coverage")}
EN_PAGINAS = {
  "index.html": ("LQS — Your ideas' best friend",
    "Your ideas' best friend. LQS is not just a creative agency: it is a modular creative agency. "
    "Seven independent areas, hired on their own or connected. We are wherever we are needed."),
  "nosotros.html": ("Who we are — LQS",
    "Not just a creative agency: a modular creative agency. Why LQS exists and how we work."),
  "muestras.html": ("Work — LQS",
    "What we have done, by area. Filter by area or search for what you need."),
  "cotizador.html": ("Quote builder — LQS",
    "Pick service by service and the total builds itself. Each item priced, whole areas discounted."),
  "legal.html": ("Terms, data and cookies — LQS",
    "Terms of service, personal data policy (Colombian Law 1581 of 2012) and cookie policy. "
    "This site uses no cookies."),
  "404.html": ("This does not exist — LQS", "The page you are looking for is not here."),
}
EN_ENCAB = {
 "encab-nosotros": ("Who we are", "We are not just a creative agency",
   "We are a modular creative agency. Here is what that means, why LQS exists and how we work."),
 "encab-muestras": ("Work", "What we have done",
   "By area, filterable, with a search box for when you already know what you need."),
 "encab-legal": ("Legal", "The legal part, in plain words",
   "Terms, data and cookies. Written to be understood on one read, without leaving out what the "
   "law requires. The Spanish version is the one that governs."),
 "encab-cotizador": ("Quote builder", "Let us build the number",
   "Open an area, tick what you need and the total builds itself. Every service has its price; "
   "take a whole area and it drops. It goes straight to our WhatsApp."),
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
        "partes": ["encab-nosotros", "nosotros", "trabajamos", "casos"],
    },
    "muestras.html": {
        "titulo": "Muestras — LQS",
        "desc": ("Lo que hemos hecho, por area: video, foto, marca, redes, digital, eventos y "
                 "automatizacion. Se filtra por area y se busca por lo que necesites."),
        "partes": ["encab-muestras", "areas", "paquetes", "antesdespues", "express"],
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
        "desc": ("Elige servicio por servicio y el total se arma solo. Cada cosa con su precio, "
                 "el area completa con descuento. Llega directo a nuestro WhatsApp o correo."),
        "partes": ["encab-cotizador", "modulos", "descuentos", "ecosistema", "cotizador",
                   "asesoria", "tarifas", "faqs", "contacto"],
    },
}

ENCABEZADOS = {
 "encab-nosotros": ("Quiénes somos", "No somos solo una agencia creativa",
   "Somos una agencia creativa modular. Acá está qué significa eso, por qué existe LQS y cómo trabajamos."),
 "encab-muestras": ("Muestras", "Lo que hemos hecho",
   "Por área, filtrable, y con buscador para cuando ya sabes qué necesitas."),
 "encab-legal": ("Legal", "Lo legal, en español",
   "Términos, datos y cookies. Escrito para que se entienda leyéndolo una vez, sin dejar de decir "
   "lo que la ley obliga a decir."),
 "encab-cotizador": ("Cotizador", "Armemos el número",
   "Abre el área, marca lo que necesitas y el total se arma solo. Cada servicio tiene su precio; "
   "si tomas un área completa, baja. Llega directo a nuestro WhatsApp, sin formularios que nadie revisa."),
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
            '<button class="serv-todo" type="button" data-area="%s">%s</button>'
            '</div></article>'
            % (nombre, color, ico, nombre, desc, precio, TICK,
               ico, U["verServ"] % len(servicios), ico, items, nombre,
               U["tomarArea"] % AREA_COMPLETA))

def encabezado(clave, idi):
    eyebrow, titulo, bajada = (EN_ENCAB if idi == "en" else ENCABEZADOS)[clave]
    return ('<section class="seccion pagina-encab">'
            '<div class="eyebrow">%s</div>'
            '<h1 class="tit-pagina">%s</h1>'
            '<p class="dim bajada">%s</p>'
            '</section>' % (eyebrow, titulo, bajada))

def paquetes_html(idi):
    """Tarjetas de paquetes por sector para Muestras. El botón lleva a WhatsApp
       con el paquete y sus servicios ya escritos; {{WHATSAPP}} se reemplaza al final."""
    tag = "Starter" if idi == "es" else "Starter"
    cta = "Armar este paquete →" if idi == "es" else "Build this pack →"
    incluye = "Incluye" if idi == "es" else "Includes"
    out = []
    for nom_es, ico, color, para_es, servs in PAQUETES:
        nom = EN_PAQUETES[nom_es][0] if idi == "en" else nom_es
        para = EN_PAQUETES[nom_es][1] if idi == "en" else para_es
        servs_disp = [EN_SERV.get(s, s) if idi == "en" else s for s in servs]
        lis = "".join("<li>%s</li>" % s for s in servs_disp)
        txt = (("Hola LQS, me interesa el paquete «%s»: %s." % (nom, ", ".join(servs_disp)))
               if idi == "es" else
               ("Hi LQS, I'm interested in the «%s» pack: %s." % (nom, ", ".join(servs_disp))))
        href = "https://wa.me/{{WHATSAPP}}?text=" + quote(txt)
        out.append('<article class="paq" style="--c:%s">'
                   '<div class="paq-cab"><span class="paq-ico ico" data-ico="%s"></span>'
                   '<span class="paq-tag">%s</span></div>'
                   '<h3 class="paq-nom">%s</h3>'
                   '<p class="paq-para">%s</p>'
                   '<span class="paq-lab">%s</span>'
                   '<ul class="paq-serv">%s</ul>'
                   '<a class="btn sm paq-cta" href="%s">%s</a></article>'
                   % (color, ico, tag, nom, para, incluye, lis, href, cta))
    return '<div class="paq-rej">%s</div>' % "".join(out)

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
        def precio_corto(p, m):
            return (fmt(p) + (" " + U["mes"] if m else "")) if p else U["porAlcance"]
        def tarj(color, ico, nom, desc, cuadros, extra=""):
            return ('<details class="area-cd%s" name="muestras-area" style="--c:%s">'
                    '<summary><span class="area-ico ico" data-ico="%s"></span>'
                    '<span class="area-tx"><span class="area-nom">%s</span>'
                    '<span class="area-desc">%s</span></span>'
                    '<span class="area-mas" aria-hidden="true"></span></summary>'
                    '<div class="mstra-rej">%s</div></details>'
                    % (extra, color, ico, nom, desc, cuadros))
        envivo = "En vivo" if idi == "es" else "Live"
        ver_demo = "Ver muestra →" if idi == "es" else "See sample →"
        ver_serv = "Ver →" if idi == "es" else "View →"
        # Los cuadros forman un bento: el que tiene muestra en vivo ocupa 2×2
        # (tamaño destacado, con su portada de fondo); si un área no tiene demo,
        # el primer cuadro se ensancha para que no quede una rejilla plana.
        # Cada cuadro lleva un «Ver →» para que se note que se toca para abrirlo.
        def cuadro(nom_disp, precio, idx, demo=None, cls=""):
            extra = (" " + cls) if cls else ""
            foot = ('<span class="mstra-foot"><span class="mstra-p mono">%s</span>'
                    '<span class="mstra-ver">%s</span></span>'
                    % (precio, ver_demo if demo else ver_serv))
            if demo:
                arch, img, tono, marca = demo
                mini = ('<span class="mstra-mini" aria-hidden="true">'
                        '<img src="{{RAIZ}}demos/%s" alt="" loading="lazy"></span>' % img)
                badge = '<span class="mstra-badge">%s</span>' % envivo
                return ('<button class="mstra mstra-live%s" type="button" data-f="%d" '
                        'style="--t:%s">%s%s<span class="mstra-cap">'
                        '<span class="mstra-n">%s</span>%s</span></button>'
                        % (extra, idx, tono, mini, badge, nom_disp, foot))
            return ('<button class="mstra%s" type="button" data-f="%d">'
                    '<span class="mstra-mini" aria-hidden="true"></span>'
                    '<span class="mstra-cap"><span class="mstra-n">%s</span>%s</span></button>'
                    % (extra, idx, nom_disp, foot))

        def ficha_demo(nombre_es):
            d = DEMOS.get(nombre_es)
            if not d:
                return None
            return {"arch": "{{RAIZ}}demos/" + d[0], "img": "{{RAIZ}}demos/" + d[1],
                    "tono": d[2], "marca": d[3]}

        # Campos del bloque de precio de la ficha: separa lo que al cliente le
        # importa —cuánto y de qué tipo—. Cuatro tipos: pago único (proyecto),
        # plan mensual (continuo), por alcance (se cotiza) y a pedido (Express).
        es = idi == "es"
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

        cds = []
        for n_es, ico, color_mod, desc_es, servs_es in MODULOS:
            color = AREA_TONO.get(ico, color_mod)
            nom_a = EN_AREAS[n_es][0] if idi == "en" else n_es
            desc_a = EN_AREAS[n_es][1] if idi == "en" else desc_es
            hay_demo = any(s["n"] in DEMOS for s in servs_es)
            cuadros = []
            for k, s in enumerate(servs_es):
                n_disp = EN_SERV.get(s["n"], s["n"]) if idi == "en" else s["n"]
                que, uso = FICHA_I.get(s["n"], ("", ""))
                pc = precio_corto(s["p"], s["m"])
                demo = DEMOS.get(s["n"])
                f = {"n": n_disp, "area": nom_a, "ico": ico, "color": color,
                     "p": pc, "que": que, "uso": uso, "demo": ficha_demo(s["n"])}
                f.update(modal_campos(s["p"], s["m"]))
                fichas.append(f)
                # un área sin demo: el primer cuadro se ensancha, para dar ritmo
                cls = "mstra-wide" if (not hay_demo and k == 0) else ""
                cuadros.append(cuadro(n_disp, pc, len(fichas) - 1, demo, cls))
            cds.append(tarj(color, ico, nom_a, desc_a, "".join(cuadros)))
        # Express como una tarjeta más: encargos a pedido, sin cotizador.
        exd = ("Sin cotizador: se pide por WhatsApp y se entrega el mismo día."
               if idi == "es" else "No quote: ask on WhatsApp, same-day delivery.")
        ex_src = EN_EXPRESS if idi == "en" else EXPRESS
        expr_p = "A pedido" if idi == "es" else "On request"
        cuadros = []
        for j, e_es in enumerate(EXPRESS):
            que, uso = FICHA_I.get(e_es, ("", ""))
            f = {"n": ex_src[j], "area": "Express", "ico": "reloj",
                 "color": "#F4D000", "p": expr_p, "que": que, "uso": uso, "demo": None}
            f.update(modal_campos(None, False, express=True))
            fichas.append(f)
            cuadros.append(cuadro(ex_src[j], expr_p, len(fichas) - 1,
                                  cls="mstra-wide" if j == 0 else ""))
        cds.append(tarj("#F4D000", "reloj", "Express", exd, "".join(cuadros), extra=" area-xp"))
        return ('<div class="areas-rej">%s</div>' % "".join(cds),
                json.dumps(fichas, ensure_ascii=False))
    areas_html, fichas_json = areas_explora()
    paq_html = paquetes_html(idi)

    datos = json.dumps([{"nombre": m[0], "ico": m[1], "color": m[2], "desc": m[3],
                         "serv": [{"n": s["n"], "p": s["p"], "m": s["m"], "u": s["u"], "g": s["g"]}
                                  for s in m[4]]} for m in mods_i], ensure_ascii=False)
    planes = [{"n": (EN_PLANES[n][0] if idi == "en" else n),
               "a": [tr_area(x, idi) for x in a],
               "p": p_, "d": (EN_PLANES[n][1] if idi == "en" else d)} for n, a, p_, d in PLANES]
    recom = EN_PLANES[RECOMENDADO][0] if idi == "en" else RECOMENDADO

    def parte(nombre):
        if nombre.startswith("encab-"):
            return encabezado(nombre, idi)
        t = (carpeta / (nombre + ".html")).read_text(encoding="utf-8")
        return (t.replace("{{MODULOS}}", mods).replace("{{APERTURA}}", apert)
                 .replace("{{EXPRESS}}", expr).replace("{{AREAS}}", areas_html)
                 .replace("{{FICHAS}}", fichas_json).replace("{{PAQUETES}}", paq_html))

    guion = ((BASE / "guion.html").read_text(encoding="utf-8")
             .replace("/*CARITA_JS*/", (BASE / "carita.js").read_text(encoding="utf-8"))
             .replace("/*ICONOS_JS*/", (BASE / "iconos.js").read_text(encoding="utf-8"))
             .replace("{{DATOS}}", datos)
             .replace("{{LOGO}}", json.dumps(logo))
             .replace("{{CONTACTO}}", json.dumps(CONTACTO, ensure_ascii=False))
             .replace("{{ESCALERA}}", json.dumps(ESCALERA))
             .replace("{{PLANES}}", json.dumps(planes, ensure_ascii=False))
             .replace("{{RECOMENDADO}}", json.dumps(recom, ensure_ascii=False))
             .replace("{{AREACOMPLETA}}", str(AREA_COMPLETA))
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
