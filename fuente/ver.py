from playwright.sync_api import sync_playwright
import sys, pathlib
paginas = ["index","nosotros","modulos","cotizador"]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    for n in paginas:
        pg=b.new_page(viewport={"width":1280,"height":900})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"file:///home/claude/lqs/sitio/dist/{n}.html",wait_until="domcontentloaded",timeout=60000)
        pg.wait_for_timeout(1400)
        print(f"{n:11s} errores={errs or 'ninguno'}  alto={pg.evaluate('()=>document.body.scrollHeight')}  "
              f"scrollW={pg.evaluate('()=>document.documentElement.scrollWidth')}  titulo={pg.title()[:40]}")
        pg.screenshot(path=f"p-{n}.png",full_page=True); pg.close()
    b.close()
