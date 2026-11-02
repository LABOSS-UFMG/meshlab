# NACA-2412 — aerodinâmica transônica estacionária

Tutorial 2D para o OpenFOAM Foundation 13. O módulo compressível `fluid` resolve as equações RANS com k–ω SST, gás perfeito, entalpia sensível e viscosidade de Sutherland. O campo distante é subsônico (Mach 0,75); a aceleração local sobre o perfil pode gerar uma região supersônica. O esquema temporal é `steadyState`, com correção de pressão `transonic yes`: os índices de saída são iterações, não segundos físicos.

## Condições de referência

Editar [constant/caseParameters](constant/caseParameters) **antes** de executar. O arquivo alimenta os campos iniciais, a termodinâmica e a normalização das forças.

| Parâmetro | Padrão |
|---|---:|
| Mach e ângulo de ataque | 0,75 e 2° |
| Pressão e temperatura estáticas | 101325 Pa e 288,15 K |
| Corda e espessura extrudada | 1 m e 0,1 m |
| Intensidade turbulenta e razão de viscosidades | 0,1% e 10 |

Para mudar a incidência, editar somente `angleOfAttack`, em graus. A velocidade e os eixos de arrasto e sustentação giram juntos no plano x–y: arrasto paralelo a (cos α, sen α, 0), sustentação paralela a (−sen α, cos α, 0). O momento positivo segue a regra da mão direita em torno de +z, com centro em 25% da corda. A área de referência é corda × espessura = 0,1 m².

A velocidade é calculada de Mach e temperatura; a densidade, da equação de estado. O valor de k é 1,5 (I U∞)² e ω é k/[(νt/ν) ν∞]. A superfície `wall` é aderente e adiabática, com funções de parede para SST. As faces `frontAndBack` são `empty`. No contorno externo, velocidade e pressão usam condições de corrente livre, e T, k e ω permitem entrada e saída.

## Executar e verificar

Com o ambiente OpenFOAM 13 carregado, executar `./Allrun` nesta pasta. O script verifica a malha fornecida em `constant/polyMesh` e inicia o cálculo do zero. São 3000 iterações, sem parada antecipada por resíduo, com gravação de campos a cada 100. Para comparar ângulos, executar cada condição numa cópia separada: uma nova execução pode sobrescrever os resultados anteriores.

- [Coeficientes](postProcessing/forceCoeffsCompressible/0/forceCoeffs.dat): Cm, Cd e Cl da parede, por iteração. Usar os nomes e a ordem das colunas do cabeçalho.
- [Resíduos](postProcessing/residuals/0/residuals.dat): resíduos iniciais das equações de p, componentes ativas de U, h, k e ω. O [log do solver](log.foamRun) contém também resíduos finais, iterações lineares e erros de continuidade.
- Nos diretórios numéricos, inspecionar `Ma` para localizar a região supersônica e `yPlus` para avaliar a resolução junto à parede.

Avaliar a convergência pela queda dos resíduos **e** pela estabilização das cargas. Para resultados quantitativos, verificar também sensibilidade à malha, ao tratamento de parede e à distância do contorno externo.

## Execução de referência: Mach 0,75 e α = 2°

Foram verificados os 30 conjuntos de campos (100 a 3000) e os históricos completos das 3000 iterações. Na linha 0, os resíduos aparecem como `N/A` porque nenhuma equação foi resolvida ainda. Na última iteração, o Mach local máximo foi 1,233, com 251 células supersônicas.

| Coeficiente | Iteração 3000 | Faixa nas últimas 100 iterações |
|---|---:|---:|
| Cm (+z, a ¼ da corda) | 0,05683 | 0,05681–0,05689 |
| Cd | 0,03732 | 0,03708–0,03732 |
| Cl | 0,38777 | 0,38756–0,38792 |

As cargas variaram pouco nessa janela, mas os resíduos de U e h ainda estavam entre 6×10⁻⁴ e 10⁻³. O y⁺ médio na parede foi aproximadamente 982 (máximo 1781), indicando resolução grosseira junto ao perfil. Estes resultados demonstram a execução transônica; para usar Cd quantitativamente, refinar a malha junto à parede e avaliar independência de malha e convergência iterativa.
