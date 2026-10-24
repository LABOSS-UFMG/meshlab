# `interfaces/gmsh/` — integração com Gmsh

**Status:** exportador atual implementado em `meshlab/export/`, com modos `planar` e `axisymmetric`. As seções históricas abaixo registram a proposta de reorganização e as limitações do exportador legado.

## Uso atual e visualização

```python
from meshlab.export import export_mesh

export_mesh(mesh, fronts=[front], filename="NACA-2412.msh",
            mode="planar", thickness=0.1, mesh_size=0.5, show=True)
```

`show=False` é o padrão para execução sem interface gráfica. `show=True` abre a malha volumétrica final na janela do Gmsh, após a classificação dos grupos físicos e antes da gravação. Fechar a janela permite continuar a exportação; é necessário um ambiente com interface gráfica e suporte FLTK no Gmsh.

O [tutorial t5](../../tutorials/t5.ipynb) adapta o antigo tutorial de exportação do NACA 2412. O parâmetro `show_gmsh` controla essa opção e começa como `False`. As coordenadas estão em `tutorials/data/NACA-2412.dat`; a saída é `tutorials/results/NACA-2412.msh`. São dez camadas com 1.240 quadriláteros antes do preenchimento residual. O arquivo gerado foi convertido com OpenFOAM 13 e passou em `checkMesh -allTopology -allGeometry`, com 7.466 células, em 24/10/2026.

Para a conversão, configurar `writePrecision 16` no `controlDict` antes de executar `gmshToFoam`. O grupo `frontAndBack` deve receber `empty` no arquivo `constant/polyMesh/boundary` e nos campos do caso. O exportador escreve o `.msh`; não altera automaticamente o caso OpenFOAM.


## Refinamentos locais

```python
from meshlab.core import Point, Curve, Refinement

refinements = [
    Refinement(Point("focus", [2.0, 0.0]), size=0.02,
               distance=0.1, transition=0.5),
    Refinement(Curve("wake", [[1.0, 0.0], [4.0, 0.0]]), size=0.05,
               distance=0.2, transition=0.8),
]
export_mesh(mesh, filename="refined.msh", refinements=refinements)
```

`refinements=None` mantém o comportamento anterior. Cada `Refinement` aceita também um `Contour`, refinando seu interior completo. Os controles são aplicados na seção 2D antes da extrusão ou revolução; não mudam a espessura nem o número de camadas volumétricas.

`export/refinement.py` prepara cópias das coordenadas e uma função de tamanho para `gmsh.model.mesh.setSizeCallback`. Calcula distâncias a pontos e segmentos e identifica interiores por paridade de cruzamentos. Seja `d` a distância à geometria (zero dentro de um contorno):

```text
t = clip((d - distance) / transition, 0, 1)
w = t² (3 - 2t)
h = min(size, h_base) + (h_base - min(size, h_base)) w
```

`h_base` é o tamanho que o Gmsh forneceria, limitado pelos limites originais de tamanho. Controles sobrepostos são combinados pelo mínimo. Fora da influência, a função retorna o tamanho de base; a triangulação final não é obrigada a manter os mesmos elementos. O tamanho é um alvo: uma faixa muito estreita ou uma transição curta pode não ser bem resolvida. Aumentar `transition` permite uma variação espacial menos abrupta.

`remaining_domain.py` reduz temporariamente `Mesh.MeshSizeMin` para permitir os tamanhos locais mesmo quando `mesh_size` foi fornecido. Remove a função após o malhamento 2D e restaura o limite. O exportador restaura as opções da sessão ao terminar. A referência de callback do wrapper Python do Gmsh também é preservada para não invalidar callbacks de outros modelos.

Os segmentos físicos e as interfaces de camada permanecem fixos. Solicitar um tamanho pequeno junto a um segmento grosseiro não o subdivide: discretize previamente essa fronteira quando necessário. As geometrias de refinamento não são inseridas no modelo como fronteiras ou entidades embutidas e não geram grupos físicos.


