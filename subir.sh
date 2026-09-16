#!/usr/bin/env bash
# Crea el repo motta-bit/lqs, sube todo y prende GitHub Pages.
# Requiere el CLI de GitHub: https://cli.github.com  (o usar el bloque manual del final)
set -e
gh auth status >/dev/null 2>&1 || gh auth login

git init -b main
git add -A
git commit -m "LQS — sitio oficial v1

Las doce secciones, el ecosistema interactivo y el cotizador con las
dos cifras separadas de Redes. Sin dependencias ni build."

gh repo create lqs --public --source=. --push \
  --description "LQS — agencia creativa modular. Sitio oficial."

gh api -X POST repos/motta-bit/lqs/pages \
  -f 'source[branch]=main' -f 'source[path]=/' >/dev/null 2>&1 || \
  gh api -X PUT repos/motta-bit/lqs/pages -f 'source[branch]=main' -f 'source[path]=/'

echo
echo "Listo. En 1 o 2 minutos:  https://motta-bit.github.io/lqs/"
