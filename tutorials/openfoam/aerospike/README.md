# Aerospike axissimétrico — OpenFOAM Foundation 13

Caso de expansão de gás por um aerospike e interação da pluma com o ambiente.
A malha representa um setor de 5° em torno do eixo x, com patches `wedge`.
A câmara e o convergente não fazem parte do domínio: `inlet` é a garganta.
Não há combustão, química, turbulência modelada ou transferência de calor
nas paredes. O gás é perfeito, com calor específico constante e transporte
de Sutherland. É um caso idealizado para estudar a malha e o escoamento.

## Parâmetros e entrada

Editar `constant/caseParameters`. Esse arquivo é importado por `0/U`, `0/T`,
`0/p`, `constant/physicalProperties` e pelos monitores em `system/functions`.
Os parâmetros derivados usam `#calc` do OpenFOAM; a primeira leitura pode
compilar pequenas bibliotecas em `dynamicCode` e requer o ambiente de compilação.

| Parâmetro | Valor inicial | Significado |
|---|---:|---|
| `pReservoir` | 2 MPa absolutos | Pressão de estagnação |
| `TReservoir` | 3000 K | Temperatura de estagnação |
| `pAmbient` | 101325 Pa absolutos | Pressão ambiente e referência das forças |
| `TAmbient` | 300 K | Temperatura inicial e de retorno do ambiente |
| `molWeight` | 28,96 kg/kmol | Massa molar do gás equivalente |
| `Cv` | 718 J/(kg K) | Calor específico a volume constante |

Os valores de reservatório aproximam as condições implícitas na entrada antiga
(2500 K, 1,05656 MPa e 1002,4 m/s). Não são dados experimentais de um motor.
Calculam-se `Rgas = Ru/molWeight`, `Cp = Cv + Rgas` e `gamma = Cp/Cv`.

Assume-se garganta estrangulada, uniforme, com Mach 1 e expansão isentrópica
desde o reservatório:

```text
T* = 2 T0 / (gamma + 1)
p* = p0 [2 / (gamma + 1)]^[gamma / (gamma - 1)]
U* = sqrt(gamma R T*)
rho* = p* / (R T*)
mdot_ideal = rho* U* A_inlet
```

`T` e `p` usam os valores estáticos críticos calculados; `U` usa
`surfaceNormalFixedValue`, apontando para dentro do domínio com módulo `U*`.
Não se impõem 3000 K e 2 MPa como valores estáticos na garganta. O reservatório
é representado analiticamente; esta entrada não prevê desestrangulamento,
refluxo, perdas no convergente nem o perfil de camada limite vindo da câmara.
Para esses fenômenos, incluir o convergente/plenum e usar condições totais a montante.

Nas fronteiras laterais do ambiente, `totalPressure` representa um ambiente
em repouso; a velocidade permite entrada e saída. Na saída a jusante,
`waveTransmissive` permite propagação das ondas. A antiga chave `pInf` foi
removida porque não é usada por essa condição no OpenFOAM 13. Não há relaxação
da saída para uma pressão distante; verificar sensibilidade ao tamanho do domínio.

## Energia e pseudo-tempo

O módulo `shockFluid` usa `eConst` e `sensibleInternalEnergy`.
A incógnita térmica é a energia interna sensível `e`, mas o balanço inclui
energia total `E = e + |U|²/2`, trabalho de pressão, transporte de calor e
trabalho viscoso. Para malha fixa, sua forma conservativa é:

```text
d(rho E)/dt + div[rho U (E + p/rho)] = termos térmicos e viscosos
H = E + p/rho
```

Não se resolve `H` diretamente. A entalpia total aparece no fluxo de energia;
não se deve trocar o pacote termodinâmico para `sensibleEnthalpy` neste solver.