## Responsabilidade

Transferir a malha de camada limite, construir a região residual, solicitar seu malhamento e gravar o resultado preservando fronteiras e conectividade. O núcleo do MeshLab não deve armazenar identificadores Gmsh como identidade principal de suas entidades.

## Arquivos propostos

| Arquivo | Responsabilidade |
|---|---|
| `model.py` | Preparação, coordenação da integração, gravação e ciclo de vida |
| `boundary_layer.py` | Conversão dos nós e elementos já construídos |
| `remaining_domain.py` | Construção e malhamento das regiões residuais |
| `physical_groups.py` | Mapeamento dos nomes e identificadores físicos |
| `extrusion.py` | Extrusão pseudo-2D opcional |

## Situação atual

A implementação agrupa células conectadas, cria superfícies discretas, identifica paredes por conjuntos de nós, constrói fronteiras da região externa, gera malha 2D e a extruda em uma camada de volumes. Em seguida, remove nós duplicados, otimiza e cria grupos físicos.

Limitações que precisam orientar a migração:

- A importação trata todas as células como quadriláteros, embora colapsos possam produzir triângulos.
- Nomes são associados a paredes completas e a um campo distante, sem distinguir seus segmentos.
- A identificação por conjunto completo de nós não representa diretamente curvas nomeadas dentro de um contorno composto.
- A construção atual agrega linhas externas e de furos em uma chamada de criação de laço; a representação explícita dos laços deve ser revista e testada para múltiplos furos.
- A extrusão está incorporada ao caminho padrão de exportação.

Essas observações resultam de inspeção do código; não são uma validação de execução de todos os caminhos.

## Contrato pretendido

Receber malha construída, associações de fronteiras e descrição da região residual. Manter um mapeamento explícito de índices internos para tags externas. Exportar por tipo real de célula, sem interpretar preenchimento `-1` como nó.

A região residual pode ter múltiplos laços e componentes. Cada contorno externo e cada furo devem ser representados explicitamente, com orientação e associação corretas. Após união de frentes, não reutilizar uma lista de furos que deixou de corresponder à topologia.

## Conformidade e preservação

A interface entre camadas e preenchimento deve possuir correspondência consistente de nós e arestas. Impedir subdivisões incompatíveis na interface ou reconciliá-las por um procedimento explícito. Remover nós duplicados, isoladamente, não prova conformidade de arestas e células.

Preservar coordenadas e elementos protegidos das camadas. Qualquer otimização posterior deve ter escopo documentado e ser verificada para não desfazer primeira altura, guias ou conectividade protegida. Não presumir que uma chamada geral de otimização preserve essas propriedades.

## Nomes e grupos físicos

Em uma malha 2D, condições de contorno são associadas a entidades de dimensão 1; a região fluida é de dimensão 2. Após extrusão, as fronteiras laterais tornam-se superfícies e o fluido um volume. Os nomes definidos nas curvas devem acompanhar esse mapeamento.

A interface não atribui automaticamente o comportamento físico de um solver apenas pelo nome. Nomes repetidos podem futuramente agrupar várias entidades, mas essa política precisa ser definida. Nós compartilhados entre duas curvas não apagam a distinção entre suas arestas nomeadas.

## Extrusão e 3D

A extrusão deve ser uma opção explícita, com espessura configurável e identificação das faces frontal e traseira. A geração 2D deve funcionar sem extrusão. A futura integração de malha volumétrica 3D recebe células construídas por algoritmos 3D próprios.

## Questões abertas e testes

Definir suporte a modelos Gmsh já inicializados, formato de saída, propriedade do ciclo de vida e dependência opcional. Testar preservação das camadas, células mistas, nomes por segmento, vários furos e conformidade. A estratégia concreta de API será validada contra a versão suportada durante a implementação.
