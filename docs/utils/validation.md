# `utils/validation.py` — verificações e testes

**Status:** validadores existentes usados pelos construtores; critérios geométricos adicionais permanecem planejados.

## Organização e política

Manter as verificações reutilizáveis em `meshlab/utils/validation.py`, sem criar um pacote paralelo `meshlab/validation/`. As classes chamam os validadores durante a construção; métodos de inserção e alterações diretas nos arrays não repetem essas verificações. `Mesh.dim` ainda é verificado diretamente no construtor.

Critérios de aceitação geométrica de uma camada, colapso ou união são parte das operações propostas. Não se deve atribuir essas garantias a `Mesh.add_cell` ou ao armazenamento de `Front`.

## Cobertura atual dos construtores

| Estrutura | Verificações explícitas |
|---|---|
| `Mesh` | Dimensão, capacidades, fator de crescimento e tipos NumPy |
| `CellBlock` | Largura, capacidade, fator de crescimento e tipo inteiro |
| `Curve` | Tipo de ponto flutuante |
| `Contour` | Junções de curvas através de `is_contour` |
| `Front` | Tipo inteiro configurado |

Os auxiliares genéricos `is_int`, `is_sequence`, `is_object` e `is_union` também permanecem no módulo para seus chamadores existentes.

## Limites observados

- `is_positive_float` aceita zero e valores menores ou iguais a um; não garante o fator maior que um mencionado nas docstrings de capacidade. O crescimento ainda usa no mínimo uma linha adicional.
- `is_positive_int` usa `int` de Python, embora a docstring mencione inteiros NumPy, e avalia finitude antes de concluir a checagem de tipo.
- `Curve` não verifica explicitamente nome, forma ou validade geométrica dos pontos.
- `is_contour` verifica junções e fechamento. Não verifica explicitamente lista vazia, tolerância ou auto-interseções.
- `Front` não tem acesso à malha para verificar a existência dos vértices. Arestas válidas como armazenamento não garantem uma frente geometricamente válida.

Essas observações descrevem o código atual. A atualização documental não modifica os validadores nem amplia os testes.

## Testes básicos

A suíte de `tests/core/` contém seis casos:

| Arquivo | Cobertura |
|---|---|
| `mesh_test.py` | Inserção, crescimento e conectividade em 2D e 3D, com os tipos configurados |
| `curve_test.py` | Nome, ordem, precisão e cópia das coordenadas |
| `contour_test.py` | Composição e armazenamento de duas curvas |
| `front_test.py` | Frente vazia e cópia da conectividade fornecida |

Executar na raiz do repositório:

```bash
.venv/bin/python -m pytest tests/core -q
```

A verificação em 23/10/2026 passou nos seis casos. São testes mínimos de funcionamento, não uma cobertura exaustiva dos validadores. A árvore atual contém os seis casos de `tests/core/` e dois testes de montagem em `tests/operations/assembly_test.py`: canal com frentes independentes e inserções sucessivas em 3D. Os oito casos passaram após esta implementação. O resultado não comprova o funcionamento das operações legadas ou da integração Gmsh.

## Critérios futuros das operações

Os itens abaixo são propostas para a evolução dos algoritmos, não uma exigência de adicionar agora todos os respectivos testes. Acrescentar apenas casos essenciais quando cada funcionalidade for implementada.

## Validade e qualidade

Validade é uma condição obrigatória; qualidade é avaliada em relação à aplicação. Elementos alongados podem ser adequados à camada limite. Não usar proximidade a um quadrado ou triângulo equilátero como objetivo universal.

Para triângulos planos, verificar orientação e área acima da tolerância. Para quadriláteros lineares, verificar simplicidade, orientação e critérios locais de jacobiano/convexidade compatíveis com a representação adotada. Área total positiva, isoladamente, não é suficiente. A proposta inicial é aceitar quadriláteros convexos não degenerados.

Elementos individualmente válidos ainda podem se sobrepor. A aceitação precisa considerar também interseções e cobertura da região.

## Invariantes principais

- Nenhuma conectividade referencia índices fora da faixa válida ou usa `-1` como vértice.
- Junções declaradas compartilham um nó global.
- Fronteiras físicas conservam nome e associação geométrica.
- A frente representa a separação entre região construída e residual.
- Pontos guiados permanecem na guia dentro da tolerância.
- Operações rejeitadas preservam o estado anterior na abrangência prometida.
- Renumerações atualizam todas as referências.
- A malha final é conforme nas interfaces internas, sem nós pendurados não previstos.

## Casos de referência

| Caso | O que deve demonstrar |
|---|---|
| Reta e arco redistribuídos | Extremos, ordem e distribuição prescrita |
| Monitor constante | Equivalência à distribuição uniforme na medida adotada |
| Duas curvas ativas | Nó único e vizinhança atravessando a junção |
| Canal com entrada e saída | Ausência de camadas nessas curvas e extremos guiados |
| Guia curva | Permanência sobre a geometria após passo finito |
| Aerofólio composto | Preservação dos nomes e domínio com um furo |
| Dois corpos | Detecção de aproximação e região residual consistente |
| Colapso | Atualização de conectividade, tipos e mapas |
| Camada mista exportada | Triângulos e quadriláteros corretamente transferidos |
| Saída 2D e pseudo-2D | Distinção de dimensões e grupos físicos |

## Tolerâncias

Separar tolerância numérica dos predicados, tolerância de conexão geométrica e limiares de qualidade/proximidade. Definir escalas relativas ao tamanho do problema e à discretização. Não espalhar constantes independentes pelos módulos.
