import pathlib, re, json

BASE = pathlib.Path(__file__).parent
OUT  = BASE.parent
OUT.mkdir(exist_ok=True)

# siempre reconstruye: editar lqs.html a mano se pierde
import subprocess, sys
subprocess.run([sys.executable, str(BASE / "build.py")], check=True, cwd=BASE)

html = (BASE / "lqs.html").read_text()

# 1. quitar la nota de armado (es interna, no va publicada)
html = re.sub(
    r'<!-- ={6,} NOTA DE ARMADO.*?</section>\s*(?=</main>)',
    '', html, flags=re.S)
assert "NOTA DE ARMADO" not in html, "la nota no se quito"

# 2. separar el <title>/<link>/<style> del cuerpo
i = html.index("</style>") + len("</style>")
cabeza, cuerpo = html[:i], html[i:]

DESC = ("El mejor amigo de tus ideas. LQS no es solo una agencia creativa: es una agencia creativa "
        "modular. Siete areas independientes que se contratan solas y se conectan entre si: "
        "video, foto, marca, redes, web, eventos y automatizacion. Estamos donde nos necesiten.")
URL  = "https://motta-bit.github.io/lqs/"

doc = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{DESC}">
<meta name="theme-color" content="#FDFBF7">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="canonical" href="{URL}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="LQS">
<meta property="og:title" content="LQS — El mejor amigo de tus ideas">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{URL}og.jpg">
<meta property="og:locale" content="es_CO">
<meta name="twitter:card" content="summary_large_image">
{cabeza}
</head>
<body>
{cuerpo}
</body>
</html>
"""
(OUT / "index.html").write_text(doc)

# 3. favicon a partir del gato vectorizado
logo = (BASE / "carita-inline.svg").read_text()
logo = re.sub(r'\s(width|height)="[^"]*"', '', logo, count=2)
logo = logo.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"', 1) if 'xmlns' not in logo.split('>')[0] else logo
logo = logo.replace('fill="currentColor"', 'fill="#1A1720"')
(OUT / "favicon.svg").write_text(logo)

(OUT / ".nojekyll").write_text("")
print("index.html", len(doc), "bytes")
