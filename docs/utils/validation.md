# `utils/validation.py` — verificações dos construtores

As verificações reutilizáveis ficam neste módulo e são chamadas na construção das estruturas. Métodos de inserção e alterações diretas dos arrays não as repetem. `Mesh.dim` ainda é verificado diretamente no construtor.

| Estrutura | Verificações explícitas |
|---|---|
| `Mesh` | Dimensão, capacidades, fator de crescimento e tipos NumPy |
| `CellBlock` | Largura, capacidade, fator de crescimento e tipo inteiro |
| `Curve` | Tipo de ponto flutuante |
| `Contour` | Junções e fechamento através de `is_contour` |
| `Front` | Tipo inteiro configurado |
| `Point` | Tipo de ponto flutuante e vetor finito de duas ou três coordenadas |
| `Refinement` | Tipo da geometria, tamanho e transição positivos, distância não negativa |

Os auxiliares `is_int`, `is_sequence`, `is_object` e `is_union` também ficam disponíveis para os chamadores existentes.

## Limites atuais

- `is_positive_float` aceita zero; não garante `increase_ratio > 1`. A expansão de capacidade ainda acrescenta no mínimo uma linha.
- `is_positive_int` exige `int` de Python, apesar da menção a inteiros NumPy em sua docstring.
- `Curve` não verifica explicitamente nome, formato, finitude ou geometria dos pontos.
- `is_contour` compara os extremos consecutivos, incluindo o fechamento; não verifica lista vazia, tolerância ou auto-interseções.
- `Front` não verifica a existência dos vértices nem a validade geométrica das arestas. O auxiliar `is_front` não é chamado por seu construtor.

Esses limites descrevem a implementação, sem acrescentar garantias ao armazenamento. Conversões e atribuições NumPy ainda podem produzir erros naturais.

## Critérios geométricos nas operações

O avanço não detecta colisões ou inversões. O colapso faz testes locais de orientação e convexidade antes de aceitar uma alteração; a exportação verifica jacobianos volumétricos e a classificação de faces. Esses critérios fazem parte dos algoritmos, não da validação de entrada dos construtores. Nenhum deles constitui uma detecção global de sobreposições.

Ao alterar conectividade, preservar índices válidos, junções compartilhadas e associações das fronteiras; após compactação, atualizar todas as frentes. Ver [colapso](../operations/collapse_edges.md) e [exportação](../export/README.md).

## Testes

Executar `.venv/bin/python -m pytest -q` na raiz do repositório. A suíte verifica contratos selecionados e exemplos básicos, sem garantir validade para qualquer geometria ou conjunto de parâmetros. Acrescentar testes pequenos que exercitem mudanças de comportamento; a validação de um caso OpenFOAM inclui a conversão e a leitura do relatório de `checkMesh`.
