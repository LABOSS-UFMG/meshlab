# Pipelines

O módulo `meshlab.pipelines` reúne operações de geração de malha em procedimentos reutilizáveis. Sua função pública, `generate_layers`, gera camadas de quadriláteros a partir de uma ou mais frentes já inicializadas na mesma malha plana.

## `generate_layers`

```python
meshlab.pipelines.generate_layers(
    mesh, fronts, *, num_layers, first_height, growth_rate=1.0,
    method="central", smooth_steps=0, relaxation=0.5, min_edge_ratio=0.0,
)
```

### Parâmetros

Os parâmetros após `fronts` são passados por nome. Um valor individual vale para todas as frentes. Uma lista deve ter o mesmo comprimento de `fronts`, e seu elemento de índice `i` configura a frente `fronts[i]`. As duas formas podem ser combinadas na mesma chamada.

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `mesh` | `Mesh` | Obrigatório | Malha bidimensional que recebe os novos vértices e quadriláteros. |
| `fronts` | sequência de `Front` | Obrigatório | Frentes distintas já inicializadas na malha, com suas guias quando aplicáveis. Para uma única frente, use `[frente]`. |
| `num_layers` | `int` ou `list[int]` | Obrigatório | Número de camadas por frente. Com zero, a frente permanece na posição inicial. |
| `first_height` | `float` ou `list[float]` | Obrigatório | Altura positiva do primeiro avanço, nas unidades das coordenadas da malha. |
| `growth_rate` | `float` ou `list[float]` | `1.0` | Fator positivo que multiplica a altura a cada camada. O valor 1 mantém a altura constante. |
| `method` | `str` ou `list[str]` | `"central"` | Método de cálculo das normais de cada frente. Aceita `"central"` ou `"bisector"`. |
| `smooth_steps` | `int` ou `list[int]` | `0` | Número de passos de suavização das normais antes de cada avanço. Com zero, usam-se as normais calculadas diretamente. |
| `relaxation` | `float` ou `list[float]` | `0.5` | Peso das normais vizinhas em cada passo de suavização, entre 0 e 1. |
| `min_edge_ratio` | `float` ou `list[float]` | `0.0` | Razão não negativa entre o comprimento mínimo de aresta e a altura da camada. Zero desativa a verificação para a frente correspondente. |

### Método de geração

A cada camada, a função percorre as frentes na ordem fornecida. Para cada frente que ainda tem camadas a gerar, recalcula as normais, aplica o número solicitado de passos de suavização e avança uma camada. Cada aresta da frente gera um quadrilátero.

Na frente $`i`$, a altura fornecida ao avanço da camada $`k`$ é

```math
h_{i,k} = h_{i,1}\,r_i^{k-1}, \qquad k=1,\ldots,N_i,
```

em que $`h_{i,1}`$ é a altura inicial, $`r_i`$ é o fator de crescimento e $`N_i`$ é o número de camadas dessa frente. A altura é uniforme ao longo da frente em cada passo. Cabe ao usuário escolher alturas compatíveis com a geometria e o espaço disponível entre frentes.

Quando a razão é positiva, após cada avanço a função seleciona as arestas da nova frente com comprimento estritamente menor que `min_edge_ratio * altura_atual`. Por exemplo, com altura 0,1 e razão 0,5, arestas menores que 0,05 são candidatas. O [colapso](3.8%20-%20collapse_edges.md) só ocorre quando o grupo de arestas satisfaz os critérios de proteção das fronteiras e validade local. Com `min_edge_ratio=[0.5, 0.0]`, apenas a primeira frente passa por essa verificação.

### Resultado

A função retorna `None`. Os novos vértices e células ficam em `mesh`, e cada frente passa a referenciar a borda da última camada que gerou. Se uma lista de parâmetros tiver comprimento diferente de `fronts`, a função lança `ValueError` antes do primeiro avanço.

### Exemplo

As bordas superior e inferior de um canal formam duas frentes orientadas para que o avanço ocorra em direção ao interior. Cada uma contém uma aresta. A frente superior gera duas camadas e a inferior gera três. As alturas iniciais são individuais, enquanto o fator de crescimento é compartilhado.

```pycon
>>> from meshlab.core import Contour, Curve, Front, Mesh
>>> from meshlab.operations import initialize_front, insert_contour
>>> from meshlab.pipelines import generate_layers

>>> mesh = Mesh()

>>> curvas = [
...     Curve("superior", [(0, 1), (2, 1)]),
...     Curve("saida", [(2, 1), (2, 0)]),
...     Curve("inferior", [(2, 0), (0, 0)]),
...     Curve("entrada", [(0, 0), (0, 1)]),
... ]

>>> insert_contour(mesh, Contour("canal", curvas))
>>> superior, inferior = Front("superior"), Front("inferior")

>>> for frente in [superior, inferior]:
...     initialize_front(mesh, frente, [frente.name], guides=["entrada", "saida"])

>>> generate_layers(
...     mesh, [superior, inferior],
...     num_layers=[2, 3], first_height=[0.05, 0.02], growth_rate=1.1,
... )

>>> mesh.cells.quadrilateral.num_cells
5

```
