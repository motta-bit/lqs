/* LQS · Caritas
   Motor de gesticulación fluida. Sin dependencias.
   Sistema: 6 ojos × 6 bocas, trazo 3, ojos separados 0.28× Ø, sin cejas ni nariz ni mejillas.

   const c = new Carita(nodo, {gesto:"contenta", seguir:true});
   c.gesto("risa");            // cambia de gesto con resorte
   c.valor(72);                // 0–33 sorpresa · 34–99 guiño · 100 risa
*/
(function (global) {
  "use strict";

  var K = 0.5523;

  // ---- geometría: todo gesto es el mismo lazo de 4 cúbicas (24 números) ----
  function lazo(rx, ty, by, ay) {
    ay = ay || 0;
    var P0 = [rx, -ay], P1 = [0, by], P2 = [-rx, ay], P3 = [0, ty];
    function seg(A, B, vert) {
      return vert
        ? [[A[0], A[1] + K * (B[1] - A[1])], [B[0] + K * (A[0] - B[0]), B[1]]]
        : [[A[0] + K * (B[0] - A[0]), A[1]], [B[0], B[1] + K * (A[1] - B[1])]];
    }
    var s1 = seg(P0, P1, true), s2 = seg(P1, P2, false),
        s3 = seg(P2, P3, true), s4 = seg(P3, P0, false);
    return [].concat(P0, s1[0], s1[1], P1, s2[0], s2[1], P2, s3[0], s3[1], P3, s4[0], s4[1]);
  }

  function d(v) {
    return "M" + v[0] + "," + v[1] +
      "C" + v[2] + "," + v[3] + " " + v[4] + "," + v[5] + " " + v[6] + "," + v[7] +
      "C" + v[8] + "," + v[9] + " " + v[10] + "," + v[11] + " " + v[12] + "," + v[13] +
      "C" + v[14] + "," + v[15] + " " + v[16] + "," + v[17] + " " + v[18] + "," + v[19] +
      "C" + v[20] + "," + v[21] + " " + v[22] + "," + v[23] + " " + v[0] + "," + v[1] + "Z";
  }

  // ---- las seis piezas de cada tipo ----
  // los lazos casi cerrados (separación ~2.2) se leen como un solo trazo de 3;
  // los abiertos (abierto, risa, oh) se leen como aro o como boca llena.
  var OJOS = {
    punto:   lazo(1.6, -1.6, 1.6),
    abierto: lazo(7.0, -7.0, 7.0),
    feliz:   lazo(8.6, -6.0, -3.6),
    guino:   lazo(7.8, -4.0, -1.8),
    sueno:   lazo(8.8, 1.6, 3.8),
    ups:     lazo(0.4, -0.4, 0.4)
  };
  var BOCAS = {
    neutra:  lazo(10.0, -0.7, 0.7),
    sonrisa: lazo(11.0, 2.4, 5.0),
    risa:    lazo(12.0, -1.0, 11.0),
    oh:      lazo(6.0, -6.4, 6.4),
    mueca:   lazo(10.0, -0.7, 0.7, 3.4),
    lengua:  lazo(9.5, -1.0, 6.4)
  };

  // ---- gestos con nombre ----
  var GESTOS = {
    neutra:   { oi: "punto",   od: "punto",   b: "neutra",  relleno: 0, equis: 0, lengua: 0 },
    contenta: { oi: "feliz",   od: "feliz",   b: "sonrisa", relleno: 0, equis: 0, lengua: 0 },
    guino:    { oi: "abierto", od: "guino",   b: "sonrisa", relleno: 0, equis: 0, lengua: 0 },
    sorpresa: { oi: "abierto", od: "abierto", b: "oh",      relleno: 1, equis: 0, lengua: 0 },
    risa:     { oi: "feliz",   od: "feliz",   b: "risa",    relleno: 1, equis: 0, lengua: 0 },
    error:    { oi: "ups",     od: "ups",     b: "mueca",   relleno: 0, equis: 1, lengua: 0 },
    traviesa: { oi: "abierto", od: "guino",   b: "lengua",  relleno: 1, equis: 0, lengua: 1 },
    sueno:    { oi: "sueno",   od: "sueno",   b: "neutra",  relleno: 0, equis: 0, lengua: 0 }
  };

  var NS = "http://www.w3.org/2000/svg";
  function el(t, a) { var n = document.createElementNS(NS, t); for (var k in a) n.setAttribute(k, a[k]); return n; }

  // ---- resorte crítico con un pelo de rebote ----
  function Resorte(v, rigidez, amort) {
    this.x = v; this.meta = v; this.v = 0;
    this.k = rigidez || 170; this.c = amort || 20;
  }
  Resorte.prototype.paso = function (dt) {
    var a = this.k * (this.meta - this.x) - this.c * this.v;
    this.v += a * dt; this.x += this.v * dt;
    if (Math.abs(this.meta - this.x) < 0.0004 && Math.abs(this.v) < 0.0004) { this.x = this.meta; this.v = 0; }
    return this.x;
  };
  Resorte.prototype.saltar = function () { this.x = this.meta; this.v = 0; };

  function banco(vals, k, c) { return vals.map(function (v) { return new Resorte(v, k, c); }); }
  function metas(b, vals) { for (var i = 0; i < b.length; i++) b[i].meta = vals[i]; }
  function leer(b, dt) { var o = new Array(b.length); for (var i = 0; i < b.length; i++) o[i] = Math.round(b[i].paso(dt) * 100) / 100; return o; }

  var quietos = global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function Carita(nodo, opts) {
    opts = opts || {};
    this.nodo = nodo;
    this.seguir = opts.seguir !== false;
    this.respira = opts.respira !== false && !quietos;
    this.parpadea = opts.parpadear !== false && !quietos;
    this.aro = opts.aro !== false;

    var svg = el("svg", { viewBox: "0 0 100 100", fill: "none", "aria-hidden": "true" });
    svg.style.cssText = "width:100%;height:100%;display:block;overflow:visible";
    var g = el("g", {});                       // respiración + inclinación
    var cara = el("g", {});                    // rasgos (parallax)
    this.g = g; this.cara = cara;

    var trazo = { stroke: "currentColor", "stroke-width": 3, "stroke-linecap": "round", "stroke-linejoin": "round", fill: "none" };
    if (this.aro) g.appendChild(el("circle", Object.assign({ cx: 50, cy: 50, r: 44 }, trazo)));

    this.gOI = el("g", {}); this.gOD = el("g", {});
    this.pOI = el("path", trazo); this.pOD = el("path", trazo);
    this.gOI.appendChild(this.pOI); this.gOD.appendChild(this.pOD);

    // capa X (gesto "ups") — se funde mientras el lazo se cierra
    this.xOI = el("g", Object.assign({ opacity: 0 }, trazo));
    this.xOD = el("g", Object.assign({ opacity: 0 }, trazo));
    [this.xOI, this.xOD].forEach(function (gx) {
      gx.appendChild(el("path", { d: "M-6,-6 L6,6" }));
      gx.appendChild(el("path", { d: "M6,-6 L-6,6" }));
    });
    this.gOI.appendChild(this.xOI); this.gOD.appendChild(this.xOD);
    this.gOI.setAttribute("transform", "translate(36,43)");
    this.gOD.setAttribute("transform", "translate(64,43)");

    this.gB = el("g", { transform: "translate(50,64)" });
    this.lengua = el("path", { d: "M-4.8,0 C-4.8,10 4.8,10 4.8,0 Z", fill: "currentColor", opacity: 0 });
    this.pB = el("path", trazo);
    this.gB.appendChild(this.lengua); this.gB.appendChild(this.pB);

    cara.appendChild(this.gOI); cara.appendChild(this.gOD); cara.appendChild(this.gB);
    g.appendChild(cara); svg.appendChild(g);
    nodo.appendChild(svg);
    this.svg = svg;

    var g0 = GESTOS[opts.gesto] || GESTOS.contenta;
    this.bOI = banco(OJOS[g0.oi], 210, 22);
    this.bOD = banco(OJOS[g0.od], 210, 22);
    this.bB = banco(BOCAS[g0.b], 190, 21);
    this.rell = new Resorte(g0.relleno, 150, 22);
    this.req = new Resorte(g0.equis, 150, 22);
    this.rlen = new Resorte(g0.lengua, 150, 18);
    this.abierto = { i: alto(g0.oi), d: alto(g0.od) };
    this.pulso = new Resorte(1, 260, 16);
    this.px = new Resorte(0, 120, 20); this.py = new Resorte(0, 120, 20);

    this.t = 0; this.prox = 1.4 + Math.random() * 3; this.blink = 1; this.bfase = -1;
    this._actual = opts.gesto || "contenta";

    if (this.seguir && !quietos) {
      var self = this;
      this._mueve = function (e) {
        var r = svg.getBoundingClientRect();
        if (!r.width) return;
        var dx = (e.clientX - (r.left + r.width / 2)) / (r.width * 2.2);
        var dy = (e.clientY - (r.top + r.height / 2)) / (r.height * 2.2);
        var m = Math.min(1, Math.hypot(dx, dy) / 0.5) || 0;
        var n = Math.hypot(dx, dy) || 1;
        self.px.meta = (dx / n) * m * 3.0;
        self.py.meta = (dy / n) * m * 2.4;
      };
      global.addEventListener("pointermove", this._mueve, { passive: true });
    }

    this._bucle = this._bucle.bind(this);
    this.ultimo = 0;
    this.raf = requestAnimationFrame(this._bucle);
  }

  function alto(nombre) { var v = OJOS[nombre]; return Math.abs(v[7] - v[19]); } // P1y - P3y

  Carita.prototype.gesto = function (nombre) {
    var g = GESTOS[nombre]; if (!g) return this;
    this._actual = nombre;
    metas(this.bOI, OJOS[g.oi]); metas(this.bOD, OJOS[g.od]); metas(this.bB, BOCAS[g.b]);
    this.rell.meta = g.relleno; this.req.meta = g.equis; this.rlen.meta = g.lengua;
    this.abierto = { i: alto(g.oi), d: alto(g.od) };
    if (!quietos) { this.pulso.x = 1.075; this.pulso.v = 0; }   // chispazo de squash
    return this;
  };
  Carita.prototype.actual = function () { return this._actual; };

  // regla del sistema: la cara acompaña el valor de un control
  Carita.prototype.valor = function (v) {
    return this.gesto(v >= 100 ? "risa" : v <= 33 ? "sorpresa" : "guino");
  };

  Carita.prototype.destruir = function () {
    cancelAnimationFrame(this.raf);
    if (this._mueve) global.removeEventListener("pointermove", this._mueve);
  };

  Carita.prototype._bucle = function (ms) {
    var dt = this.ultimo ? Math.min(0.034, (ms - this.ultimo) / 1000) : 0.016;
    this.ultimo = ms; this.t += dt;

    // parpadeo: envolvente rápida, independiente del gesto
    if (this.parpadea) {
      if (this.bfase < 0) {
        this.prox -= dt;
        if (this.prox <= 0) { this.bfase = 0; this.dobles = Math.random() < 0.22 ? 1 : 0; }
      } else {
        this.bfase += dt / 0.085;
        var f = this.bfase;
        this.blink = f < 1 ? 1 - f * 0.94 : f < 2 ? 0.06 + (f - 1) * 0.94 : 1;
        if (this.bfase >= 2) {
          if (this.dobles) { this.dobles = 0; this.bfase = 0; }
          else { this.bfase = -1; this.blink = 1; this.prox = 2.2 + Math.random() * 4.2; }
        }
      }
    }

    this.pOI.setAttribute("d", d(leer(this.bOI, dt)));
    this.pOD.setAttribute("d", d(leer(this.bOD, dt)));
    this.pB.setAttribute("d", d(leer(this.bB, dt)));

    var r = this.rell.paso(dt);
    this.pB.setAttribute("fill", "currentColor");
    this.pB.setAttribute("fill-opacity", r.toFixed(3));
    var x = this.req.paso(dt);
    this.xOI.setAttribute("opacity", x.toFixed(3)); this.xOD.setAttribute("opacity", x.toFixed(3));
    var lg = this.rlen.paso(dt);
    this.lengua.setAttribute("opacity", lg.toFixed(3));
    this.lengua.setAttribute("transform", "translate(0,5.4) scale(1," + (0.25 + 0.75 * lg).toFixed(3) + ")");

    // el parpadeo solo pesa donde el ojo está abierto
    var pi = 1 - (1 - this.blink) * Math.min(1, this.abierto.i / 9);
    var pd = 1 - (1 - this.blink) * Math.min(1, this.abierto.d / 9);
    this.pOI.setAttribute("transform", "scale(1," + pi.toFixed(3) + ")");
    this.pOD.setAttribute("transform", "scale(1," + pd.toFixed(3) + ")");

    var px = this.px.paso(dt), py = this.py.paso(dt);
    this.cara.setAttribute("transform", "translate(" + px.toFixed(2) + "," + py.toFixed(2) + ")");

    var s = this.pulso.paso(dt);
    var ox = 0, oy = 0, rot = 0;
    if (this.respira) {
      ox = Math.sin(this.t * 0.31) * 1.1;
      oy = Math.sin(this.t * 0.23 + 1.7) * 0.9;
      rot = Math.sin(this.t * 0.17) * 0.9;
    }
    ox += px * 0.45; oy += py * 0.45;
    this.g.setAttribute("transform",
      "translate(" + (50 + ox).toFixed(2) + "," + (50 + oy).toFixed(2) + ") " +
      "rotate(" + rot.toFixed(2) + ") scale(" + s.toFixed(3) + "," + (2 - s).toFixed(3) + ") " +
      "translate(-50,-50)");

    this.raf = requestAnimationFrame(this._bucle);
  };

  // pieza suelta y estática, para catálogos
  Carita.pieza = function (tipo, nombre, tam) {
    var v = (tipo === "ojo" ? OJOS : BOCAS)[nombre];
    var lleno = nombre === "risa" || nombre === "oh" || nombre === "lengua";
    return '<svg viewBox="-16 -17 32 34" width="' + (tam || 44) + '" height="' + ((tam || 44) * 34 / 32) + '" fill="none" aria-hidden="true">' +
      (nombre === "lengua" ? '<path d="M-4.8,5.4 C-4.8,15.4 4.8,15.4 4.8,5.4 Z" fill="currentColor"/>' : '') +
      '<path d="' + d(v) + '" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"' +
      (lleno ? ' fill="currentColor"' : '') + '/>' +
      (nombre === "ups" ? '<path d="M-6,-6 L6,6 M6,-6 L-6,6" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>' : '') +
      '</svg>';
  };
  Carita.OJOS = Object.keys(OJOS);
  Carita.BOCAS = Object.keys(BOCAS);
  Carita.GESTOS = Object.keys(GESTOS);

  global.Carita = Carita;
})(window);
