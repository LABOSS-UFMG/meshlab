# Descrição do domínio

Não existe classe `Domain`. `Curve` descreve segmentos nomeados; `Contour` declara suas junções; `insert_contour` registra os índices em `Mesh`; `Front` representa as interfaces móveis.

Um canal pode usar um contorno externo; corpos internos correspondem a furos. Todos os contornos físicos devem ser inseridos em `mesh.boundaries`. Entrada e saída também são fronteiras físicas, mas não precisam ser selecionadas por `initialize_front`.

O exportador não recebe os objetos `Contour`: reconstrói os laços residuais usando as fronteiras registradas e as arestas das células já geradas. Classifica exteriores e furos por contenção. Ver [preenchimento residual](../export/remaining_domain.md).

Laços devem ser simples, sem cruzamentos, com interfaces conformes. Não há montagem geral de domínios volumétricos 3D.
