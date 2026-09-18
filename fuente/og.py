import pathlib, re
from playwright.sync_api import sync_playwright
logo = pathlib.Path("/home/claude/lqs/repo/favicon.svg").read_text()
logo = logo.replace('fill="#1A1720"', 'fill="currentColor"')
page = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Syne:wght@800&family=IBM+Plex+Mono:wght@600&display=swap">
<style>
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;background:#FDFBF7;font-family:Syne,sans-serif;overflow:hidden}
.c{position:absolute;inset:8px;border-radius:40px;overflow:hidden;
   background:linear-gradient(140deg,#C4A8F5,#F7B2AB);color:#1A1720;padding:56px;
   display:flex;flex-direction:column;justify-content:space-between}
.c::after{content:"";position:absolute;inset:0;opacity:.3;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.55' numOctaves='5'/></filter><rect width='120' height='120' filter='url(%23n)' opacity='.55'/></svg>")}
.bola{position:absolute;right:-90px;top:-90px;width:380px;height:380px;border-radius:50%;background:#F7D9A6;opacity:.72}
.cuad{position:absolute;right:270px;bottom:-80px;width:170px;height:170px;background:#2563EB;opacity:.5;transform:rotate(18deg)}
.m{display:flex;align-items:center;gap:14px;position:relative;z-index:2}
.m .g{width:62px;height:62px;color:#1A1720}
.m span{font-size:40px;font-weight:800;letter-spacing:-.03em}
h1{position:relative;z-index:2;font-size:188px;line-height:.78;letter-spacing:-.05em;font-weight:800}
.lema{position:relative;z-index:2;font-size:52px;font-weight:800;letter-spacing:-.03em;line-height:1;margin-top:30px}
.p{position:relative;z-index:2;font-family:'IBM Plex Mono',monospace;font-size:19px;
   font-weight:600;letter-spacing:.2em;text-transform:uppercase}
.fila{position:absolute;right:56px;bottom:56px;display:grid;grid-template-columns:repeat(3,46px);gap:3px;z-index:2}
.fila i{height:46px;display:block}
</style>
<div class="c">
  <div class="bola"></div><div class="cuad"></div>
  <div class="m"><span class="g">LOGO_AQUI</span></div>
  <div><h1>LQS</h1><div class="lema">El mejor amigo de tus ideas</div></div>
  <div class="p">Agencia creativa modular &middot; Estamos donde nos necesiten</div>
  <div class="fila">
    <i style="background:#C4A8F5"></i><i style="background:#A8CBF5"></i><i style="background:#BFE0A8"></i>
    <i style="background:#F7D9A6"></i><i style="background:#F7B2AB"></i><i style="background:#F5F2EC"></i>
  </div>
</div>"""
page = page.replace("LOGO_AQUI", logo)
pathlib.Path("og.html").write_text(page)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width":1200,"height":630})
    pg.goto("file:///home/claude/lqs/sitio/og.html", wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(1500)
    pg.screenshot(path="/home/claude/lqs/repo/og.png")
    b.close()
print("ok")
