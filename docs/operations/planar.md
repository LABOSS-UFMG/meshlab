# Cálculos planares em `operations/`

Os arquivos estão diretamente em `meshlab/operations/`; não existe uma subpasta `planar/`. As funções abaixo pressupõem frentes sem ramificações, arestas orientadas consistentemente e vetores não nulos. Usam a ordem de vértices `np.unique(front.entities.edge)`.

## `compute_normals(mesh, front, method="central")`

Para cada aresta dirigida `(a, b)`, calcula `v = p_b - p_a`. A contribuição é `v` no método `central` e `v / ||v||` no método `bisector`. Acumula a mesma contribuição nos dois extremos da aresta com `np.add.at`.

Em um nó interno, a soma central equivale a `p_seguinte - p_anterior`; a bissetora dá o mesmo peso às tangentes unitárias incidentes. Em extremos abertos, usa a única aresta. Normaliza a soma para obter `t` e retorna `n = (t_y, -t_x)`, conforme `t × ez`.

Não impõe guias nem suaviza. Tangentes resultantes nulas não possuem tratamento especial. O retorno tem forma `(N, 2)` e usa `mesh.float_dtype`.

## `compute_angles(mesh, front)`

Normaliza as arestas e forma, em cada nó, os vetores unitários `u` e `v` apontando para seus vizinhos. Calcula:

```text
angle = arccos(clip(u · v, -1, 1))
```

O resultado está em `[0, pi]`: nós retos têm `pi`, mas cantos convexos e reflexos não são distinguidos. Extremos de grau um recebem `pi` por convenção, tornando neutra a correção de altura baseada apenas no ângulo.

## `smooth_normals(mesh, front, normals, relaxation=0.5)`

Acumula as normais dos vizinhos pelas arestas e divide pelo grau do nó. Com média `m` e relaxação `alpha`, calcula simultaneamente:

```text
q = (1 - alpha) n + alpha m
n_novo = q / ||q||
rotation = atan2(n_x n_novo_y - n_y n_novo_x, n · n_novo)
```

Retorna novos arrays de normais e rotações assinadas; sentido anti-horário é positivo. `alpha` pode ser escalar ou por nó. Extremos usam um vizinho. O cálculo não protege cantos, não impõe guias e pressupõe `q` não nulo.

## `advance_front(mesh, front, normals, height)`

Calcula `p_novo = p + height * normals`, com altura escalar ou por nó. Para cada extremo guiado, usa origem `o` e tangente `t` entre os extremos da fronteira-guia:

```text
s = ((p_novo - o) · t) / (t · t)
p_novo = o + s t
```

A projeção é na reta de suporte, sem limitar `s` a `[0, 1]`. Em seguida, insere um nó por vértice distinto da frente e um quadrilátero `[a, novo_a, novo_b, b]` por aresta `(a, b)`.

Novos nós guiados são acrescentados à fronteira correspondente e ordenados pela projeção na tangente. As chaves de `constraints["guides"]` e as arestas da frente passam a apontar para os novos nós. O retorno é `None`.

Não há verificação de qualidade, colisões ou limites da guia nessa operação. Normais e passos adequados são responsabilidade do chamador.

## Alturas usadas nos tutoriais

O crescimento segue `h_k = h_0 * growth_rate**k`. A correção de canto usa `h_k / sin(angle/2)`. O exemplo suavizado usa `h_k / sin(angle/2 + abs(rotation_acumulada))`, preservando a heurística legada; não é garantia geral de espessura normal ou validade.

A seção final de `t3.ipynb` usa dez camadas, altura inicial `0.04`, crescimento `1.10` e colapso de candidatos menores que `1.5*h_k`. Nos parâmetros demonstrados, colapsa nove arestas e termina com 258 quadriláteros e nove triângulos. Os critérios do colapso estão em [collapse_edges.md](collapse_edges.md).
