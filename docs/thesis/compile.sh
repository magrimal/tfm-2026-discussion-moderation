#!/bin/bash
# Compilación completa de la tesis (lualatex + biber + lualatex x2)
# Ejecutar desde docs/thesis/
cd "$(dirname "$0")"

# Limpia auxiliares para evitar conflictos con compilaciones anteriores
rm -f tfm.aux tfm.toc tfm.bbl tfm.bcf tfm.blg tfm.out tfm.run.xml tfm.lof tfm.lot

# Primera pasada: genera .bcf para biber (puede haber warnings de refs sin resolver)
lualatex -interaction=nonstopmode tfm.tex || true

# Procesa la bibliografía
biber tfm

# Segunda y tercera pasadas: resuelve referencias y TOC
lualatex -interaction=nonstopmode tfm.tex || true
lualatex -interaction=nonstopmode tfm.tex

echo ""
echo "=== Errores fatales ==="
grep -E "^!" tfm.log | head -20 || echo "(ninguno)"
echo ""
echo "=== Páginas generadas ==="
grep "Output written" tfm.log || echo "(ver tfm.log)"
