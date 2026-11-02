# `utils/refinement.py` — redistribuição de pontos

As funções trabalham com arrays `(N, 2)` ou `(N, 3)`, antes da montagem em `Mesh`. Não modificam os pontos recebidos. O parâmetro `s` é o comprimento acumulado da poligonal dividido por seu comprimento total.

```python
from meshlab.utils import (
    redistribute_points, monitor_start, monitor_end, monitor_curvature, monitor_corners,
)

points = redistribute_points(
    curve.points,
    num_points=150,
    monitor=lambda points: (
        monitor_start(points, strength=5.0, width=0.1)
        + monitor_end(points, strength=2.0, width=0.2)
        + monitor_curvature(points, strength=3.0)
    ),
    steps=4,
)
```

## Contrato dos monitores

Cada monitor recebe os pontos originais e retorna um array de comprimento `N`, com pesos finitos e estritamente positivos. Pesos maiores concentram mais pontos. Uma função personalizada segue o mesmo contrato, por exemplo `lambda points: 1 + points[:, 0]**2`. A função principal fornece uma cópia das coordenadas ao monitor.

| Função | Peso calculado |
|---|---|
| `monitor_start(points, strength=5, width=0.1)` | `1 + strength * exp(-s / width)` |
| `monitor_end(points, strength=5, width=0.1)` | `1 + strength * exp(-(1-s) / width)` |
| `monitor_curvature(points, strength=5)` | `1 + strength * curvature / max(curvature)` |
| `monitor_corners(points, strength=10, min_angle=pi/6)` | `1 + strength * clip((angle-min_angle)/(pi-min_angle), 0, 1)` |

`strength` deve ser não negativo e `width` positivo, em frações do comprimento total. A curvatura é estimada pelo ângulo entre tangentes unitárias dividido pela média dos comprimentos incidentes. Curvas retas retornam pesos unitários; extremos abertos usam a estimativa interna mais próxima. Curvas fechadas usam vizinhos periódicos.

O monitor de quinas usa o ângulo de mudança de direção entre arestas adjacentes, sem dividir pelo comprimento local. O limiar `min_angle` é dado em radianos e deve estar em `[0, pi)`. Extremos abertos recebem peso unitário; curvas fechadas usam vizinhos periódicos. Ele pode ser somado aos demais monitores e suavizado com `steps`. Concentrar pontos não garante preservar o vértice da quina; um arco pouco amostrado também pode ultrapassar o limiar angular.

A soma dos monitores inclui a soma de suas bases unitárias. Multiplicar o monitor inteiro por uma constante positiva não muda a distribuição; alterar o peso relativo de uma parcela muda sua influência.

## `redistribute_points(points, num_points, monitor=None, steps=0)`

Com `monitor=None`, o peso é constante e o espaçamento é uniforme no comprimento da poligonal. `steps` aplica passagens simultâneas de suavização aos pesos:

```text
m_novo[i] = 0.5*m[i] + 0.25*(m[i-1] + m[i+1])
```

Extremos abertos permanecem fixos. Para curvas fechadas, os pesos dos dois extremos coincidentes são inicialmente substituídos pela sua média; a suavização é periódica, sem contar duas vezes o nó de fechamento. Os monitores de início/fim, nesse caso, concentram pontos perto do corte escolhido para representar a curva.

A função integra o monitor linear por partes usando trapézios. Divide a massa total em `num_points - 1` partes iguais e inverte a integral quadrática em cada intervalo. Isso evita aproximar a inversa por uma reta quando os pesos variam. Por fim, interpola cada coordenada linearmente em `s` e restaura exatamente os extremos.

O retorno preserva `float32` ou `float64` da entrada; outros tipos produzem `float64`. O cálculo intermediário usa `float64`. `num_points` inclui o fechamento repetido quando presente.

## Pré-condições e limites

Os pontos devem ser finitos, ordenados e sem duplicatas consecutivas; a curva precisa ter comprimento positivo. São necessários pelo menos dois pontos de saída, ou quatro para uma curva fechada. O fechamento é reconhecido pela igualdade exata entre primeiro e último ponto. `steps` deve ser um inteiro não negativo. Não há validação explícita dos argumentos.

O monitor é avaliado nos pontos fornecidos, não em uma geometria analítica. A amostragem original deve resolver picos estreitos de refinamento; a suavização por vizinhos é discreta e depende dessa amostragem. Mais pontos não recuperam detalhes geométricos ausentes nos dados.

Cantos que precisam ser preservados devem separar curvas distintas: reconectar amostras que omitiram um canto pode cortá-lo. Nenhuma operação verifica auto-interseções da curva resultante. O refinamento não atualiza uma `Mesh` já montada e é independente de `core.Refinement`, usado no campo de tamanho do Gmsh.
