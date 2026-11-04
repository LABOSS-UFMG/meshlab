# Utils

O módulo `meshlab.utils` reúne funções para redistribuir pontos ao longo de curvas e visualizar a malha. O refinamento atua sobre as coordenadas da curva antes de sua inserção na malha.

## Refinamento de curvas

```python
meshlab.utils.redistribute_points(points, num_points, monitor=None, steps=0, kind="cubic")
```

A função distribui uma quantidade definida de pontos ao longo de uma curva. O monitor atribui um peso a cada ponto de entrada. Nas regiões de maior peso, o espaçamento entre os novos pontos é menor.

### Parâmetros

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `points` | array de forma `(N, 2)` ou `(N, 3)` | Coordenadas finitas em ordem de percurso, sem pontos consecutivos coincidentes. Uma curva fechada repete o primeiro ponto no final. Prefira coordenadas de ponto flutuante para preservar posições fracionárias. |
| `num_points` | `int` | Número total de pontos de saída, incluindo os extremos. Use pelo menos dois em curvas abertas e quatro em curvas fechadas, contando o ponto repetido. |
| `monitor` | função ou `None` | Recebe uma cópia das coordenadas e devolve um peso positivo e finito por ponto. O padrão `None` produz espaçamento uniforme no parâmetro de comprimento de arco. |
| `steps` | `int` | Número de passos de suavização dos pesos. O padrão é zero. |
| `kind` | `str` | Interpolação usada para obter as coordenadas finais. O padrão `"cubic"` requer ao menos quatro pontos de entrada. Com `"linear"`, bastam dois e cada posição é interpolada sobre um segmento da poligonal. |

### Monitores disponíveis

As quatro funções recebem as coordenadas originais e retornam um array de forma `(N,)`. O parâmetro `strength` controla a intensidade do refinamento e deve ser não negativo. Com `strength=0`, todos os pesos valem 1.

| Função | Distribuição dos pontos |
|---|---|
| `monitor_start(points, strength=5.0, width=0.1)` | Concentra pontos no início. O peso é $1+A\exp(-s/w)$, em que $A$ é `strength`, $w$ é `width` e $s$ é o comprimento de arco normalizado entre 0 e 1. Uma largura positiva maior estende o efeito por um trecho maior. |
| `monitor_end(points, strength=5.0, width=0.1)` | Concentra pontos no fim. Usa os mesmos parâmetros, com peso $1+A\exp(-(1-s)/w)$. |
| `monitor_curvature(points, strength=5.0)` | Concentra pontos onde a direção varia mais por unidade de comprimento. Estima a curvatura pelo ângulo de giro dividido pelo comprimento médio das duas arestas incidentes e normaliza pela maior curvatura da curva. Em um trecho inteiramente reto, os pesos são uniformes. |
| `monitor_corners(points, strength=10.0, min_angle=np.pi/6)` | Concentra pontos perto de cantos cujo ângulo de giro supera `min_angle`. O giro vale zero em um trecho reto. O limiar é dado em radianos, entre zero e π, excluído π. |

Em curvas abertas, o monitor de curvatura atribui a cada extremo a estimativa do vértice interior mais próximo, quando ele existe. O monitor de cantos atribui peso 1 aos extremos. Em curvas fechadas, ambos consideram a vizinhança dos dois lados da junção. Para garantir que um canto permaneça entre os pontos de saída, divida a geometria em curvas que tenham esse canto como extremo.

### Método de cálculo

**1. Parametrização.** A função soma os comprimentos dos segmentos até cada ponto e divide pelo comprimento total da poligonal. O parâmetro resultante, $s$, varia de 0 a 1.

**2. Suavização dos pesos.** Em cada passo, um peso interior $w_i$ recebe a média ponderada $(w_{i-1}+2w_i+w_{i+1})/4$, usando os pesos do passo anterior. Nas curvas abertas, os pesos dos extremos permanecem fixos. Nas fechadas, a vizinhança é periódica.

