"""Plot the coefficient and initial-residual histories from a run starting at 0."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    post = Path(__file__).resolve().parent / "postProcessing"
    coeff = np.loadtxt(post / "forceCoeffsCompressible/0/forceCoeffs.dat", ndmin=2)
    # The residuals at iteration zero are "N/A" because no equation was solved.
    resid = np.genfromtxt(post / "residuals/0/residuals.dat", ndmin=2)
    resid = resid[resid[:, 0] > 0]

    fig, axes = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True,
                             constrained_layout=True)
    for i, name in enumerate(("Cm", "Cd", "Cl"), start=1):
        axes[0].plot(coeff[:, 0], coeff[:, i], label=name)
    for i, name in enumerate(("p", "Ux", "Uy", "h", "k", "ω"), start=1):
        axes[1].semilogy(resid[:, 0], resid[:, i], label=name)
    axes[0].set_title("NACA-2412 multi-elemento · conjunto completo")
    axes[0].set_ylabel("Coeficiente")
    axes[1].set_ylabel("Resíduo inicial")
    axes[1].set_xlabel("Iteração de pseudo-tempo")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(ncol=3)
    fig.savefig(post / "historicos.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
