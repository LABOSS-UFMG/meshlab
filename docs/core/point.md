# `core/point.py` — `Point`

Armazena um ponto geométrico nomeado, independente dos índices de `Mesh`.

```python
point = Point("wake_center", [2.0, 0.0], float_dtype=np.float64)
```

O construtor copia as coordenadas para um vetor NumPy de comprimento 2 ou 3. As propriedades `name`, `coordinates` e `float_dtype` expõem os dados; `coordinates` pode ser alterado diretamente. As validações de tipo numérico, dimensão e finitude ficam em `utils/validation.py` e são chamadas apenas na construção.

Criar um `Point` não insere nós, fronteiras nem grupos físicos. Seu uso atual é como referência geométrica de um `Refinement`. O armazenamento aceita 3D; o refinamento no exportador atual utiliza coordenadas 2D.
