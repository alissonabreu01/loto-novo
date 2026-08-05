from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class GameFeatures:
    """Representa as características extraídas de um concurso da Lotofácil."""
    concurso: int
    data: str
    numbers: Tuple[int, ...]

    # Estruturais básicos
    soma: int
    pares: int
    impares: int
    amplitude: int

    # Região do volante
    moldura: int
    miolo: int

    # Grupos numéricos
    primos: int
    fibonacci: int
    multiplos_3: int
    multiplos_4: int
    multiplos_5: int

    # Relação com concurso anterior (preenchido se houver contexto)
    repetidas: int | None
    novas: int | None

    # Sequências
    quantidade_blocos: int | None
    maior_bloco: int | None
    menor_bloco: int | None
    blocos: Tuple[int, ...] | None

    # Distribuição espacial
    linhas: Tuple[int, ...]
    colunas: Tuple[int, ...]

    # Informação
    entropia_blocos: float | None
