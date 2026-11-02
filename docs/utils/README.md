# `utils/` — utilitários

| Arquivo | Responsabilidade |
|---|---|
| [validation.py](validation.md) | Verificações usadas pelos construtores |
| [refinement.py](refinement.md) | Redistribuição por monitores e suavização dos pesos |
| [plot_mesh.py](plot_mesh.md) | Células, fronteiras físicas, interfaces expostas e normais |

As operações sobre a malha ficam em `operations/`; a visualização não modifica a malha. Anotações adiadas e imports somente para tipagem evitam dependências circulares entre utilitários e estruturas do núcleo.
