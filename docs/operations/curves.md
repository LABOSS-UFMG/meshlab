# Redistribuição de pontos

A redistribuição está implementada em `meshlab/utils/refinement.py`, com interpolação linear por comprimento acumulado, monitores de início, fim e curvatura e suavização dos pesos. Ver [API e cálculos](../utils/refinement.md).

Aplicar antes de inserir as curvas em `Mesh`. Interpolação por splines e preservação automática de cantos permanecem possibilidades futuras. Não existe subpasta `operations/curves/`.
