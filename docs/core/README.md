# `core/` — estruturas de dados

**Status:** estruturas e operações de montagem implementadas. `operations-old/` é uma referência histórica, não o caminho de execução atual.

| Arquivo | Classes | Responsabilidade |
|---|---|---|
| [mesh.py](mesh.md) | `Mesh`, `Cells`, `CellBlock` | Coordenadas, conectividade e capacidade |
| [curve.py](curve.md) | `Curve` | Pontos ordenados e nome da curva |
| [contour.py](contour.md) | `Contour` | Referências ordenadas às curvas de um contorno |
| [front.py](front.md) | `Front`, `FrontEntities` | Arestas da frente e restrições |
| [point.py](point.md) | `Point` | Ponto geométrico nomeado |
| [refinement.py](refinement.md) | `Refinement` | Geometria e controle local de tamanho |
| `__init__.py` | Exportações | Disponibiliza as classes em `meshlab.core` |

## Convenções

As classes armazenam dados; normais, suavização e avanço pertencem às operações. O campo de tamanho de `Refinement` é aplicado pelo módulo de exportação. Os atributos internos usam prefixo `_` e propriedades expõem o estado. Uma propriedade sem setter não torna o array retornado imutável.

`Cells`, `FrontEntities` e `Refinement` usam `@dataclass(slots=True, repr=False, eq=False)`: contêineres simples acessados por atributos, sem interface de dicionário. Isso não os torna estruturas binárias compatíveis com C. Os buffers NumPy são o ponto de integração para futuros núcleos compilados.

Verificações de entrada são feitas nos construtores, preferencialmente por `utils/validation.py`; a checagem de `Mesh.dim` ainda está diretamente no construtor. Métodos de inserção e alterações diretas dos arrays não executam validação explícita. Ver [limites atuais](../utils/validation.md).

## Relações e propriedade dos dados

`Curve` copia coordenadas; `Contour` referencia as curvas sem copiá-las. `Mesh` mantém seu próprio armazenamento. `Front` copia a conectividade recebida, sem copiar coordenadas nem guardar uma malha.

A montagem associa pontos de curvas a índices globais em `mesh.boundaries`. Junções declaradas devem compartilhar um índice. Os nomes pertencem às arestas de origem: um único rótulo por nó não distingue duas condições de contorno que se encontram.

O chamador mantém as instâncias de `Mesh` e `Front` e as passa às operações. Não há singleton global. A frente pode futuramente representar vários componentes através das arestas; a classe atual não calcula componentes nem adjacência.

## Compatibilidade e expansão

O `data.Contour` legado é uma sequência de índices e também representa a frente móvel. O `core.Contour` é uma composição de curvas; o estado móvel pertence a `core.Front`. Portanto, a migração exige adaptar os chamadores, não apenas trocar imports.

Não há `domain.py`, `named_dict.py` ou `cell_types.py` no núcleo. A [descrição do domínio](../operations/domain.md) é passada explicitamente à montagem. Tipos volumétricos e entidades de face serão adicionados quando necessários; por enquanto, `Mesh(dim=3)` armazena triângulos e quadriláteros no espaço.
