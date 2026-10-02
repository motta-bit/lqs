#!/usr/bin/env python3
"""
Las imagenes de preview (Open Graph), una por pagina.

Es lo que se ve cuando alguien manda el enlace por WhatsApp: el recuadro con
imagen, titulo y descripcion. El titulo y la descripcion ya cambiaban por
pagina; la imagen no, asi que las diez paginas se veian iguales al compartirlas.

    python3 fuente/og.py

Escribe og.jpg, og-nosotros.jpg, ... en la raiz del repo, y las inglesas en
en/. Las fuentes van incrustadas en base64: el contenedor no alcanza a Google
Fonts y un fallback silencioso arruina la composicion sin avisar.
"""

import base64, pathlib, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parent.parent
FUENTES = REPO.parent / "video" / "public" / "fonts"
SALIDA = pathlib.Path("/tmp/og-trabajo")

C = {
    "papel": "#FDFBF7", "crema": "#F5F2EC", "tinta": "#1A1720", "humo": "#4A4453",
    "violeta": "#8B3DF0", "azul": "#2563EB",
    "pVioleta": "#C4A8F5", "pAzul": "#A8CBF5", "pLima": "#BFE0A8",
    "pAmbar": "#F7D9A6", "pRojo": "#F7B2AB",
}

# Cada pagina con su campo de color: el preview se distingue de un vistazo
# aunque el texto se lea chico en la lista de un chat.
PAGINAS = [
    # archivo,        de,          a,           titulo,                 bajada
    ("og",            "pVioleta",  "pRojo",     "El mejor amigo\nde tus ideas",
     "Siete áreas que se contratan solas y se conectan entre sí"),
    ("og-nosotros",   "pAzul",     "pVioleta",  "Quiénes\nsomos",
     "Por qué existe LQS y cómo trabaja"),
    ("og-muestras",   "pLima",     "pAmbar",    "Muestras",
     "Video, foto, marca, redes, digital, eventos y automatización"),
    ("og-cotizador",  "pAmbar",    "pRojo",     "Cotizador",
     "Elige servicio por servicio y el total se arma solo"),
    ("og-legal",      "crema",     "pAzul",     "Términos\ny datos",
     "Ley 1581 de 2012 · privacidad y cookies"),
]

PAGINAS_EN = [
    ("og",            "pVioleta",  "pRojo",     "The best friend\nof your ideas",
     "Seven areas you can hire alone, that connect to each other"),
    ("og-nosotros",   "pAzul",     "pVioleta",  "About\nus",
     "Why LQS exists and how it works"),
    ("og-muestras",   "pLima",     "pAmbar",    "Work",
     "Video, photo, brand, social, digital, events and automation"),
    ("og-cotizador",  "pAmbar",    "pRojo",     "Quote\nbuilder",
     "Pick service by service and the total builds itself"),
    ("og-legal",      "crema",     "pAzul",     "Terms\nand data",
     "Colombian Law 1581 of 2012 · privacy and cookies"),
]


def incrustar(nombre, archivo, peso):
    """Una @font-face con el woff2 en base64. Sin red, sin fallback silencioso."""
    b = base64.b64encode((FUENTES / archivo).read_bytes()).decode()
    return (f"@font-face{{font-family:'{nombre}';font-weight:{peso};font-display:block;"
            f"src:url(data:font/woff2;base64,{b}) format('woff2')}}")


def marca_svg():
    """El monograma vigente: azulejo violeta con el trazo en papel.

    La og.jpg anterior llevaba la carita, que dejó de ser la marca el 27 de
    septiembre. La carita sigue viva como personaje dentro de la página, pero
    en el preview va el monograma.
    """
    def interior(p):
        s = (REPO / "marca" / p).read_text(encoding="utf-8")
        return s[s.index(">", s.index("<svg")) + 1: s.rindex("</svg>")]

    return (f'<svg viewBox="0 0 100 100" class="azulejo">'
            f'<g fill="{C["violeta"]}">{interior("lqs-azulejo-forma.svg")}</g>'
            f'<g fill="{C["papel"]}" fill-rule="evenodd">{interior("lqs-marca.svg")}</g></svg>')


