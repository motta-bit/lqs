"""Arma las paginas finales del sitio: documento completo, metadatos y assets."""
import pathlib, subprocess, sys, re, shutil

BASE = pathlib.Path(__file__).parent
# El sitio se publica EN LA RAIZ DEL PROPIO REPO: fuente/ vive dentro del
# checkout, asi que el destino es su carpeta madre. Antes decia
# BASE.parent/"repo", de cuando fuente/ estaba al lado del checkout y no
# dentro; con la carpeta renombrada a LQS-sitio eso creaba un LQS-sitio/repo/
# nuevo en cada publicacion y las paginas de verdad nunca se actualizaban.
OUT  = BASE.parent

subprocess.run([sys.executable, str(BASE / "build.py")], check=True, cwd=BASE)
sys.path.insert(0, str(BASE))
from build import PAGINAS, CONTACTO, LEGAL, DESCS, EN_PAGINAS   # noqa: E402

URL = "https://motta-bit.github.io/lqs/"
OUT.mkdir(parents=True, exist_ok=True)
faltan = 0

for idi in ("es", "en"):
  sub = "" if idi == "es" else "en/"
  (OUT / sub).mkdir(parents=True, exist_ok=True)
  for archivo, cfg in PAGINAS.items():
    html = (BASE / "dist" / sub / archivo).read_text(encoding="utf-8")
    i = html.index("</style>") + len("</style>")
    cabeza, cuerpo = html[:i], html[i:]
    canon = URL + sub + ("" if archivo == "index.html" else archivo)
    alterna = URL + (("en/" + archivo) if idi == "es" else archivo).replace("en/index.html", "en/")
    desc = DESCS[idi][archivo]
    # la 404 no se indexa ni se declara canonica: no es una pagina, es una respuesta
    es404 = archivo == "404.html"
    titulo = (EN_PAGINAS[archivo][0] if idi == "en" else cfg["titulo"])
    extra = ('<meta name="robots" content="noindex">'
             if es404 else f'<link rel="canonical" href="{canon}">')
    doc = f"""<!doctype html>
<html lang="{idi}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{desc}">
<meta name="theme-color" content="#FDFBF7">
<link rel="icon" href="{"../" if idi == "en" else ""}favicon.svg" type="image/svg+xml">
{extra}
<meta property="og:type" content="website">
<meta property="og:site_name" content="LQS">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{URL}og.jpg">
<meta property="og:locale" content="{'es_CO' if idi == 'es' else 'en_US'}">
<link rel="alternate" hreflang="{'es' if idi == 'es' else 'en'}" href="{canon}">
<link rel="alternate" hreflang="{'en' if idi == 'es' else 'es'}" href="{alterna}">
<link rel="alternate" hreflang="x-default" href="{URL}">
<meta name="twitter:card" content="summary_large_image">
{cabeza}
</head>
<body>
{cuerpo}
</body>
</html>
"""
    assert ".armado{" not in doc, "quedo CSS de la nota interna"
    if idi == "es":
        faltan += doc.count("FALTA:")
    (OUT / sub / archivo).write_text(doc, encoding="utf-8")
    print(f"  {idi} {archivo:16s} {len(doc):7d} bytes")

# El favicon se copia de marca/, que es donde vive el icono DISEÑADO:
# cuadrado, con el azulejo violeta y el monograma en papel.
#
# Antes se generaba a partir de carita-inline.svg, que es el monograma
# suelto: viewBox 1222x1238 —ni cuadrado ni con fondo—. Como el nombre del
# archivo no cambia, cada publicacion pisaba el favicon bueno con ese, y el
# cambio solo se notaba al abrir una pestaña nueva.
shutil.copy2(BASE.parent / "marca" / "favicon.svg", OUT / "favicon.svg")
(OUT / ".nojekyll").write_text("", encoding="utf-8")

# El custom element del trazo vive en fuente/ y se publica en la raiz,
# que es donde build.py lo enlaza ({{RAIZ}}lqs-trazo.js). Se copiaba a
# mano y por eso se quedaba viejo cuando cambiaba el original.
shutil.copy2(BASE / "lqs-trazo.js", OUT / "lqs-trazo.js")
print("  favicon.svg, .nojekyll y lqs-trazo.js")

if faltan:
    pendientes = [k for k, v in LEGAL.items() if "FALTA:" in v]
    print()
    print("  " + "!" * 66)
    print("  !! La pagina legal sale con %d campo(s) sin llenar, marcados en rojo." % len(pendientes))
    print("  !! Faltan en LEGAL, arriba de build.py: " + ", ".join(pendientes))
    print("  !! Se puede publicar el resto del sitio, pero NO enlaces legal.html")
    print("  !! en una propuesta hasta llenarlos: la ley pide esos datos exactos.")
    print("  " + "!" * 66)
