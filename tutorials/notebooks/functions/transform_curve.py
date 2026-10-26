import numpy as np

def transform_curve(
    curve: np.ndarray,
    *,
    dx: float = 0.0,
    dy: float = 0.0,
    theta: float = 0.0,
    center: np.ndarray | None = None,
) -> np.ndarray:
    """Rotaciona uma curva 2D em torno do seu próprio centro e depois translada"""
    theta = np.deg2rad(theta)
    curve = np.asarray(curve, dtype=float)
    if curve.ndim != 2 or curve.shape[1] != 2:
        raise ValueError("curve deve ter forma (n, 2).")

    if center is None:
        c = curve.mean(axis=0)     # centroide
    else:
        c = np.asarray(center, dtype=float).reshape(2)

    c_, s_ = np.cos(theta), np.sin(theta)
    R = np.array([[c_, -s_],
                  [s_,  c_]])

    # Rotação em torno de c  →  R @ (p - c) + c
    rotated = (curve - c) @ R.T + c

    # Translação final
    return rotated + np.array([dx, dy])