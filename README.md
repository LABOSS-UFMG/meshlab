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

```text
meshlab/
├── core/          # Mesh, curves, contours, fronts and refinement data
├── operations/    # Assembly and boundary-layer algorithms
├── export/        # Residual triangulation and Gmsh volume export
└── utils/         # Constructor validation and plotting

docs/              # Developer documentation, organized by source module
tutorials/         # Jupyter notebooks demonstrating the public workflow
tests/             # Basic automated checks
```

# 4. Documentation

See the [developer documentation](docs/README.md) for architecture, calculations and implementation limits. The package also uses NumPy-style docstrings.

Every new function or class should include:

- a short description;
- documentation of the input parameters;
- documentation of the returned values (when applicable).

# 5. Running the tutorials

Open the notebooks in [tutorials/](tutorials/) with Jupyter and execute their cells in order, using the environment where MeshLab is installed. Start with `t0.ipynb`; the [documentation index](docs/README.md#tutoriais-atuais) lists the remaining examples.

# 6. Running the tests

Run all unit tests with

```bash
pytest
```

The unit tests must be updated when a new feature is included or a modification is made.
