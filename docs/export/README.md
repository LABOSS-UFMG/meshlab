# `export/` — malha final e saída para OpenFOAM

O ponto de entrada público é `from meshlab.export import export_mesh`. A entrada é uma seção planar de `Mesh(dim=2)`, com fronteiras físicas e células de camada limite opcionais. A exportação preserva essas células, preenche a região restante com triângulos e gera uma camada volumétrica por translação ou revolução. Não modifica `mesh` nem as frentes.

| Arquivo | Responsabilidade |
|---|---|
| [export_mesh.py](export_mesh.md) | Coordenação, sessão Gmsh, verificação e gravação |
| [boundary_layer.py](boundary_layer.md) | Cópia das células, incidência de arestas e importação discreta |
| [remaining_domain.py](remaining_domain.md) | Interfaces, laços fechados e triangulação residual |
| [refinement.py](refinement.md) | Campo de tamanho local por distância |
| [extrusion.py](extrusion.md) | Translação planar ou revolução axissimétrica |
| [physical_groups.py](physical_groups.md) | Classificação das faces e nomes dos patches |

Os módulos auxiliares dependem de um modelo Gmsh ativo e são usados pelo coordenador. Não constituem etapas independentes que o usuário precisa executar. A seção deve ser conforme, sem sobreposições nem interseções; o exportador não repara uma camada inválida.

## Conversão e verificação

No diretório de um caso OpenFOAM configurado, executar `gmshToFoam caminho/mesh.msh`. Conferir os nomes e tipos em `constant/polyMesh/boundary` e configurar os campos: faces planares de espessura usam `empty`; faces de revolução usam `wedge`; paredes e demais fronteiras recebem os tipos apropriados ao caso. Depois executar `checkMesh -allTopology -allGeometry` e conferir o relatório, não apenas o código de saída.

Esses comandos são externos ao pacote. O exportador não edita condições de contorno, não agrupa patches automaticamente e não altera arquivos do caso. Para cunhas, preservar precisão suficiente nas coordenadas gravadas pelo OpenFOAM, por exemplo `writePrecision 16`, evita perda de planaridade por arredondamento.

Ver os tutoriais [t4](../../tutorials/t4.ipynb), [t5](../../tutorials/t5.ipynb) e [t6](../../tutorials/t6.ipynb).
