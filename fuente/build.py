import pathlib, json, re

BASE = pathlib.Path(__file__).parent

# nombre, clave de ícono, superficie pastel, descripción, precio visible, precio numérico, mensual
MODULOS = [
 ("Video",          "video",          "#C4A8F5", "Reels, edición, color",        "desde $150.000",      150000, False),
 ("Foto",           "foto",           "#A8CBF5", "Sesiones, producto, retoque",  "desde $200.000",      200000, False),
 ("Marca",          "marca",          "#F7D9A6", "Identidad, manual, piezas",    "desde $400.000",      400000, False),
 ("Redes",          "redes",          "#BFE0A8", "Calendario, contenido, community", "desde $490.000 /mes", 490000, True),
 ("Web",            "web",            "#F7B2AB", "Sitios, plataformas",          "por alcance",         0,      False),
 ("Eventos",        "eventos",        "#C4A8F5", "Cobertura, montaje",           "desde $800.000",      800000, False),
 ("Automatización", "automatizacion", "#A8CBF5", "WhatsApp, cotizador, CRM",     "por alcance",         0,      False),
]
APERTURA = [("Música","Grabación, mezcla"),
            ("Producción física","Prototipo, corte láser"),
            ("Joyería","Diseño y 3D")]

TICK = "✓"

def tarjeta(m, i, ancho=False):
    nombre, ico, color, desc, precio, _, mensual = m
    pill = '<span class="pill">mensual</span>' if mensual else ''
    ih = '<span class="ico" data-ico="%s"></span>' % ico
    clase = "mod ancho apila" if ancho else "mod apila"
    if ancho:
        return ('<button class="%s" data-name="%s" style="--sf:%s">'
                '<span class="mod-top">%s</span>'
                '<span class="mod-txt"><span class="mod-name">%s</span><span class="mod-desc">%s</span></span>'
                '<span class="mod-price">%s%s</span>'
                '<span class="check" aria-hidden="true">%s</span></button>'
                % (clase, nombre, color, ih, nombre, desc, precio, pill, TICK))
    return ('<button class="%s" data-name="%s" style="--sf:%s">'
            '<span class="mod-top">%s%s</span>'
            '<span class="mod-name">%s</span>'
            '<span class="mod-desc">%s</span>'
            '<span class="mod-price">%s</span>'
            '<span class="check" aria-hidden="true">%s</span></button>'
            % (clase, nombre, color, ih, pill, nombre, desc, precio, TICK))

mods = "\n".join(tarjeta(m, i, ancho=(i == len(MODULOS) - 1)) for i, m in enumerate(MODULOS))
apert = "\n".join(
    '<div class="apertura"><span class="mod-name">%s</span>'
    '<span class="mod-desc">%s</span><span class="mod-price">a pedido</span></div>' % (n, d)
    for n, d in APERTURA)

datos = json.dumps([{"nombre": m[0], "ico": m[1], "precio": m[5], "mensual": m[6]}
                    for m in MODULOS], ensure_ascii=False)

# el logo real: el gato vectorizado, no la carita de interfaz
logo = (BASE / "carita-inline.svg").read_text(encoding="utf-8")
logo = re.sub(r'\s(width|height)="[^"]*"', '', logo, count=2)
if 'style=' not in logo.split('>')[0]:
    logo = logo.replace('<svg', '<svg style="width:100%;height:100%;display:block"', 1)

html = (BASE / "cab.html").read_text(encoding="utf-8")
html += (BASE / "cuerpo.html").read_text(encoding="utf-8").replace("{{MODULOS}}", mods).replace("{{APERTURA}}", apert)
html += ((BASE / "pie.html").read_text(encoding="utf-8")
         .replace("/*CARITA_JS*/", (BASE / "carita.js").read_text(encoding="utf-8"))
         .replace("/*ICONOS_JS*/", (BASE / "iconos.js").read_text(encoding="utf-8"))
         .replace("{{DATOS}}", datos)
         .replace("{{LOGO}}", json.dumps(logo)))

out = BASE / "lqs.html"
out.write_text(html, encoding="utf-8")
print("ok", len(html), "bytes")
