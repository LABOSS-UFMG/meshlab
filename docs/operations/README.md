# `operations/` — operações sobre a malha

As funções recebem `mesh` e, quando necessário, `front`. Não armazenam referências globais. Os argumentos devem ser compatíveis com as pré-condições documentadas; decisões geométricas de aceitação pertencem aos algoritmos.

| Arquivo / função | Cálculo ou efeito | Retorno |
|---|---|---|
| `insert_contour.py` | Insere pontos e compartilha as junções do contorno | `None` |
| `initialize_front.py` | Monta arestas a partir de fronteiras nomeadas e associa guias | `None` |
| `compute_normals.py` | Soma tangentes incidentes e gira 90° no sentido horário | Normais |
| `compute_angles.py` | `arccos` entre direções para os dois vizinhos | Ângulos |
| `smooth_normals.py` | Média dos vizinhos, relaxação e normalização | Normais, rotação |
| `advance_front.py` | Desloca os nós, projeta extremos guiados e insere quadriláteros | `None` |
| `find_short_edges.py` | Comprimento e ordenação das arestas abaixo do limiar | Lista de pares |
| `collapse_edges.py` | Une grupos aceitos e compacta a conectividade | Mapa de índices |

## `insert_contour(mesh, contour)`

Insere o primeiro ponto do contorno, percorre cada curva e insere seus pontos intermediários. O início de cada curva reutiliza o fim da anterior; o último ponto do contorno reutiliza o primeiro índice. Em junções dentro da tolerância, prevalece a coordenada já inserida.

Cada `mesh.boundaries[curve.name]` recebe os índices ordenados em `mesh.int_dtype`. Os nomes devem ser globalmente únicos: uma chave repetida é sobrescrita. Inserções distintas não fundem pontos próximos. Não são criadas células ou frentes. As coordenadas precisam ser compatíveis com `mesh.dim`.

## `initialize_front(mesh, front, curves, guides=())`

Para cada nome em `curves`, cria arestas entre índices consecutivos da fronteira, preservando a ordem fornecida. Não acrescenta ligações entre curvas. Copia a conectividade para `front.entities.edge`, usando `front.int_dtype`; seleção vazia resulta em `(0, 2)`.

Conta incidências dos índices para identificar extremos de grau um. A interseção desses índices com as fronteiras de `guides` cria `front.constraints["guides"] = {índice: nome}`. A associação é topológica, não por proximidade. A chave `guides` é substituída; outras restrições são mantidas. As guias precisam ser segmentos retos não nulos.

## Contratos comuns

Normais, ângulos e alturas por nó seguem `np.unique(front.entities.edge)`: índices únicos em ordem crescente, não necessariamente ordem de percurso. Recalcular esses arrays após avanço ou colapso.

`advance_front` e `collapse_edges` modificam a mesma instância de frente. Após colapso, outras frentes precisam ser remapeadas pelo chamador. As curvas geométricas não usam índices globais e não são remapeadas.

Ver [cálculos planares](planar.md), [colapso](collapse_edges.md) e [descrição do domínio](domain.md).
