# Arestas curtas e colapso local

## `find_short_edges.py`

`find_short_edges(mesh, front, min_length)` retorna pares dirigidos de índices de vértices, com comprimento estritamente menor que o limite. A ordem é crescente por comprimento; empates preservam a ordem das arestas na frente. Não altera os objetos. Usa diretamente `front.entities.edge`, sem criar uma ligação artificial entre os extremos de uma frente aberta.

## `collapse_edges.py`

```python
edges = find_short_edges(mesh, front, min_length=1.5 * height)
index_map = collapse_edges(mesh, front, edges)
```

Atualiza `mesh` e `front` no próprio objeto e retorna um array de tipo `mesh.int_dtype`, cujo tamanho é o número de vértices antes da operação. `index_map[old_index]` fornece o novo índice. Diferentemente da API antiga, não retorna uma nova frente.

O chamador fornece arestas válidas da frente, em índices anteriores à chamada. Cada componente da frente deve ser um percurso simples aberto ou fechado. A detecção funciona nas dimensões armazenadas pela malha; o colapso atual é exclusivamente 2D.

### Critérios de aceitação

Arestas candidatas conectadas formam um grupo, inclusive quando atravessam o fechamento da frente. Cada grupo é proposto como um único vértice no centroide de seus vértices originais distintos. Os grupos são processados pela ordem de seu menor índice original, independentemente da ordem dos candidatos.

O grupo inteiro é rejeitado quando:

- contém um vértice registrado em `mesh.boundaries` ou nas guias da frente;
- deixa menos de três vértices em um componente fechado ou menos de dois em um aberto;
- produz repetição não consecutiva de índices numa célula;
- torna uma célula sobrevivente degenerada, não convexa ou com orientação invertida.

Quadriláteros reduzidos a três vértices migram para `cells.triangle`. Células reduzidas a menos de três vértices são removidas, preservando o comportamento legado. Os critérios geométricos fazem parte da decisão do algoritmo; não são validações de argumentos. O colapso não detecta sobreposição com células distantes, colisão entre frentes nem certifica a topologia global.

### Armazenamento e referências

A operação prepara as alterações em cópias e compacta os vértices uma vez, após processar todos os grupos. Reutiliza a capacidade existente de coordenadas e reconstrói os blocos de células com `add_cell`. A atualização dos contadores internos fica localizada nessa etapa. Índices locais de células podem mudar; recupere novamente views dos arrays e recalcule as normais.

As coordenadas dos vértices físicos permanecem fixas. `mesh.boundaries` e as chaves de `front.constraints["guides"]` são remapeadas automaticamente. Outras frentes pertencem ao chamador:

```python
other_front.entities.edge = index_map[other_front.entities.edge].astype(other_front.int_dtype)
other_front.constraints["guides"] = {
    int(index_map[index]): name
    for index, name in other_front.constraints.get("guides", {}).items()
}
```

Esse exemplo pressupõe outra frente independente, sem arestas compartilhadas com o grupo colapsado. Se outros objetos referenciarem os mesmos vértices colapsados, sua conectividade precisa ser reconciliada, incluindo eventuais arestas degeneradas. Restrições personalizadas não são interpretadas automaticamente.

`Curve` e `Contour` guardam coordenadas geométricas, não índices de `Mesh`; não precisam desse remapeamento.

## Verificação

`tests/operations/collapse_edges_test.py` cobre ordenação de candidatos, conversão de quadrilátero em triângulo, remoção de triângulo reduzido, rejeição de inversão, preservação de vértices físicos, grupos no fechamento, guias abertas e continuidade de dez camadas na geometria em L do tutorial antigo `t5`.
