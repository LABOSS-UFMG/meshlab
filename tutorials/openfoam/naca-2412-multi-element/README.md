# NACA-2412 multi-elemento — Mach 0,2

Escoamento externo bidimensional no conjunto formado por slat, elemento principal (`body`) e flap. O caso usa o solver compressível `fluid` do OpenFOAM Foundation 13, gás perfeito, viscosidade de Sutherland e turbulência RANS k–ω SST. A corrente livre tem Mach 0,2, pressão estática de 101325 Pa e temperatura de 288,15 K (velocidade de aproximadamente 68,1 m/s). A incidência padrão é **20°**, conforme a configuração original do multi-elemento.

## Parâmetros e condições de contorno

Editar [constant/caseParameters](constant/caseParameters) para mudar `MachInf`, `angleOfAttack` em graus ou as condições de referência. A velocidade é calculada a partir de Mach e temperatura. A intensidade turbulenta de corrente livre é 0,1% e a razão entre viscosidades turbulenta e molecular é 10. O modelo usa `h` como variável térmica. Nas três paredes aderentes, a temperatura tem gradiente normal nulo; as faces dianteira e traseira da extrusão são `empty`.

A incidência positiva produz uma componente de velocidade em +y. As direções de arrasto e sustentação giram juntas com a corrente livre. Para **todos** os coeficientes, a corda de referência é a nominal do perfil de origem (1 m), a espessura da extrusão é 0,1 m e a área de referência é 0,1 m². O momento é positivo pela regra da mão direita em torno de +z, com centro em (0,25; 0; 0,05) m. Assim, as contribuições individuais podem ser somadas, inclusive o momento.

## Execução e saídas

Com o ambiente do OpenFOAM 13 carregado, executar `./Allrun` na pasta do caso. O script converte a malha Gmsh, atribui os tipos de patch, verifica a malha e executa o cálculo do zero. Para preservar uma condição antes de rodar outra incidência, usar uma cópia da pasta.

- [Coeficientes do conjunto](postProcessing/forceCoeffsCompressible/0/forceCoeffs.dat): uma linha por iteração, com Cm, Cd e Cl.
- Coeficientes individuais: [slat](postProcessing/slatCoeffs/0/forceCoeffs.dat), [elemento principal](postProcessing/bodyCoeffs/0/forceCoeffs.dat) e [flap](postProcessing/flapCoeffs/0/forceCoeffs.dat).
- [Resíduos das equações](postProcessing/residuals/0/residuals.dat): p, Ux, Uy, h, k e ω. A linha inicial não tem resíduos pois ainda não houve solução linear. O [log](log.foamRun) inclui também resíduos finais e erros de continuidade.
- Campos de solução, Mach (`Ma`) e `yPlus`: gravados a cada 100 iterações. Avaliar a estabilização dos coeficientes, os resíduos e a resolução de parede antes de interpretar as cargas.

## Marcha numérica e malha

Busca-se o regime estacionário usando passos locais de pseudo-tempo (`localEuler`), não uma evolução em tempo físico. A correção transônica de pressão está desligada para esta condição subsônica. O bloco PIMPLE usa CFL local 0,4, passo máximo de 2×10⁻⁵ s, uma correção externa e duas de pressão. A solução linear da pressão usa PCG/DIC. A execução não para antecipadamente por resíduo.

A malha fornecida tem 30889 células. O [checkMesh](log.checkMesh) identificou 12 faces de skewness elevada (máximo 7,79); portanto, a malha não passou em todos os critérios. A tentativa anterior com `steadyState` falhou na atualização da função de parede de ω no primeiro passo; o log, por si só, não estabelece a causa. A marcha local foi usada sem alterar a geometria. Antes de usar as cargas para previsão de desempenho, verificar sensibilidade ao refinamento e às faces sinalizadas, y⁺ e estabilização dos históricos.
