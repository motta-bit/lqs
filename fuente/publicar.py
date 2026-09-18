"""Arma las paginas finales del sitio: documento completo, metadatos y assets."""
import pathlib, subprocess, sys, re, shutil

BASE = pathlib.Path(__file__).parent
OUT  = BASE.parent / "repo"

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

# favicon a partir del gato vectorizado
logo = (BASE / "carita-inline.svg")
if not logo.exists():
    logo = BASE.parent / "maqueta" / "carita-inline.svg"
logo = logo.read_text(encoding="utf-8")
logo = re.sub(r'\s(width|height)="[^"]*"', '', logo, count=2)
if "xmlns" not in logo.split(">")[0]:
    logo = logo.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
logo = logo.replace('fill="currentColor"', 'fill="#1A1720"')
(OUT / "favicon.svg").write_text(logo, encoding="utf-8")
(OUT / ".nojekyll").write_text("", encoding="utf-8")
print("  favicon.svg y .nojekyll")

if faltan:
    pendientes = [k for k, v in LEGAL.items() if "FALTA:" in v]
    print()
    print("  " + "!" * 66)
    print("  !! La pagina legal sale con %d campo(s) sin llenar, marcados en rojo." % len(pendientes))
    print("  !! Faltan en LEGAL, arriba de build.py: " + ", ".join(pendientes))
    print("  !! Se puede publicar el resto del sitio, pero NO enlaces legal.html")
    print("  !! en una propuesta hasta llenarlos: la ley pide esos datos exactos.")
    print("  " + "!" * 66)
