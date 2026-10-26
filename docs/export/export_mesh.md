# `export/export_mesh.py` — coordenação

```python
export_mesh(mesh, fronts=None, filename="output.msh", mode="planar",
            thickness=1.0, axis=None, angle=np.pi / 36,
            mesh_size=None, show=False, refinements=None)
```

`fronts=None` deriva todas as interfaces expostas das células. Se fornecida, a sequência de frentes deve corresponder exatamente a essas interfaces, incluindo laterais livres de camadas abertas. `mesh_size` controla o tamanho residual; os segmentos físicos e as células existentes permanecem fixos. `refinements` recebe objetos `Refinement`.

`mode="planar"` usa `thickness`; `mode="axisymmetric"` usa `axis` e `angle` em radianos. O eixo pode ser o nome de uma fronteira ou uma `Curve` reta independente. O ângulo padrão é cinco graus. A espessura deve ser positiva; o ângulo deve estar entre zero e pi. Essas condições são pré-condições de uso, não uma validação completa dos argumentos.

A função cria um modelo temporário, completa a seção, importa a malha híbrida e executa a extrusão. Consulta `minDetJac` de todos os volumes e rejeita resultados vazios, degenerados ou invertidos. Essa verificação não detecta toda sobreposição possível.

Reconstrói o modelo de saída com grupos físicos explícitos e grava MSH 2.2 ASCII, com elementos de primeira ordem. `show=True` abre a interface gráfica do Gmsh antes da gravação. O diretório de destino deve existir. O retorno é `None`.

Um bloco `finally` remove o modelo temporário e restaura o modelo anterior e as opções alteradas. A sessão Gmsh só é finalizada se tiver sido inicializada por esta chamada. Ver [fluxo e conversão](README.md).
