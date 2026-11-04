# Core

O módulo `meshlab.core` define as estruturas de dados que representam a geometria, a malha e os parâmetros de refinamento. Essa estrutura de dados é definida em 6 arquivos:

| Arquivo | Classe | Responsabilidade |
|---|---|---|
| [mesh.py](2.1%20-%20Mesh.md) | `Mesh` | Coordenadas, conectividade e capacidade |
| [curve.py](2.2%20-%20Curve.md) | `Curve` | Pontos ordenados e nome da curva |
| [contour.py](2.3%20-%20Contour.md) | `Contour` | Referências ordenadas às curvas de um contorno |
| [front.py](2.4%20-%20Front.md) | `Front` | Arestas da frente e restrições |
| [point.py](2.5%20-%20Point.md) | `Point` | Ponto geométrico nomeado |
| [refinement.py](2.6%20-%20Refinement.md) | `Refinement` | Geometria e controle local de tamanho |

As estruturas da tabela se complementam na construção da malha. Cada `Curve` representa uma sequência de pontos e recebe um nome que identifica a fronteira correspondente nos grupos físicos do Gmsh. As curvas formam contornos fechados (`Contour`) que delimitam o domínio e curvas selecionadas fornecem as arestas da frente de avanço (`Front`), a partir da qual são geradas as camadas. A classe `Mesh` armazena as coordenadas dos vértices e a conectividade das células. Quando há refinamento local, `Refinement` associa o tamanho desejado dos elementos a uma referência geométrica, como um ponto (`Point`), uma curva ou um contorno.
