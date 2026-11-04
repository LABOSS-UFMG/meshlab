# Introdução

O pacote `meshlab` adota um estilo de programação predominantemente procedural. Classes representam as entidades geométricas e a malha, e funções implementam as etapas de geração. O usuário combina essas operações para construir a malha camada a camada.



As classes, funções de implementação e o código auxiliar são agrupados em 5 módulos:

| Pasta do pacote | Responsabilidade |
|---|---|
| [core](2%20-%20Core.md) | Define as estruturas de dados que representam a geometria, a malha e os parâmetros de refinamento. |
| [operations](3%20-%20Operations.md) | Implementa as operações de geração de malha em funções com responsabilidades específicas. |
| [export](4%20-%20Export.md) | Usa o Gmsh para preencher a região ainda sem malha e gravar a malha em formato .msh com seus grupos físicos. |
| [utils](5%20-%20Utils.md) | Implementa funções auxiliares como visualização da malha e validação. |
| [pipelines](6%20-%20Pipelines.md) | Implementa procedimentos de geração de malha completos prontos para serem aplicados a casos reais. |

A partir dos módulos descritos acima, é possível definir o fluxo de implementação da geração de malha a partir de 4 etapas, definidas por:

1. **Representação da geometria**
    - **Módulo:** `meshlab.core`
    - **Descrição:** as curvas e os contornos que delimitam o domínio são definidas.

2. **Preparação das frentes de avanço**
    - **Módulo:** `meshlab.operations`
    - **Descrição:** os contornos são incorporados à malha e as frentes de avanço são inicializadas nos trechos selecionados.
    
3. **Geração das camadas:**
    - **Módulo:** `meshlab.operations`
    - **Descrição:** a cada passo, é calculado as direções de avanço e acrescentado uma camada à malha. Conforme necessário, o módulo suaviza essas direções e colapsa arestas curtas.

4. **Preenchimento e exportação da malha:**
    - **Módulo:** `meshlab.export`
    - **Descrição:** a região restante do domínio é preenchida com elementos triangulares. Em seguida, é gerado a malha volumétrica por extrusão ou revolução e a grava em formato .msh.

A implementação do fluxo descrito anteriormente a partir das funções de `meshlab.operations` permite a criação de fluxos personalizados. Caso se deseje uma aplicação rápida, pode-se utilizar fluxos prontos de `meshlab.pipelines`.

Operações como refino tanto da malha superficial quanto da malha volumétrica podem ser incorporadas nas etapas descritas anteriormente. Esse procedimento é apresentado nos tutoriais.

Os tutoriais estão organizados em duas pastas: a pasta `notebooks` reúne os exemplos de geração de malhas em Jupyter notebooks; e a pasta `openfoam` contém os casos de simulação que utilizam essas malhas.
