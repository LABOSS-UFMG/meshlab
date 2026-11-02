# Whitcomb supercrítico — aerodinâmica transônica estacionária

Tutorial 2D para o OpenFOAM Foundation 13. O módulo compressível `fluid` resolve as equações RANS com k–ω SST, gás perfeito, entalpia sensível e viscosidade de Sutherland. O campo distante é subsônico (Mach 0,75); a aceleração local sobre o perfil pode gerar uma região supersônica. Busca-se uma solução estacionária com passo de tempo local (`localEuler`) e correção de pressão `transonic yes`. Os índices de saída são passos de pseudo-tempo, não segundos físicos.

## Condições de referência

Editar [constant/caseParameters](constant/caseParameters) **antes** de executar. O arquivo alimenta os campos iniciais, a termodinâmica e a normalização das forças.

| Parâmetro | Padrão |
|---|---:|
| Mach e ângulo de ataque | 0,75 e 2° |
| Pressão e temperatura estáticas | 101325 Pa e 288,15 K |
| Corda e espessura extrudada | 1 m e 0,1 m |
| Intensidade turbulenta e razão de viscosidades | 0,1% e 10 |

Para mudar a incidência, editar somente `angleOfAttack`, em graus. A velocidade e os eixos de arrasto e sustentação giram juntos no plano x–y: arrasto paralelo a (cos α, sen α, 0), sustentação paralela a (−sen α, cos α, 0). O momento positivo segue a regra da mão direita em torno de +z, com centro em 25% da corda. A área de referência é corda × espessura = 0,1 m².

A velocidade é calculada de Mach e temperatura; a densidade, da equação de estado. O valor de k é 1,5 (I U∞)² e ω é k/[(νt/ν) ν∞]. A superfície `surface` é aderente e adiabática, com funções de parede para SST. As faces `frontAndBack` são `empty`. No contorno externo, velocidade e pressão usam condições de corrente livre, e T, k e ω permitem entrada e saída.

## Executar e verificar

Com o ambiente OpenFOAM 13 carregado, executar `./Allrun` nesta pasta. O script verifica a malha fornecida em `constant/polyMesh` e inicia o cálculo do zero. São 3000 iterações, sem parada antecipada por resíduo, com gravação de campos a cada 100. Para comparar ângulos, executar cada condição numa cópia separada: uma nova execução pode sobrescrever os resultados anteriores.

- [Coeficientes](postProcessing/forceCoeffsCompressible/0/forceCoeffs.dat): Cm, Cd e Cl da parede, por iteração. Usar os nomes e a ordem das colunas do cabeçalho.
- [Resíduos](postProcessing/residuals/0/residuals.dat): resíduos iniciais das equações de p, componentes ativas de U, h, k e ω. O [log do solver](log.foamRun) contém também resíduos finais, iterações lineares e erros de continuidade.
- Nos diretórios numéricos, inspecionar `Ma` para localizar a região supersônica e `yPlus` para avaliar a resolução junto à parede.

Avaliar a convergência pela queda dos resíduos **e** pela estabilização das cargas. Para resultados quantitativos, verificar também sensibilidade à malha, ao tratamento de parede e à distância do contorno externo.

A malha Whitcomb contém 11446 células e 206 faces no patch `surface`. Os parâmetros de corrente livre, a espessura extrudada, a referência do momento e os eixos de força são os mesmos do [NACA-2412](../NACA-2412/README.md).

## Diferenças numéricas em relação ao NACA-2412

A partida uniforme com os controles exatos do NACA (`steadyState`) falhou na atualização termodinâmica no passo 7. O cálculo entregue parte da mesma corrente livre uniforme. Os ajustes são restritos à marcha numérica:

| Controle | NACA-2412 | Whitcomb |
|---|---|---|
| Marcha para o regime estacionário | `steadyState` | `localEuler`, CFL local 0,2 e passo máximo 5×10⁻⁶ s |
| Correções externas / de pressão por correção externa | 1 / 1 | 2 / 2 |
| Sub-relaxação | Fatores explícitos para campos e equações | Sem fatores adicionais; o passo local limita a atualização |
| Solução linear | Sistemas de p, U, h, k e ω | Mesmos métodos; inclui sistema diagonal de ρ e entradas para a última correção |

A discretização espacial, o solver `fluid`, o SST e os parâmetros físicos são os do NACA. A condição de parede e a integração dos coeficientes foram associadas a `surface`. Os resíduos se referem às equações discretizadas em cada marcha: para comparar os perfis, verificar primeiro a estabilização dos coeficientes e o balanço de massa, sem tomar 3000 passos como prova de convergência.

## Resultado na iteração 3000

Os 30 conjuntos de campos foram gravados de 100 em 100 passos. Os históricos de resíduos e coeficientes cobrem as iterações 1 a 3000 sem lacunas, além da linha inicial. O campo final tem Mach máximo 0.934 (0 células supersônicas).

| Coeficiente | Iteração 3000 | Faixa nas últimas 100 |
|---|---:|---:|
| Cm | 0.078886 | 0.078086–0.078886 |
| Cd | 0.103293 | 0.103293–0.104443 |
| Cl | 0.165710 | 0.164188–0.165710 |

Nesta amostra não há região supersônica. Os coeficientes ainda exibem deriva; o campo final não comprova um regime estacionário convergido nem permite concluir, sozinho, como o choque difere entre os dois perfis. Os resultados e o log foram transferidos da cópia de execução após conferir a identidade da malha, dos campos iniciais e dos dicionários ativos.
