# `core/front.py` — frente independente

**Status:** armazenamento de arestas implementado. A operação `initialize_front` preenche as arestas a partir de `mesh.boundaries`.

## Responsabilidade

`Front` guarda o estado da frente sem receber ou armazenar `Mesh`. O chamador mantém a malha e a frente durante o processo e passa ambas explicitamente às operações que precisam delas. Isso não impõe um singleton global: o chamador controla a instância.

```python
from meshlab.core import Front, FrontEntities

front = Front(
    name="front",
    entities=FrontEntities(edge=[[0, 1], [1, 2]]),
    int_dtype="int32",
)
```

O uso das operações segue o padrão `operacao(mesh, front, ...)`. A dimensão espacial é consultada em `mesh.dim`, nunca duplicada na frente. Os índices da frente referenciam os vértices da malha fornecida à operação.

## Dados

- `name`: identificador da frente.
- `entities`: dataclass `FrontEntities`, com somente o campo `edge`.
- `entities.edge`: array NumPy de conectividade `(N, 2)`.
- `int_dtype`: `int32` por padrão ou `int64`, configurado no construtor.
- `constraints`: dicionário de restrições interpretadas pelas operações.

Os arrays são copiados na construção. Quando `entities` é `None`, a frente recebe um array independente `(0, 2)`, com zero arestas e o tipo inteiro configurado. `None` é uma conveniência de entrada; após a construção, `entities.edge` é um array. Não há campos `mesh` ou `dim`, nem faces triangulares ou quadrilaterais. O construtor recebe `FrontEntities`, sem entrada por dicionário.

## Validação e atualização

As verificações ficam centralizadas em `utils/validation` e são chamadas apenas no construtor. Atualmente o construtor verifica apenas `int_dtype`; formato, nomes e conectividade são responsabilidade do chamador. O auxiliar `is_front` existe, mas não é chamado pelo construtor.

A existência dos vértices não pode ser verificada sem a malha. A consistência entre frente e malha deve ser tratada na montagem ou em uma operação explícita de validação. Adjacência, orientação e validade geométrica não são inferidas pelo armazenamento.

Operações podem modificar os dados sem validação automática. Alterações que renumerem vértices devem atualizar a conectividade das frentes. Não criar cópias independentes das coordenadas em `Front`.

## Evolução

Junções, guias, divisão e união de frentes continuam sendo responsabilidades das operações. Arestas podem referenciar coordenadas 2D ou 3D, mas uma frente volumétrica de faces ainda não está implementada. Novas entidades serão acrescentadas quando necessárias.

`FrontEntities` usa `@dataclass(slots=True, repr=False, eq=False)`. O campo `edge` é o único campo de entidades. O dicionário `constraints` começa vazio em cada instância; `initialize_front(..., guides=...)` preenche a chave `"guides"` com o mapa de índices de extremos para nomes de fronteiras retas. `advance_front` atualiza esses índices após cada camada. Não há métodos de avanço ou inserção na classe. As funções externas `compute_normals` e `advance_front` recebem `mesh` e `front`; o avanço atualiza a mesma instância. Ver [operações](../operations/README.md).
