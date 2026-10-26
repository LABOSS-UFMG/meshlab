# `export/remaining_domain.py` — preenchimento residual

`generate_remaining(mesh, cells, fronts=None, mesh_size=None, refinements=None)` retorna coordenadas e conectividades da seção completa. Trabalha com cópias e acrescenta os triângulos gerados pelo Gmsh.

Sejam `P` as arestas físicas de `mesh.boundaries` e `L` as arestas de incidência única das células existentes. As chaves são pares não orientados:

```text
interface = L - P
borda_residual = (P - L) ∪ interface
```

Frentes explícitas devem coincidir com `interface`. `_loops` percorre a borda residual e exige grau dois em cada vértice. `_inside` usa cruzamento de raios para determinar a profundidade de inclusão dos laços: profundidade par inicia uma superfície; os laços imediatamente internos definem seus furos. Isso pressupõe laços simples que não se cruzam.

Cada segmento recebe uma curva transfinita com dois nós, preservando seus extremos e impedindo subdivisão da interface. `mesh_size`, quando definido, configura os limites de tamanho do interior. O callback de [refinamento](refinement.md) pode reduzir esse tamanho localmente.

Após gerar a malha 2D, os nós de fronteira são associados aos índices originais e os novos nós interiores são acrescentados. As conectividades são orientadas no sentido anti-horário pela área assinada. Células da camada são preservadas, exceto pela ordem dos índices necessária à orientação.

A correspondência é topológica: segmentos parcialmente coincidentes e nós pendurados não são corrigidos. Em extremos guiados, evitar pontos preexistentes no trecho varrido pela camada; os novos nós da guia precisam formar segmentos compatíveis com as faces das células.
