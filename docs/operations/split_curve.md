# `operations/split_curve.py` — corte arredondado de uma curva

```python
first, second = split_curve(
    curve,
    start_index=10,
    end_index=80,
    start_direction=[-1.0, 0.0],
    end_direction=[0.0, 1.0],
    radius=0.01,
)
```

Recebe uma curva planar simples, explicitamente fechada, e dois índices distintos em `curve.points[:-1]`. Ambos os vetores apontam do nó da superfície para o interior; são normalizados internamente. O raio é positivo, nas unidades das coordenadas. A operação é geométrica e anterior à montagem em `Mesh`.

## Construção

Sejam os nós `A`, `B` e as direções unitárias `u`, `v`. Resolve a interseção das retas `I = A + s*u = B + t*v`. Para `theta = arccos(u·v)` e raio `r`, o recuo a partir da interseção é `d = r/tan(theta/2)`.

Os pontos de tangência são `T1 = A + (s-d)*u` e `T2 = B + (t-d)*v`. O centro é `C = I - normalize(u+v)*r/sin(theta/2)`. O corte percorre `A → T1`, o arco menor até `T2`, e `T2 → B`. O último trecho tem direção `-v`.

O algoritmo escolhe o arredondamento anterior à interseção dos dois raios. Rejeita direções paralelas, interseções para trás e raios sem espaço para os dois segmentos. Não resolve outras configurações possíveis de círculos tangentes, como semicírculos entre raios paralelos.

## Discretização e aceitação

O espaçamento de referência é a média dos comprimentos das quatro arestas incidentes aos dois nós escolhidos. Cada segmento recebe subdivisões de comprimento no máximo igual a essa média. O arco usa o mesmo limite de comprimento e um passo angular máximo de 10 graus. Os pontos de tangência são mantidos explicitamente.

As contas usam coordenadas normalizadas e `float64`. Os resultados voltam ao tipo de `Curve`. A tangência é exata na construção analítica; os arrays representam a aproximação poligonal. A operação rejeita interseções ou sobreposições dessa poligonal com o contorno fora dos extremos e verifica que os pontos médios dos segmentos estão no interior. Esses testes são decisões geométricas, não uma validação geral do contorno de entrada.

## Retorno

Retorna duas novas `Curve`, chamadas `<nome>_1` e `<nome>_2`, sem alterar a entrada:

- A primeira segue o contorno de `start_index` até `end_index` e fecha pelo corte invertido.
- A segunda segue o trecho complementar e fecha pelo corte direto.

Os trechos da superfície preservam exatamente seus nós; o corte tem as mesmas coordenadas nas duas curvas, em ordem oposta. Cada curva repete seu primeiro ponto no fim e conserva a orientação da entrada. Antes de inserir ambas como corpos separados, criar uma folga por translação ou outra transformação: imediatamente após o corte, elas compartilham a interface.

Esta operação pertence ao pacote. Funções auxiliares em `tutorials/functions/` podem usar interfaces próprias para construir as geometrias dos exemplos; não devem ser confundidas com a API de `meshlab.operations.split_curve`.
