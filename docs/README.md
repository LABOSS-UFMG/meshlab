# MeshLab — documentação de desenvolvimento

Esta documentação descreve o código atual e seus cálculos. Os exemplos de uso ficam nos [tutoriais](../tutorials/). As pastas `operations-old/` e `tutorials-old/` são referências históricas.

## Estrutura e leitura

| Pasta do pacote | Responsabilidade | Documentação |
|---|---|---|
| `core/` | Coordenadas, células, curvas, contornos, frentes e referências de refinamento | [Estruturas](core/README.md) |
| `operations/` | Montagem, normais, ângulos, suavização, avanço e colapso | [Operações](operations/README.md) |
| `export/` | Preenchimento residual, refinamento, extrusão/revolução e gravação Gmsh | [Exportação](export/README.md) |
| `utils/` | Validação dos construtores e visualização | [Validação](utils/validation.md), [visualização](utils/plot_mesh.md) |

## Fluxo implementado

1. Definir `Curve` e agrupá-las em `Contour`.
2. Inserir os contornos em `Mesh` com `insert_contour`; nomes e índices ficam em `mesh.boundaries`.
3. Criar `Front` independentes e selecionar as curvas ativas com `initialize_front`.
4. Calcular normais, opcionalmente suavizá-las e corrigir alturas, e executar `advance_front`.
5. Opcionalmente encontrar e colapsar arestas curtas; remapear outras frentes após compactação.
6. Usar `export_mesh` para preencher a região residual e gerar uma camada volumétrica planar ou axissimétrica, com refinamentos locais opcionais.
7. Converter o `.msh` com `gmshToFoam`, configurar os patches do caso e verificar com `checkMesh`.

As classes guardam dados e as funções operam sobre eles. Não há `Domain` nem objeto global de malha. O código de camadas não depende de uma sessão Gmsh aberta.

## Dimensões e limites

`Mesh(dim=2|3)` mantém a mesma interface de armazenamento; os blocos atuais são triângulos e quadriláteros. O avanço, o colapso e o preenchimento residual são planares. A exportação por extrusão/revolução não equivale à geração geral de camadas 3D.

Não há detecção global de colisões, união de frentes independentes ou proteção automática contra sobreposição no avanço. O colapso verifica apenas suas células incidentes. Guias são retas; a projeção pode extrapolar o segmento se o passo escolhido for inadequado.

Redistribuição de pontos e um coordenador geral continuam como possibilidades futuras, resumidas em [curvas](operations/curves.md) e [coordenação](generation/README.md). Essas pastas propostas não são módulos implementados.

## Tutoriais atuais

| Arquivo | Conteúdo |
|---|---|
| `t0.ipynb` | Curvas e contornos de dois corpos em domínio retangular |
| `t1.ipynb` | Avanço manual e em laço ao redor de um círculo |
| `t3.ipynb` | Geometria em L, normais, suavização e dez camadas com colapso |
| `t4.ipynb` | Canal com canto e frentes guiadas nas paredes |
| `t5.ipynb` | Aerofólio e exportação para OpenFOAM |
| `t6.ipynb` | Dois corpos e refinamentos por ponto, curva e região fechada |

A suíte básica é executada com `.venv/bin/python -m pytest -q`. Os testes verificam contratos selecionados, não garantem validade de qualquer geometria ou conjunto de parâmetros.