def html(de, a, titulo, bajada):
    caras = "".join(
        f'<i style="background:{C[k]}"></i>'
        for k in ("pVioleta", "pAzul", "pLima", "pAmbar", "pRojo", "crema"))
    return f"""<style>
{incrustar("Syne", "Syne-800.woff2", 800)}
{incrustar("Rubik", "Rubik-500.woff2", 500)}
{incrustar("Plex", "PlexMono-500.woff2", 500)}
*{{box-sizing:border-box;margin:0}}
body{{width:1200px;height:630px;background:{C["papel"]};overflow:hidden}}
.c{{position:absolute;inset:8px;border-radius:40px;overflow:hidden;color:{C["tinta"]};
   padding:54px 56px;background:linear-gradient(140deg,{C[de]},{C[a]});
   display:flex;flex-direction:column;justify-content:space-between}}
/* El grano va en cada superficie de color: es regla del sistema. */
.c::after{{content:"";position:absolute;inset:0;opacity:.3;mix-blend-mode:overlay;pointer-events:none;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.55' numOctaves='5'/></filter><rect width='120' height='120' filter='url(%23n)' opacity='.55'/></svg>")}}
.bola{{position:absolute;right:-90px;top:-110px;width:360px;height:360px;border-radius:50%;
   background:{C["papel"]};opacity:.38}}
.cuad{{position:absolute;right:250px;bottom:-90px;width:170px;height:170px;
   background:{C["azul"]};opacity:.28;transform:rotate(18deg)}}
.m{{display:flex;align-items:center;gap:16px;position:relative;z-index:2}}
.azulejo{{width:64px;height:64px;display:block}}
.m span{{font-family:Syne,sans-serif;font-weight:800;font-size:38px;letter-spacing:-.03em}}
h1{{position:relative;z-index:2;font-family:Syne,sans-serif;font-weight:800;
   font-size:96px;line-height:.94;letter-spacing:-.04em;white-space:pre-line}}
.bajada{{position:relative;z-index:2;font-family:Rubik,sans-serif;font-weight:500;
   font-size:27px;line-height:1.3;margin-top:20px;max-width:760px;color:{C["humo"]}}}
.p{{position:relative;z-index:2;font-family:Plex,monospace;font-weight:500;
   font-size:18px;letter-spacing:.2em;text-transform:uppercase}}
.fila{{position:absolute;right:56px;bottom:54px;display:grid;
   grid-template-columns:repeat(3,44px);gap:3px;z-index:2}}
.fila i{{height:44px;display:block}}
</style>
<div class="c">
  <div class="bola"></div><div class="cuad"></div>
  <div class="m">{marca_svg()}<span>LQS</span></div>
  <div><h1>{titulo}</h1><div class="bajada">{bajada}</div></div>
  <div class="p">Agencia creativa modular</div>
  <div class="fila">{caras}</div>
</div>"""


def main():
    from playwright.sync_api import sync_playwright
    SALIDA.mkdir(exist_ok=True)
    trabajos = [(REPO, PAGINAS), (REPO / "en", PAGINAS_EN)]
    hechos = []

    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = nav.new_page(viewport={"width": 1200, "height": 630})
        for destino, lista in trabajos:
            for archivo, de, a, titulo, bajada in lista:
                tmp = SALIDA / f"{destino.name}-{archivo}.html"
                tmp.write_text(html(de, a, titulo, bajada), encoding="utf-8")
                pg.goto(tmp.as_uri(), wait_until="load")
                pg.wait_for_timeout(350)
                png = SALIDA / f"{destino.name}-{archivo}.png"
                pg.screenshot(path=str(png))
                salida = destino / f"{archivo}.jpg"
                # JPG con calidad 88: por debajo de 300 KB, que es lo que
                # WhatsApp y Facebook piden para mostrar el preview grande.
                subprocess.run(
                    [sys.executable, "-c",
                     f"from PIL import Image;Image.open({str(png)!r}).convert('RGB')"
                     f".save({str(salida)!r},'JPEG',quality=88,optimize=True,progressive=True)"],
                    check=True)
                hechos.append((salida.relative_to(REPO), salida.stat().st_size))
        nav.close()

    for ruta, peso in hechos:
        print(f"  {str(ruta):24} {peso/1024:6.1f} KB")
    print(f"\n{len(hechos)} imágenes")


if __name__ == "__main__":
    main()