`localEuler` ativa passos locais para convergir ao regime estacionário.
Os rótulos de tempo representam iterações, não uma história física.
Usam-se fluxos `Kurganov` e reconstrução limitada `Minmod` para densidade,
velocidade e temperatura (esta última também controla a reconstrução de energia).
Uma correção externa por passo reduz o custo, sem sub-relaxação adicional.
O CFL local é `maxCo = 0.5`, com `rDeltaTSmoothingCoeff = 0.02`
em `system/fvSolution`; não há o teto
artificial de `1e-7 s` da configuração anterior. A suavização de `rDeltaT`
limita contrastes de passos entre células. Aumentar o CFL indiscriminadamente
pode provocar temperaturas negativas; rapidez não deve comprometer estabilidade.

## Vazão e forças

Os monitores são carregados por `controlDict` e gravados em `postProcessing`:

| Monitor | Resultado |
|---|---|
| `inletMassFlow` | Soma de `phi` na garganta, em kg/s |
| `spikeForces`, `ductBottomForces`, `ductTopForces`, `outerLipForces`, `outerCasingForces` | Pressão e viscosidade, por superfície |

São apenas seis monitores: vazão na entrada e cinco superfícies sólidas.
Gravam uma linha por iteração, além da amostra inicial. O objeto nativo `forces`
inclui também momentos no mesmo arquivo; não são gerados campos auxiliares,
monitor de força agregada, histórico de Mach ou de tensão na parede.

`phi` já é vazão mássica por face: usar **soma**, não integral de área.
A normal aponta para fora do fluido, portanto entrada tem sinal negativo:
`mdot_entrada = -sum(phi)`. O monitor registra o fluxo corrigido pelo solver;
compará-lo com `mdot_ideal`. Em regime estacionário, a soma nas aberturas deve
aproximar-se de zero. Durante LTS, o desequilíbrio não representa uma acumulação
em tempo físico global.

Em `postProcessing/<superfície>Forces/<início>/forces.dat`, cada linha tem:

```text
tempo ((Fx_p Fy_p Fz_p) (Fx_v Fy_v Fz_v)) ((Mx_p My_p Mz_p) (Mx_v My_v Mz_v))
```

As forças são do fluido sobre as paredes, em N: pressão (`p`) e contribuição
viscosa (`v`) separadas. A referência é `pAmbient`, isto é, integra-se a pressão
relativa ao ambiente. A parcela viscosa vem do tensor de tensões desviadoras;
pode conter componente normal, não apenas cisalhamento tangencial.
Mantiveram-se as paredes `slip`: elas não modelam o atrito de uma parede aderente.
Para perdas por atrito, usar `noSlip` e uma malha/modelo de transporte compatíveis.

As integrais correspondem ao setor. Para estimar a vazão e a força **axial**
no motor completo, multiplicar por `360/wedgeAngleDeg = 72` (aproximação do setor
discretizado). Não multiplicar os vetores transversais diretamente: suas
componentes se cancelam ao integrar a configuração axissimétrica completa.

A força nas paredes modeladas **não é, isoladamente, o empuxo total do motor**:
faltam as superfícies da câmara e do convergente. A vazão sozinha também não
determina empuxo. Um balanço completo requer fluxo de quantidade de movimento,
pressão e tensões nas seções de controle, com sinais e superfícies consistentes;
não somar indiscriminadamente `mdot U` à integral de todas as paredes.

## Execução e avaliação

Com o ambiente do OpenFOAM Foundation 13 carregado, executar `./Allrun` nesta
pasta. Ele importa a malha Gmsh, aplica os tipos de patch, executa `checkMesh`
e chama `foamRun`. Os logs recebem um sufixo único para preservar logs antigos
e impedir que sua existência faça `runApplication` pular etapas.
Os campos de solução e `postProcessing` de uma execução anterior podem ser
reescritos: executar em uma cópia do caso para preservar resultados anteriores.

O cálculo termina em 1000 passos, gravando campos em `100`, `200`, ..., `1000`.
Os históricos em `postProcessing` são gravados a cada passo.
Completar 1000 passos não certifica convergência.
Verificar resíduos, balanço de massa, estabilização das forças e independência
de malha/domínio antes de interpretar desempenho. Não há critério automático
de parada por convergência. O modelo de ar com calor específico constante a
alta temperatura é uma aproximação, não uma descrição dos produtos de combustão.
