# Redistribuição de pontos — proposta futura

Não há implementação de parametrização, interpolação ou redistribuição de `Curve` nesta versão. Os pontos fornecidos são usados diretamente na montagem. Isso é diferente de `Refinement`, que controla o tamanho solicitado ao Gmsh sem mudar a curva.

A proposta futura é parametrizar a poligonal pelo comprimento acumulado normalizado, interpolar cada coordenada no mesmo parâmetro e avaliar uma nova distribuição. Uma função monitor positiva pode definir uma cumulativa normalizada cuja inversa concentra os pontos onde o monitor é maior.

Método de interpolação, estimativa de curvatura e preservação de cantos ainda precisam ser definidos. A redistribuição deverá ocorrer antes da inserção em `Mesh`, preservando extremos, nome e orientação. Não existe subpasta `operations/curves/` no código atual.
