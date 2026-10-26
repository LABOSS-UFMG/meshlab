import numpy as np

def split_curve(
        curve: np.ndarray,
        n1: int,
        t1: np.ndarray,
        n2: int,
        t2: np.ndarray,
        r: float,
    ) -> list[np.ndarray]:
    
    # Passo médio local
    diff_curve = np.diff(curve, axis=0)                # (n-1, 2)
    delta_s = np.linalg.norm(diff_curve, axis=1)       # (n-1,)
    ds = 0.5 * (delta_s[n1] + delta_s[n2]) / 2

    P1 = curve[n1]                                      # (2,)
    P2 = curve[n2]                                      # (2,)

    # Interseção das retas P1 + s·t1  e  P2 + u·t2
    A = np.column_stack((t1, -t2))
    b = P2 - P1
    try:
        s, u = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        raise ValueError("As retas definidas por t1 e t2 são paralelas.")

    if s < 0 or u < 0:
        raise ValueError("As retas não se cruzam no sentido positivo de t1 e t2.")

    P = P1 + s * t1

    # Ângulo interno do canto
    cos_theta = np.clip(np.dot(t1, t2), -1.0, 1.0)
    theta = np.arccos(cos_theta)
    if theta < 1e-12 or theta > np.pi - 1e-12:
        raise ValueError("Ângulo degenerado; filete impossível.")

    d = r / np.tan(theta / 2.0)
    if s < d or u < d:
        raise ValueError("O raio r é grande demais para os segmentos dados.")

    T1 = P - d * t1
    T2 = P - d * t2

    # Centro da circunferência
    b_vec = (-t1) + (-t2)
    b_vec /= np.linalg.norm(b_vec)
    C = P + (r / np.sin(theta / 2.0)) * b_vec

    # Sentido do arco
    cross = t1[0] * t2[1] - t1[1] * t2[0]
    direction = -np.sign(cross)
    if direction == 0:
        direction = 1.0

    phi = np.pi - theta   # ângulo central do arco

    # ---------- discretização: número de elementos ≈ L / ds ----------
    def n_elements(L, step):
        # arredonda para o inteiro mais próximo e garante pelo menos 1
        return max(1, int(L / step + 0.5))

    def points_on_segment(A_pt, B_pt, step):
        v = B_pt - A_pt
        L = np.linalg.norm(v)
        if L < 1e-12:
            return np.empty((0, 2))
        k = n_elements(L, step)
        tt = np.linspace(0.0, 1.0, k + 1)[1:]           # exclui A_pt
        return A_pt[None, :] + v[None, :] * tt[:, None]  # (k, 2)

    def points_on_arc(C_pt, Ta, Tb, radius, step, direction, phi):
        a1 = np.arctan2(Ta[1] - C_pt[1], Ta[0] - C_pt[0])
        a2 = a1 + direction * phi
        L = radius * phi
        if L < 1e-12:
            return np.empty((0, 2))
        k = n_elements(L, step)
        angles = np.linspace(a1, a2, k + 1)[1:]          # exclui Ta
        pts = np.empty((k, 2))
        pts[:, 0] = C_pt[0] + radius * np.cos(angles)
        pts[:, 1] = C_pt[1] + radius * np.sin(angles)
        pts[-1] = Tb                                     # fecha exatamente em Tb
        return pts

    # ---------- novo caminho: P1 → T1 → arco → T2 → P2 ----------
    new_path_parts = [P1[None, :]]
    seg1 = points_on_segment(P1, T1, ds)
    if seg1.shape[0] > 0:
        new_path_parts.append(seg1)
    arc = points_on_arc(C, T1, T2, r, ds, direction, phi)
    if arc.shape[0] > 0:
        new_path_parts.append(arc)
    seg2 = points_on_segment(T2, P2, ds)
    if seg2.shape[0] > 0:
        new_path_parts.append(seg2)

    new_path = np.concatenate(new_path_parts, axis=0)
    new_path[0] = P1
    new_path[-1] = P2

    # ---------- trechos da curva original ----------
    def get_curve_segment(curve, i, j):
        if i <= j:
            return curve[i:j + 1]
        return np.concatenate((curve[i:], curve[1:j + 1]), axis=0)

    partA = get_curve_segment(curve, n1, n2)   # n1 → n2 (ordem original)
    partB = get_curve_segment(curve, n2, n1)   # n2 → n1 (ordem original)

    # ---------- duas curvas fechadas ----------
    curve1 = np.concatenate((partB, new_path[1:]),      axis=0)  # n2→n1 + (n1→n2 novo)
    curve2 = np.concatenate((partA, new_path[-2::-1]),  axis=0)  # n1→n2 + (n2→n1 novo)

    return [curve1, curve2]