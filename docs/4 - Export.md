# Export

O módulo `meshlab.export` disponibiliza a função `export_mesh`. Ela completa uma seção bidimensional e gera uma malha volumétrica com uma camada de elementos, gravada em formato Gmsh MSH 2.2 ASCII para posterior conversão.

## `export_mesh`

```python
meshlab.export.export_mesh(
    mesh, fronts=None, filename="output.msh", mode="planar",
    thickness=1.0, axis=None, angle=np.pi / 36, mesh_size=None,
    show=False, refinements=None,
)
```

### Parâmetros

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `mesh` | `Mesh` | Malha bidimensional com fronteiras físicas registradas por nomes únicos. A seção deve ser conforme, com células sem sobreposição. |
| `fronts` | sequência de `Front` ou `None` | Frentes que delimitam a interface entre as células existentes e a região a preencher. Por padrão, a função identifica essa interface pelas células e fronteiras. Se fornecidas, as frentes devem cobrir toda a interface. |
| `filename` | `str` ou `Path` | Caminho do arquivo de saída. O diretório deve existir. O padrão é `"output.msh"`. |
| `mode` | `"planar"` ou `"axisymmetric"` | Seleciona a extrusão por translação ou por revolução. O padrão é `"planar"`. |
| `thickness` | `float` | Espessura positiva da extrusão planar, na mesma unidade das coordenadas. O padrão é `1.0`. |
| `axis` | `str`, `Curve` ou `None` | Eixo de revolução, obrigatório no modo axissimétrico. Pode ser o nome de uma fronteira reta ou uma curva reta independente no plano da seção. O padrão é `None`. |
| `angle` | `float` | Ângulo total do setor axissimétrico, em radianos, entre zero e π, excluídos os extremos. O padrão é π/36 (5°). |
| `mesh_size` | `float` ou `None` | Tamanho-alvo positivo dos triângulos no interior da região a preencher. O padrão é `None`. |
| `show` | `bool` | Se `True`, abre a interface do Gmsh antes da gravação. O padrão é `False`. |
| `refinements` | sequência de `Refinement` ou `None` | Controles locais de tamanho na região a preencher. Em regiões de sobreposição, prevalece o menor tamanho solicitado. O padrão é `None`. |

### Método de geração

**1. Completa a seção.** A função preserva os triângulos e quadriláteros existentes e preenche a região restante com triângulos. Os parâmetros `mesh_size` e `refinements` atuam nessa triangulação, mantendo os segmentos de fronteira já definidos.

**2. Gera uma camada volumétrica.** No modo planar, a seção é transladada ao longo do eixo $`z`$ pela distância `thickness`. No modo axissimétrico, a seção é varrida de $`-\theta/2`$ até $`+\theta/2`$ em torno de `axis`, com $`\theta`$ igual a `angle`. A seção deve ficar de um só lado do eixo e pode tocá-lo. Os vértices sobre o eixo são compartilhados pelas duas faces do setor.

**3. Registra os grupos físicos.** O volume recebe o nome `fluid`. As superfícies laterais herdam os nomes das fronteiras que as geraram. No modo planar, as duas faces da seção formam o grupo `frontAndBack`. No modo axissimétrico, elas formam os grupos `wedge_front` e `wedge_back`. Esses nomes e `fluid` são reservados.

### Resultado

A função retorna `None` e grava a malha em `filename`. A malha bidimensional de entrada é preservada. Para uso no OpenFOAM, a conversão do arquivo com `gmshToFoam` e a configuração dos tipos de fronteira são etapas posteriores.

### Exemplo

Um contorno quadrado chamado `dominio` delimita a seção. A exportação preenche seu interior e gera uma camada de espessura 0,1. A superfície lateral recebe o nome da curva, `parede`.

```pycon
>>> from meshlab.core import Contour, Curve, Mesh
>>> from meshlab.operations import insert_contour
>>> from meshlab.export import export_mesh

>>> mesh = Mesh()

>>> parede = Curve("parede", [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
>>> insert_contour(mesh, Contour("dominio", [parede]))

>>> export_mesh(mesh, filename="quadrado.msh", thickness=0.1)

```
