# MeshLab

O MeshLab é um pacote Python para geração de malhas com foco em problemas de aerodinâmica externa, em especial na geração de camada limite. O pacote utiliza a API Python do Gmsh para exportar as malhas no formato `.msh`.

## Versões e branches

O desenvolvimento do pacote segue duas branches:

- **`dev`:** reúne o desenvolvimento mais recente. Toda modificação começa em uma branch criada a partir da `dev` e volta para ela por meio de um *pull request*.
- **`main`:** recebe as alterações da `dev` que já foram revisadas e testadas e estão prontas para lançamento. A cada lançamento, a equipe publica uma **tag** no commit correspondente da `main`. A tag identifica aquela versão exata, mesmo depois que a branch recebe outras alterações.

O projeto adota o [versionamento semântico](https://semver.org/lang/pt-BR/), sendo a primeira versão estável **1.0.0**. Os três números indicam o impacto de uma atualização sobre quem usa o pacote:

| Mudança | Exemplo a partir de `1.0.0` |
|---|---|
| Correção de uma falha, preservando a interface documentada | `1.0.1` |
| Nova funcionalidade compatível com o código existente | `1.1.0` |
| Mudança incompatível, como a remoção de uma função pública | `2.0.0` |

## Instalação

Para instalar a versão atual de desenvolvimento ou a primeira versão estável quando publicada, você precisa de Python 3.10 ou superior e Git.

1. **Crie um ambiente virtual, se desejar.** Na pasta em que pretende trabalhar, execute:

   ```bash
   python -m venv .venv
   ```

   Para ativá-lo, use `source .venv/bin/activate` no Linux ou macOS, ou `.\.venv\Scripts\Activate.ps1` no PowerShell do Windows.

2. **Instale a versão desejada.** Para o uso do pacote, é recomendado instalar através de um tag específica. Caso instale outra branch não será possível assegurar compatibilidade com algum código já existente. A branch `dev` pode ser instável.

   | Origem | Comando |
   |---|---|
   | `main` — conteúdo atual da branch de lançamentos | `python -m pip install "git+https://github.com/LABOSS-UFMG/meshlab.git@main"` |
   | `dev` — alterações mais recentes em desenvolvimento | `python -m pip install "git+https://github.com/LABOSS-UFMG/meshlab.git@dev"` |
   | Tag — versão específica, por exemplo `v1.0.0` após sua publicação | `python -m pip install "git+https://github.com/LABOSS-UFMG/meshlab.git@v1.0.0"` |

3. **Confira a instalação.** O comando a seguir imprime a versão instalada:

   ```bash
   python -c "import meshlab; from importlib.metadata import version; print(version('meshlab'))"
   ```

## Tutoriais e documentação

Os tutoriais estão organizados em duas pastas. A primeira mostra como usar o pacote para gerar e exportar malhas, e a segunda utiliza algumas dessas malhas em simulações de aerodinâmica externa no OpenFOAM. A documentação apresenta a estrutura do pacote e descreve os algoritmos de cada operação, permitindo entender como a malha é construída.

## Como contribuir

As contribuições são feitas em branches do próprio repositório `LABOSS-UFMG/meshlab`. Para publicar sua branch, você precisa de acesso de escrita. Se ainda não tiver essa permissão, solicite-a a um mantenedor.

1. **Clone o repositório.** Se já tiver um clone do projeto, abra a pasta `meshlab` e siga para o passo 2.

   ```bash
   git clone https://github.com/LABOSS-UFMG/meshlab.git
   cd meshlab
   ```

2. **Crie uma branch a partir da `dev` atualizada.** Escolha um nome que descreva sua contribuição. O exemplo usa `melhoria-instalacao`.

   ```bash
   git fetch origin
   git switch --no-track -c melhoria-instalacao origin/dev
   ```

3. **Prepare o ambiente e faça a alteração.** Na raiz do repositório, instale o pacote em modo editável:

   ```bash
   python -m pip install -e ".[dev]"
   ```

    Edite o código, a documentação ou os tutoriais e execute os testes com `python -m pytest`.

4. **Registre a alteração e publique sua branch.** Confira os arquivos modificados com `git status` e adicione os que fazem parte da contribuição. Para uma alteração neste README, por exemplo:

   ```bash
   git add README.md
   git commit -m "Esclarece as instruções de instalação"
   git push -u origin melhoria-instalacao
   ```

5. **Abra um pull request para a `dev`.** No GitHub, acesse **Pull requests → New pull request** no repositório do projeto. Escolha `dev` como destino (**base**) e sua branch como origem (**compare**). Clique em **Create pull request** e descreva o que mudou e como testou. A equipe revisará a contribuição antes de incorporá-la à `dev`.

## Lançamento de uma nova versão

Prepare a versão na `dev` pelo fluxo de contribuição, atualize o campo `version` do `pyproject.toml` e execute `python -m pytest`. Com os testes aprovados, incorpore a `dev` à `main` por pull request. O exemplo a seguir utiliza a tag da primeira versão `v1.0.0`.

1. **Confira o commit de lançamento.** Atualize sua `main` local e confirme que o commit exibido corresponde ao lançamento aprovado.

   ```bash
   git switch main
   git pull --ff-only origin main
   git log -1 --oneline
   ```

2. **Crie a tag e publique-a no GitHub.** O primeiro comando marca o commit atual com a tag anotada `v1.0.0`. O segundo envia essa tag ao repositório do projeto.

   ```bash
   git tag -a v1.0.0 -m "Primeira versão estável do MeshLab"
   git push origin v1.0.0
   ```
