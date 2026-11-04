# Operations

O módulo `meshlab.operations` reúne as funções que inserem contornos na malha, preparam as frentes de avanço e geram as camadas de células. A função principal de cada arquivo tem o mesmo nome do arquivo, sem a extensão `.py`, e é exportada por `meshlab.operations`.

No fluxo básico, o contorno é inserido na malha e a frente é inicializada nas curvas selecionadas. A cada camada, as normais indicam a direção de avanço dos vértices, e o deslocamento da frente gera uma nova faixa de quadriláteros. Essas operações são descritas em 4 arquivos, definidos por:

| Arquivo | Responsabilidade |
|---|---|
| [insert_contour.py](../meshlab/operations/insert_contour.py) | Insere os vértices do contorno na malha e registra as fronteiras pelos nomes das curvas. |
| [initialize_front.py](../meshlab/operations/initialize_front.py) | Forma a frente a partir das curvas selecionadas e associa seus extremos às guias, quando fornecidas. |
| [compute_normals.py](../meshlab/operations/compute_normals.py) | Calcula a normal unitária em cada vértice, à direita da frente orientada. |
| [advance_front.py](../meshlab/operations/advance_front.py) | Gera uma camada de quadriláteros e atualiza a frente para o próximo avanço. |

As operações descritas anteriormente geram malhas pouco satisfatórias ou falham em cenários não muito complexos, como quando o ângulo entre duas arestas se aproxima de 90 graus. Nesse cenário, operações completares completares são definidas pelos arquivos:

| Arquivo | Responsabilidade |
|---|---|
| [compute_angles.py](../meshlab/operations/compute_angles.py) | Calcula o menor ângulo entre arestas incidentes e atribui π aos extremos abertos. |
| [smooth_normals.py](../meshlab/operations/smooth_normals.py) | Suaviza as normais com base nas normais vizinhas e calcula a rotação de cada vetor. |
| [find_short_edges.py](../meshlab/operations/find_short_edges.py) | Identifica as arestas da frente com comprimento abaixo do limite e as ordena da menor para a maior. |
| [collapse_edges.py](../meshlab/operations/collapse_edges.py) | Colapsa as arestas aceitas e atualiza a conectividade da malha e da frente. |
