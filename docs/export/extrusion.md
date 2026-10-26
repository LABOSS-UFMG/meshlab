# `export/extrusion.py` — translação e revolução

`extrude_mesh` importa a seção híbrida como superfícies discretas e usa uma única camada de elementos, com recombinação. Retorna tags, coordenadas, blocos volumétricos e o referencial usado para classificar faces.

## Planar

Insere a seção em `z=0` e aplica translação `(0, 0, thickness)`. Triângulos normalmente produzem prismas e quadriláteros produzem hexaedros.

## Axissimétrico

O primeiro e o último ponto de `axis` definem origem `o` e direção unitária `a`. O eixo deve ser reto e não nulo, e a seção deve estar de um único lado dele. A direção é ajustada para que o lado radial médio seja positivo.

A função `rotate` aplica a fórmula de Rodrigues a `v = p - o`:

```text
p_rot = o + v cos(theta) + (a × v) sin(theta)
        + a (a · v) (1 - cos(theta))
```

A seção é posicionada em `-angle/2` e varrida por `angle`, centrando a cunha no plano original. O Gmsh trata os nós sobre o eixo e remove nós duplicados após gerar os volumes. Os blocos capturados suportam tetraedros, hexaedros, prismas e pirâmides.

Células incidentes ao eixo podem degenerar, dependendo de sua topologia; a verificação de jacobiano em `export_mesh` rejeita volumes inválidos, sem repará-los. Eixos curvos, seções atravessando o eixo e geração geral de camadas 3D não são suportados.
