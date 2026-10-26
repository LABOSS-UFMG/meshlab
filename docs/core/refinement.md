# `core/refinement.py` — `Refinement`

Dataclass com `slots=True`, `repr=False` e `eq=False`. Armazena configuração; o cálculo dos tamanhos pertence a `export/refinement.py`.

```python
refinement = Refinement(geometry=curve, size=0.02, distance=0.1, transition=0.7)
```

| Atributo | Significado |
|---|---|
| `geometry` | Referência a `Point`, `Curve` ou `Contour`, sem cópia |
| `size` | Tamanho positivo desejado na região fina |
| `distance` | Distância adicional de tamanho constante, não negativa; padrão `0.0` |
| `transition` | Largura positiva da transição; padrão `1.0` |

Todas as distâncias estão nas unidades das coordenadas. Os parâmetros são validados no construtor, por funções em `utils/validation.py`. Alterações posteriores são responsabilidade do chamador.

- `Point`: vizinhança circular do ponto.
- `Curve`: faixa ao redor dos segmentos retos entre seus pontos; não há interpolação spline.
- `Contour`: interior completo de um polígono simples, inclusive côncavo, com uma faixa externa opcional.

Contornos com auto-interseções ou furos internos não fazem parte deste contrato. As geometrias de refinamento devem ter coordenadas 2D na exportação atual. A orientação do contorno não altera o refinamento. Nomes não criam patches nem precisam ser únicos entre referências de refinamento.

O refinamento não redistribui os pontos da geometria, não fixa novos nós e não altera camadas já geradas. A densidade de amostragem de uma curva descreve sua forma; `size` controla o tamanho solicitado ao Gmsh. Ver [campo de tamanho](../export/refinement.md).
