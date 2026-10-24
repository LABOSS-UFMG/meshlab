# MeshLab

**MeshLab** is a lightweight Python toolkit for mesh generation and manipulation.

The project is being developed for research and education in Computational Fluid Dynamics (CFD). Its main goal is to provide a simple and modular codebase that allows students to understand, implement, and test mesh generation algorithms.

# 1. Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/LABOSS-UFMG/meshlab
```

If you want to contribute to the project, follow the steps below.

# 2. Contributing to MeshLab

Follow these steps to set up your development environment.

## 2.1. Clone the repository

```bash
git clone git@github.com:LABOSS-UFMG/meshlab.git
cd meshlab
```

## 2.2. Create a virtual environment

```bash
python3 -m venv .venv
```

## 2.3. Activate the virtual environment

```bash
source .venv/bin/activate
```

You should now see `(.venv)` in your terminal prompt.

## 2.4. Install MeshLab in development mode

```bash
pip install -e .[dev]
```

where

- `-e` installs the package in editable mode;
- `[dev]` installs the development dependencies.

## 2.5. Development workflow

The project follows a simple Git workflow with two permanent branches:

- `main` contains the stable version of the project.
- `dev` is the development branch where all new features and bug fixes are implemented.

Before starting your work, switch to the `dev` branch:

```bash
git checkout dev
git pull
```

After implementing your changes, commit and push them to the `dev` branch:

```bash
git add .
git commit -m "Implement new smoothing algorithm"
git push origin dev
```

**Do not commit directly to the `main` branch.**

The `main` branch should only be updated after the new features have been reviewed and tested.

# 3. Project structure

The project is organized into four main modules.

```
meshlab/

├── data/          # Data structures
├── operations/    # Mesh generation and manipulation algorithms
├── export/        # Interfaces with gmsh
├── visualization/ # Visualization utilities
└── utils/         # Utility functions
```

The code is intentionally organized so that new features can usually be implemented by modifying a single file.

# 4. Documentation

The package is documented using NumPy-style docstrings.

Every new function or class should include:

- a short description;
- documentation of the input parameters;
- documentation of the returned values (when applicable).

# 5. Running the tutorials

The `tutorials/` directory contains simple scripts demonstrating the main features of the package.

For example,

```bash
python examples/square.py
```

# 6. Running the tests

Run all unit tests with

```bash
pytest
```

The unit tests must be update when a new feature is included or a modification is made.

Ficou muito bom! Agora eu quero a sua ajuda com a parte de criar a malha final a partir do gmsh. Como você sugere que seja a estrutura de pastas e arquivos para fazer esse processo? A exportação deve seguir o que foi feito no método anterior. O objetivo é exportar a malha para ser utilizada no openfoam. Como estava, estava funcionando normalmente. Agora eu quero fazer uma alteração, porque eu quero dois tipos de exportação: 1) como estava sendo feito com uma malha 2D e um elemento na direção d espessura; e 2) uma malha axissimétrica com um eixo de revolução. Isso é feito definindo um eixo e rotacionando um ângulo pequeno em torno dele. O eixo de revolução vai ser definido por uma curva (nesse caso a curva vai definir uma reta).