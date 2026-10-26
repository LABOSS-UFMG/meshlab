# `core/curve.py` — curva nomeada

**Status:** armazenamento e montagem implementados; redistribuição de pontos ainda não implementada.

```python
Curve(name, points, float_dtype=np.float64)
```

A classe guarda `name`, `points` e `float_dtype`. O uso previsto é um array `(N, 2)` ou `(N, 3)` com pontos em ordem de percurso. Cada ponto da discretização final corresponde a um nó após a montagem.

O construtor valida o tipo de ponto flutuante (`float32` ou `float64`) e copia as coordenadas. Modificar o array de entrada depois da construção não modifica a curva. A propriedade `points` expõe o array gravável; a ordem nunca é alterada automaticamente.

Atualmente não há verificação explícita do nome, formato, finitude ou coincidência de pontos. Os requisitos geométricos citados nas docstrings são pré-condições de uso, não garantias fornecidas pelo construtor. Ver [validação](../utils/validation.md).

## Orientação em 2D

Para tangente unitária `t = (tx, ty)` e `ez = (0, 0, 1)`, a convenção das operações é `n = t × ez = (ty, -tx)`. A normal aponta à direita do percurso. O usuário escolhe a ordenação conforme o lado fluido: um corpo percorrido em sentido anti-horário produz normal para fora; um contorno externo percorrido em sentido horário produz normal para dentro.

A classe não calcula normais. Em coordenadas 3D, uma curva isolada não determina a normal de uma superfície; a convenção com `ez` é restrita ao caso planar.

## Operações e montagem

As [operações sobre curvas](../operations/curves.md) deverão separar interpolação geométrica de distribuição de pontos, preservar extremos e orientação e tratar cantos explicitamente. A proposta inicial redistribui os pontos antes da montagem em `Mesh`.

O nome identifica a fronteira física. Não determina se a curva gera camadas: entradas e saídas também precisam de nomes. `insert_contour` registra os índices em `mesh.boundaries`; `initialize_front` seleciona curvas ativas e guias por nome. `split_curve` permite separar uma curva fechada antes da montagem, conforme [operações](../operations/README.md). Não há campos adicionais de refinamento ou condições de contorno em `Curve`.
