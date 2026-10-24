# Coordenação da geração

Não existe módulo `meshlab/generation/`. O ciclo de camadas fica explícito nos tutoriais: calcular normais, suavizar opcionalmente, calcular alturas, avançar e, quando solicitado, colapsar arestas curtas.

O crescimento usual é `h_k = h_0 * r**k`. A exportação é uma chamada posterior a `export_mesh`, independente da visualização. O número de camadas e os parâmetros são controlados pelo chamador.

Um coordenador reutilizável, critérios automáticos de parada, ajuste de passo por colisão e recuperação de falhas permanecem possibilidades futuras, sem API definida.
