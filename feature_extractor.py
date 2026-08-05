from typing import List, Tuple, Optional
from game import Game
from game_features import GameFeatures


class FeatureExtractor:
    """Extrai características estatísticas e estruturais de um jogo da Lotofácil."""

    # Constantes para análise
    PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    FIBONACCI = {1, 2, 3, 5, 8, 13, 21}
    
    # Definição do volante (5x5)
    #  1  2  3  4  5
    #  6  7  8  9 10
    # 11 12 13 14 15
    # 16 17 18 19 20
    # 21 22 23 24 25
    MOLDURA = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}
    MIOLO = {7, 8, 9, 12, 13, 14, 17, 18, 19}

    def extract(self, game: Game, previous_game: Optional[Game] = None) -> GameFeatures:
        numbers = game.numbers

        # Cálculos básicos
        soma = sum(numbers)
        pares = len([n for n in numbers if n % 2 == 0])
        impares = len([n for n in numbers if n % 2 == 1])
        amplitude = max(numbers) - min(numbers)

        # Região do volante
        moldura = self._count_in_set(numbers, self.MOLDURA)
        miolo = self._count_in_set(numbers, self.MIOLO)

        # Grupos numéricos
        primos = self._count_in_set(numbers, self.PRIMOS)
        fibonacci = self._count_in_set(numbers, self.FIBONACCI)
        multiplos_3 = self._count_multiples(numbers, 3)
        multiplos_4 = self._count_multiples(numbers, 4)
        multiplos_5 = self._count_multiples(numbers, 5)

        # Relação com concurso anterior
        repetidas = None
        novas = None
        if previous_game:
            repetidas = len(set(numbers) & set(previous_game.numbers))
            novas = 15 - repetidas

        # Sequências e blocos
        blocos = self._calculate_blocks(numbers)
        quantidade_blocos = len(blocos) if blocos else None
        maior_bloco = max(blocos) if blocos else None
        menor_bloco = min(blocos) if blocos else None
        
        # Entropia dos blocos (medida de distribuição)
        entropia_blocos = self._calculate_entropy(blocos) if blocos else None

        # Distribuição espacial (linhas e colunas)
        linhas = self._count_lines(numbers)
        colunas = self._count_columns(numbers)

        return GameFeatures(
            concurso=game.concurso,
            data=game.data,
            numbers=numbers,
            soma=soma,
            pares=pares,
            impares=impares,
            amplitude=amplitude,
            moldura=moldura,
            miolo=miolo,
            primos=primos,
            fibonacci=fibonacci,
            multiplos_3=multiplos_3,
            multiplos_4=multiplos_4,
            multiplos_5=multiplos_5,
            repetidas=repetidas,
            novas=novas,
            quantidade_blocos=quantidade_blocos,
            maior_bloco=maior_bloco,
            menor_bloco=menor_bloco,
            blocos=blocos,
            linhas=linhas,
            colunas=colunas,
            entropia_blocos=entropia_blocos,
        )

    @staticmethod
    def _count_in_set(numbers: Tuple[int, ...], target_set: set) -> int:
        return len([n for n in numbers if n in target_set])

    @staticmethod
    def _count_multiples(numbers: Tuple[int, ...], divisor: int) -> int:
        return len([n for n in numbers if n % divisor == 0])

    @staticmethod
    def _calculate_blocks(numbers: Tuple[int, ...]) -> Tuple[int, ...]:
        """Calcula o tamanho dos blocos de números consecutivos."""
        if not numbers:
            return ()
        
        blocks = []
        current_block_size = 1
        
        for i in range(1, len(numbers)):
            if numbers[i] == numbers[i-1] + 1:
                current_block_size += 1
            else:
                blocks.append(current_block_size)
                current_block_size = 1
        
        blocks.append(current_block_size)
        return tuple(blocks)

    @staticmethod
    def _calculate_entropy(blocks: Tuple[int, ...]) -> float:
        """Calcula uma medida simples de entropia baseada na distribuição dos blocos."""
        if not blocks:
            return 0.0
        
        total = sum(blocks)
        entropy = 0.0
        for b in blocks:
            p = b / total
            if p > 0:
                import math
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    @staticmethod
    def _count_lines(numbers: Tuple[int, ...]) -> Tuple[int, ...]:
        """Conta quantos números há em cada linha do volante (5 linhas)."""
        counts = [0] * 5
        for n in numbers:
            line = (n - 1) // 5
            counts[line] += 1
        return tuple(counts)

    @staticmethod
    def _count_columns(numbers: Tuple[int, ...]) -> Tuple[int, ...]:
        """Conta quantos números há em cada coluna do volante (5 colunas)."""
        counts = [0] * 5
        for n in numbers:
            col = (n - 1) % 5
            counts[col] += 1
        return tuple(counts)
