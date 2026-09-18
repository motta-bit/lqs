import pathlib, json, re

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
EXPRESS = ["Panfletos", "Presentaciones", "Edición de fotos", "Arreglos de costura"]

# Datos que la ley exige y que hay que llenar antes de publicar la página legal.
# Lo que quede con FALTA sale marcado en rojo en la página y publicar.py avisa.
FALTA = '<mark class="falta">FALTA: %s</mark>'
LEGAL = {
    "RAZON":       FALTA % "razón social o nombre completo",
    "NIT":         FALTA % "NIT o cédula",
    "DOMICILIO":   FALTA % "ciudad de domicilio",
    "DIRECCION":   FALTA % "dirección de notificaciones",
    "RESPONSABLE": FALTA % "quién atiende las solicitudes de datos",
    "VIGENCIA":    "17 de septiembre de 2026",
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
EN_EXPRESS = ["Flyers", "Presentations", "Photo editing", "Sewing repairs"]
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
        "partes": ["encab-muestras", "galeria", "antesdespues", "express"],
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
        return t.replace("{{MODULOS}}", mods).replace("{{APERTURA}}", apert).replace("{{EXPRESS}}", expr)

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
                + cuerpo + "\n</main>\n" + pie + "\n" + guion)
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