**3. Redistribuição.** A função interpola os pesos linearmente entre as amostras e integra essa densidade pelo método dos trapézios. Em seguida, escolhe os parâmetros de saída de modo que cada intervalo contenha a mesma parcela da integral. Para $M$ pontos de saída e densidade $w(s)$, o parâmetro do ponto $j$ satisfaz

$$
\int_0^{s_j} w(s)\,ds =
\frac{j}{M-1}\int_0^1 w(s)\,ds,
\qquad j=0,\ldots,M-1.
$$

Por fim, a função interpola as coordenadas nesses parâmetros usando `kind`.

### Retorno e exemplo

O retorno é um novo array de forma `(num_points, 2)` ou `(num_points, 3)`, com o tipo numérico da entrada. O primeiro e o último ponto preservam exatamente as coordenadas originais.

No exemplo, as duas distribuições têm cinco pontos no mesmo segmento. Com `monitor_start`, o primeiro intervalo fica menor que o último.

```pycon
>>> import numpy as np
>>> from meshlab.utils import monitor_start, redistribute_points

>>> x = np.linspace(0.0, 1.0, 9)
>>> pontos = np.column_stack((x, np.zeros_like(x)))

>>> uniforme = redistribute_points(pontos, 5, kind="linear")
>>> uniforme[:, 0].tolist()
[0.0, 0.25, 0.5, 0.75, 1.0]

>>> refinada = redistribute_points(pontos, 5, monitor=monitor_start, kind="linear")

>>> intervalos = np.diff(refinada[:, 0])
>>> bool(intervalos[0] < intervalos[-1])
True

```

## Visualização

```python
meshlab.utils.plot_mesh(
    mesh, boundaries=None, show_points=True, ax=None, show=True,
    normals=None, normal_scale=0.1,
)
```

A função desenha os contornos das células e as fronteiras físicas de uma malha em duas ou três dimensões.

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `mesh` | `Mesh` | Obrigatório | Malha que contém as coordenadas dos vértices, as células e as fronteiras. |
| `boundaries` | sequência de `str` ou `None` | `None` | Nomes das fronteiras a destacar. `None` seleciona todas as fronteiras registradas e uma sequência vazia desativa o destaque. |
| `show_points` | `bool` | `True` | Exibe os vértices da malha como pontos. |
| `ax` | `Axes` do Matplotlib ou `None` | `None` | Eixos existentes compatíveis com a dimensão da malha. Quando omitido, a função cria uma figura com eixos 2D ou 3D. |
| `show` | `bool` | `True` | Exibe a figura ao final da chamada. Use `False` para personalizá-la antes da exibição. |
| `normals` | sequência de pares `(Front, ndarray)` ou `None` | `None` | Frentes e vetores normais a desenhar. Para cada frente, o array tem forma `(N, mesh.dim)`, com uma linha por vértice distinto, em ordem crescente de índice. |
| `normal_scale` | `float` | `0.1` | Multiplicador do comprimento das setas. Uma normal unitária é desenhada com esse comprimento em unidades da malha. |

### Retorno e exemplo

O retorno é o par `(fig, ax)` do Matplotlib. No exemplo, `fig` ajusta o tamanho da figura e `ax` define o título do gráfico antes da exibição.

```pycon
>>> import matplotlib.pyplot as plt
>>> from meshlab.core import Mesh
>>> from meshlab.utils import plot_mesh

>>> mesh = Mesh(dim=2)

>>> vertices = [mesh.add_vertex(p) for p in [(0, 0), (2, 0), (0, 1)]]
>>> mesh.add_cell("triangle", vertices)
0

>>> fig, ax = plot_mesh(mesh, show=False)
>>> fig.set_size_inches(6, 3)
>>> _ = ax.set_title("Malha triangular")
>>> plt.show()

```

## Validação

O arquivo `validation.py` implementa a validação dos dados de entrada das estruturas de `meshlab.core`. As funções de `meshlab.operations` pressupõem que as entradas atendam às condições descritas em cada operação e não fazem validação geral desses dados.
