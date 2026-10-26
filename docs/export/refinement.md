# `export/refinement.py` — campo de tamanho

`build_size_callback(refinements, base_minimum, base_maximum)` captura cópias das coordenadas das geometrias e constrói o callback de tamanho usado durante a triangulação residual.

A distância `d` é euclidiana para `Point` e a menor distância aos segmentos para `Curve`. Em `Contour`, o teste de inclusão por cruzamento de raios atribui distância zero ao interior; fora dele, usa a distância ao perímetro. O contorno deve ser simples e fechado.

Para cada controle, com tamanho `size`, faixa constante `distance` e largura `transition`, calcula:

```text
base = clip(lc, base_minimum, base_maximum)
fine = min(size, base)
t = clip((d - distance) / transition, 0, 1)
w = t² (3 - 2t)
h = fine + (base - fine) w
```

`lc` é o tamanho recebido do Gmsh. O mínimo entre os controles sobrepostos determina o tamanho final. A interpolação tem derivada nula nos extremos; o controle só refina, não engrossa a distribuição de base. Isso suaviza o campo solicitado, mas não impõe uma razão exata entre tamanhos de elementos vizinhos.

O módulo de preenchimento reduz temporariamente o limite mínimo para permitir os refinamentos e remove o callback ao terminar. Preserva a referência de um callback anterior da API Python, quando existente. As geometrias não inserem nós fixos, fronteiras físicas ou superfícies internas; células e segmentos já construídos não são refinados novamente.

Ver os dados de entrada em [core/refinement.py](../core/refinement.md).
