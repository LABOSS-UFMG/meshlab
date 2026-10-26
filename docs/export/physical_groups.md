# `export/physical_groups.py` — classificação dos patches

`classify_faces` enumera as faces dos volumes e conta incidências por conjuntos de nós. Apenas faces com incidência única são externas. As duas seções da extrusão são identificadas pelo referencial geométrico:

| Modo | Grupos das seções |
|---|---|
| Planar | `frontAndBack` para ambas |
| Axissimétrico | `wedge_front` e `wedge_back` |

Para as faces laterais, projeta os nós de volta à seção 2D e associa cada coordenada ao nó de seção mais próximo. Na revolução, recupera a posição axial e o raio; na translação, usa as coordenadas `xy`. A tolerância é `1e-8 * max(extensão espacial, 1)`.

Os dois índices de seção de uma face lateral identificam uma aresta física e, portanto, o nome registrado em `mesh.boundaries`. Nós sem correspondência ou faces externas não classificadas provocam erro: interfaces internas não devem virar patches. Uma fronteira sobre o eixo não produz uma face de área finita.

`write_groups` reconstrói o modelo com um grupo volumétrico `fluid` e um grupo de superfície por nome. Os nomes `fluid`, `frontAndBack`, `wedge_front` e `wedge_back` são reservados para a saída e não devem ser usados nas curvas de entrada. Não há renomeação ou agrupamento automático das fronteiras fornecidas, nem definição de condições físicas do OpenFOAM.
