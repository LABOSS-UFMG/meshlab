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

A implementação antiga em `visualization/plot_mesh.py` continua como referência e depende das estruturas legadas removidas. O ponto de entrada atualizado é `meshlab.utils.plot_mesh`.

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
