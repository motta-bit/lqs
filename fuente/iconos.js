/* LQS · Íconos de módulo
   Siete íconos literales con un movimiento lento cada uno. Sin dependencias.
   Mismo idioma que las caritas: trazo 3.4, puntas redondas, hereda currentColor.

   Iconos.montar(nodo, "video");     // inserta el SVG en el nodo
   Iconos.html("video")              // devuelve el SVG como string
*/
(function (global) {
  "use strict";

  var CSS = [
    '.lqs-ico{display:block;width:100%;height:100%;overflow:visible}',
    '.lqs-ico .t{fill:none;stroke:currentColor;stroke-width:3.4;stroke-linecap:round;stroke-linejoin:round}',
    '.lqs-ico .s{fill:currentColor;stroke:none}',
    /* video · el play empuja hacia adelante */
    '@keyframes lqs-play{0%,100%{transform:translateX(0)}50%{transform:translateX(1.8px)}}',
    '.i-video .play{animation:lqs-play 3.4s ease-in-out infinite}',
    /* foto · el lente obtura */
    '@keyframes lqs-obtura{0%,54%,100%{transform:scale(1)}62%{transform:scale(.68)}70%{transform:scale(1)}}',
    '.i-foto .lente{animation:lqs-obtura 4.6s ease-in-out infinite;transform-origin:22px 25px;transform-box:fill-box}',
    /* marca · la etiqueta cuelga y se mece */
    '@keyframes lqs-colgar{0%,100%{transform:rotate(-4.5deg)}50%{transform:rotate(4.5deg)}}',
    '.i-marca .etiqueta{animation:lqs-colgar 5.4s ease-in-out infinite;transform-origin:32px 12px}',
    /* redes · una señal recorre la red */
    '@keyframes lqs-viaja{',
    '  0%{transform:translate(14.6px,14.9px);opacity:0}',
    '  10%{opacity:1}',
    '  44%{transform:translate(29.4px,18.1px)}',
    '  56%{transform:translate(30.6px,23.6px)}',
    '  90%{transform:translate(17.5px,31.6px);opacity:1}',
    '  100%{transform:translate(17.5px,31.6px);opacity:0}}',
    '.i-redes .viaja{animation:lqs-viaja 4.6s ease-in-out infinite}',
    /* web · el contenido carga */
    '@keyframes lqs-carga{0%,100%{transform:scaleX(.55)}45%,75%{transform:scaleX(1)}}',
    '.i-web .l1,.i-web .l2{animation:lqs-carga 4s ease-in-out infinite;transform-origin:11px 50%;transform-box:fill-box}',
    '.i-web .l2{animation-delay:.45s}',
    /* eventos · el foco barre */
    '@keyframes lqs-barrer{0%,100%{transform:rotate(-15deg)}50%{transform:rotate(15deg)}}',
    '.i-eventos .foco{animation:lqs-barrer 5.6s ease-in-out infinite;transform-origin:22px 8px}',
    /* automatización · el ciclo corre solo */
    '@keyframes lqs-gira{to{transform:rotate(360deg)}}',
    '.i-auto .anillo{animation:lqs-gira 12s linear infinite;transform-origin:22px 22px}',
    /* express · el reloj corre rápido, que es todo el argumento */
    '@keyframes lqs-minutero{to{transform:rotate(360deg)}}',
    '.i-reloj .minutero{animation:lqs-minutero 2.6s linear infinite;transform-origin:22px 22px}',
    '.i-reloj .horario{animation:lqs-minutero 31.2s linear infinite;transform-origin:22px 22px}',
    '@media (prefers-reduced-motion:reduce){.lqs-ico *{animation:none!important}}'
  ].join("\n");

  var SVG = {
    video:
      '<rect class="t" x="5" y="9" width="34" height="26" rx="7"/>' +
      '<path class="s play" d="M19 16.5 L29.5 22 L19 27.5 Z"/>',

    foto:
      '<path class="t" d="M16 13.2 V10.6 a2.2 2.2 0 0 1 2.2-2.2 h7.6 a2.2 2.2 0 0 1 2.2 2.2 V13.2"/>' +
      '<rect class="t" x="4" y="13.2" width="36" height="23.6" rx="7"/>' +
      '<g class="lente"><circle class="t" cx="22" cy="25" r="7"/></g>' +
      '<circle class="s" cx="33.4" cy="19.4" r="1.8"/>',

    marca:
      '<g class="etiqueta">' +
      '<path class="t" d="M25.2 5 H36.5 a2.5 2.5 0 0 1 2.5 2.5 V18.8 a3 3 0 0 1-.88 2.12 L23.6 35.97 a3 3 0 0 1-4.24 0 L8.03 24.64 a3 3 0 0 1 0-4.24 L23.08 5.88 A3 3 0 0 1 25.2 5 Z"/>' +
      '<circle class="s" cx="32" cy="12" r="2.7"/>' +
      '</g>',

    redes:
      '<path class="t" d="M14.8 15 L29.2 18"/>' +
      '<path class="t" d="M30.4 23.8 L17.7 31.4"/>' +
      '<circle class="t" cx="10.5" cy="13" r="4.6"/>' +
      '<circle class="t" cx="33.5" cy="20" r="4.6"/>' +
      '<circle class="t" cx="14" cy="34" r="4.6"/>' +
      '<circle class="s viaja" cx="0" cy="0" r="2.5"/>',

    web:
      '<rect class="t" x="4" y="8" width="36" height="28" rx="7"/>' +
      '<path class="t" d="M5.2 17 H38.8"/>' +
      '<circle class="s" cx="10.6" cy="12.6" r="1.7"/>' +
      '<circle class="s" cx="16.2" cy="12.6" r="1.7"/>' +
      '<path class="t l1" d="M11 24.6 H26"/>' +
      '<path class="t l2" d="M11 30.6 H32"/>',

    eventos:
      '<rect class="s" x="7" y="5.6" width="30" height="4.2" rx="2.1"/>' +
      '<g class="foco">' +
      '<path class="s" d="M18.4 19.6 L25.6 19.6 L33.4 37.6 L10.6 37.6 Z" opacity=".42"/>' +
      '<path class="t" d="M22 9.8 V12.4"/>' +
      '<path class="s" d="M16.2 12.4 h11.6 l-2.1 7.4 h-7.4 Z"/>' +
      '</g>',

    "automatizacion":
      '<circle class="t anillo" cx="22" cy="22" r="15.4" stroke-dasharray="5 6.4"/>' +
      '<path class="s" d="M25.6 10.4 L14.6 24.2 H20.6 L18.4 33.6 L29.4 19.8 H23.4 Z"/>',

    reloj:
      '<path class="t" d="M17 4.6 H27"/>' +
      '<circle class="t" cx="22" cy="22" r="15.4"/>' +
      '<path class="t" d="M22 6.6 V4.6"/>' +
      '<path class="t horario" d="M22 22 V15.4"/>' +
      '<path class="t minutero" d="M22 22 L29.4 22"/>' +
      '<circle class="s" cx="22" cy="22" r="2.2"/>'
  };

  var ALIAS = { "automatización": "automatizacion", auto: "automatizacion" };
  function clave(n) { n = String(n).toLowerCase(); return ALIAS[n] || n; }
  var CLASE = { automatizacion: "i-auto" };

  var puesto = false;
  function estilo() {
    if (puesto || typeof document === "undefined") return;
    var s = document.createElement("style");
    s.setAttribute("data-lqs", "iconos");
    s.textContent = CSS;
    document.head.appendChild(s);
    puesto = true;
  }

  function html(nombre) {
    var k = clave(nombre), cuerpo = SVG[k];
    if (!cuerpo) return "";
    var c = CLASE[k] || ("i-" + k);
    return '<svg class="lqs-ico ' + c + '" viewBox="0 0 44 44" fill="none" aria-hidden="true">' + cuerpo + "</svg>";
  }

  function montar(nodo, nombre) {
    if (!nodo) return null;
    estilo();
    nodo.innerHTML = html(nombre);
    return nodo.firstChild;
  }

  // monta todos los [data-ico] del documento
  function auto(raiz) {
    estilo();
    (raiz || document).querySelectorAll("[data-ico]").forEach(function (n) {
      n.innerHTML = html(n.getAttribute("data-ico"));
    });
  }

  global.Iconos = {
    html: html, montar: montar, auto: auto, CSS: CSS,
    NOMBRES: ["video", "foto", "marca", "redes", "web", "eventos", "automatizacion", "reloj"]
  };
})(window);
