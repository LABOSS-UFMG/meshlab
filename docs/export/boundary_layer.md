# `export/boundary_layer.py` — transferência das células

`collect_cells(mesh)` copia as conectividades válidas dos blocos `triangle` e `quadrilateral` para uma lista de células. Os buffers de `Mesh` não são alterados.

`boundary_edges(cells)` conta incidências usando o par de índices ordenado como chave não orientada. Arestas com uma única incidência compõem a borda; o valor mantém a orientação encontrada na célula. O procedimento pressupõe uma malha conforme: não reconhece automaticamente um nó intermediário sobre uma aresta maior.

`import_surfaces(points, cells)` agrupa células conectadas por vértices, usando união de conjuntos, e cria uma superfície discreta Gmsh por componente. Os índices de vértices tornam-se tags a partir de um. Triângulos e quadriláteros são inseridos como elementos Gmsh dos tipos 2 e 3. `createTopology` cria a topologia usada pela extrusão, sem rediscretizar a camada.
