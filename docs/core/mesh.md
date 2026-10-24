# `core/mesh.py` — malha e blocos de células

**Status:** implementado. As operações legadas ainda não usam esta estrutura.

## `Mesh`

```python
Mesh(dim=2, vertices_capacity=1000, cells_capacity=1000,
     increase_ratio=1.5, float_dtype=np.float64, int_dtype=np.int32)
```

`dim` informa a dimensão espacial, 2 ou 3. A interface de inserção é a mesma nas duas dimensões. `float_dtype` aceita `float32` ou `float64`; `int_dtype` aceita `int32` ou `int64`. As propriedades correspondentes retornam objetos `numpy.dtype`.

```python
from meshlab.core import Mesh

mesh = Mesh(dim=2)
for point in [[0, 0], [1, 0], [0, 1]]:
    mesh.add_vertex(point)
cell_index = mesh.add_cell("triangle", [0, 1, 2])
connectivity = mesh.cells.triangle.connectivity
```

`add_vertex` retorna um índice global de vértice. `add_cell` retorna um índice local ao bloco: a identidade de uma célula é o par `(tipo, índice)`. Os nomes aceitos são os atributos exatos `triangle` e `quadrilateral`, sem aliases.

## Coordenadas e capacidade

`mesh.points` é uma vista gravável das linhas válidas, com formato `(mesh.num_vertices, mesh.dim)`. `mesh.vertices_capacity` informa a capacidade reservada; o buffer completo é privado. Não há propriedade pública `vertices`.

Quando necessário, a capacidade passa para `max(capacidade + 1, ceil(capacidade * increase_ratio))`. Os dados válidos e seus índices são preservados. Recomenda-se fator maior que um para crescimento multiplicativo; o validador atual não impõe esse limite, conforme [validação](../utils/validation.md).

## `Cells` e `CellBlock`

`Cells` é uma dataclass que contém apenas `triangle` e `quadrilateral`. Cada atributo referencia um `CellBlock` independente, criado já no construtor de `Mesh`, com `cells_capacity` linhas reservadas. O acesso é por atributo, não por chave.

```python
CellBlock(vertices_per_cell, capacity=1000,
          increase_ratio=1.5, int_dtype=np.int32)
```

| Propriedade de `CellBlock` | Significado |
|---|---|
| `connectivity` | Vista gravável das linhas válidas |
| `num_cells` | Quantidade de células inseridas |
| `capacity` | Quantidade de linhas reservadas |
| `vertices_per_cell` | Largura fixa da conectividade |
| `int_dtype` | Tipo NumPy dos índices |

Triângulos usam três índices; quadriláteros usam quatro. `block.add_cell(indexes)` insere uma linha e devolve seu índice local. `mesh.num_cells` soma as contagens dos dois blocos.

A reserva usa `np.empty`: as linhas não utilizadas não têm conteúdo definido e não são expostas por `connectivity`. Não há preenchimento com `-1`, propriedade `values` ou dimensão topológica armazenada no bloco. Em `Mesh(dim=3)`, esses mesmos blocos representam células de superfície, não volumes.

## Responsabilidade do chamador

As inserções convertem os dados para os tipos configurados, mas não fazem verificações explícitas de aridade, referências, finitude, orientação ou qualidade. Falhas naturais de conversão e atribuição NumPy ainda podem ocorrer. O chamador fornece coordenadas e conectividade consistentes, com índices representáveis no tipo escolhido.

Após uma expansão, obter novamente `mesh.points` e `block.connectivity`: vistas e ponteiros antigos podem continuar ligados ao buffer anterior. Essa regra também se aplica à integração futura com C ou C++.

Remoção, compactação e renumeração não estão implementadas no núcleo. Sua futura implementação precisará atualizar as referências de células, frentes e associações das fronteiras.

## Fronteiras físicas

`_boundaries` é inicializado como um dicionário independente por malha, acessível pela propriedade gravável `boundaries`. Cada chave é o nome globalmente único de uma curva; o valor é um array de índices ordenados em `mesh.int_dtype`. Não há agrupamento pelo nome do contorno.

`insert_contour` preenche esse registro; `initialize_front` usa uma seleção explícita de nomes para construir as arestas móveis. Nomes únicos são responsabilidade do usuário, sem verificação. As fronteiras não mudam quando a conectividade da frente é alterada. Ver [montagem](../operations/README.md).
