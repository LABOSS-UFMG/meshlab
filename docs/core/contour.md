# `core/contour.py` — contorno composto

**Status:** armazenamento e inserção no novo núcleo implementados.

```python
Contour(name, curves, tolerance=1e-10)
```

O construtor materializa o iterável de curvas em uma tupla, chama `validation.is_contour(curves, tolerance)` e guarda `name`, `curves` e `tolerance`. As propriedades expõem esses dados. As curvas são referenciadas sem cópia, reordenação ou inversão; alterações posteriores nas curvas não provocam nova validação.

## Contrato geométrico

O contorno representa um laço de curvas ordenadas. O fim de cada curva deve coincidir com o início da seguinte, incluindo o fim da última com o início da primeira, dentro da tolerância absoluta em unidades das coordenadas.

Exemplos são um perfil formado por extradorso, fechamento do bordo de fuga e intradorso, ou um canal formado por entrada, duas paredes e saída. O nome do contorno não substitui os nomes dos segmentos.

O validador verifica junções consecutivas e o fim da última curva contra o início da primeira. Não são verificadas explicitamente sequência vazia, auto-interseções ou validade da tolerância.

## Montagem

A classe não insere nós em `Mesh` e não constrói `Front`. A operação `insert_contour` atribui um único índice global a cada junção declarada. Proximidade geométrica, isoladamente, não autoriza fundir pontos de curvas independentes.

Os índices compartilhados podem aparecer nas associações de ambas as curvas. Os nomes acompanham as arestas, preservando fronteiras distintas na junção. Essas associações ficam em `mesh.boundaries`, conforme as [operações de montagem](../operations/README.md).

A região fluida usa [contorno externo e contornos internos](../operations/domain.md), sem classe `Domain`. Em 3D, contornos continuam úteis como bordos de superfícies; não representam, por si só, uma casca que delimita um volume.
