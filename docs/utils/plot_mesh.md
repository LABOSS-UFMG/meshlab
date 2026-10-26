# `utils/plot_mesh.py` — visualização da malha

**Status:** implementado para o novo `core`, com coordenadas 2D e 3D.

```python
from meshlab.utils import plot_mesh

figure, ax = plot_mesh(mesh)
```

A função desenha os contornos dos triângulos e quadriláteros válidos, as curvas registradas em `mesh.boundaries` e os vértices. As curvas seguem seus índices sem fechamento automático. Uma curva fechada já inclui o índice inicial no fim do registro. Em 3D, são mostradas arestas de células de superfície; não há renderização de volumes.

## Parâmetros

- `mesh`: malha a visualizar; não é modificada.
- `boundaries=None`: mostra todas as curvas. Uma sequência de nomes seleciona curvas; `[]` oculta todas.
- `show_points=True`: mostra os vértices da malha como pontos.
- `ax=None`: cria eixos de acordo com `mesh.dim`, ou utiliza os eixos fornecidos pelo chamador.
- `show=True`: exibe a figura. Use `False` para personalizar ou salvar antes da exibição.

A função retorna `(figure, ax)`. Não verifica entradas explicitamente; os eixos fornecidos devem ser compatíveis com a dimensão da malha. Não recebe objetos `Contour`. Normais de frentes selecionadas podem ser mostradas pelo parâmetro `normals`, conforme abaixo.

```python
figure, ax = plot_mesh(mesh, boundaries=["circle", "square"], show=False)
ax.set_title("Corpos")
figure.savefig("bodies.png", dpi=150, bbox_inches="tight")
```

O [tutorial t0](../../tutorials/t0.ipynb) demonstra a definição de círculo, quadrado e contorno externo retangular, incluindo a montagem e visualização. As curvas laterais usam nomes únicos `laterals_upper` e `laterals_lower`.

## Cores e interfaces expostas

As arestas das células usam `dimgrey`, com largura de 0.8 ponto. Fronteiras físicas usam cores por nome e largura de 1.8 ponto. As arestas com uma única célula incidente, excluindo todas as fronteiras físicas registradas, são desenhadas em preto, com largura de 0.8 ponto.

Essa borda preta é inferida das células, sem receber uma lista de frentes ativas. Pode incluir laterais livres da camada. A seleção `boundaries` controla apenas quais fronteiras físicas são mostradas; não muda essa classificação. Os vértices usam cinza.

## Normais em frentes selecionadas

```python
normals = compute_normals(mesh, inner_front)
figure, ax = plot_mesh(
    mesh,
    normals=[(inner_front, normals)],
    normal_scale=0.15,
)
```

`normals` recebe pares `(front, vetores)`. Para mostrar várias frentes, acrescentar os respectivos pares à sequência. Os pontos de aplicação são os vértices atuais da frente, na ordem de `np.unique(front.entities.edge)`, mesma ordem usada pelas operações. Recalcular os vetores após cada avanço. A função não calcula nem armazena normais em `Front`.

`normal_scale` multiplica o comprimento dos vetores apenas na figura, em unidades das coordenadas. O padrão é 0.1. As setas são suportadas em 2D e 3D, desde que os vetores tenham `mesh.dim` componentes; o cálculo atual de normais permanece planar. Omitir `normals` mantém o comportamento anterior.

Em 2D, o eixo da seta tem largura fixa de 0.8 ponto, igual à linha das células. A cabeça usa largura de três vezes e comprimento de quatro vezes essa largura. Assim, `normal_scale` altera o comprimento em coordenadas, sem engrossar o eixo ou aumentar a cabeça. Os limites incluem origens e pontas, com margem proporcional ao maior vetor.

Em 3D, `quiver` usa a mesma largura de linha, mas mantém a cabeça proporcional ao comprimento da seta. O ajuste dos limites inclui uma margem para essas cabeças. A renderização 2D e 3D não usa exatamente a mesma regra para a cabeça.
