"""
MVP Vertical - Lotofácil Data Pipeline
Fase 1: Modelo Central de Dados
"""

from dataclasses import dataclass
from typing import Tuple
from datetime import datetime


@dataclass(frozen=True)
class Game:
    """
    Representa um concurso da Lotofácil.
    
    Atributos:
        concurso: Número único do concurso
        data: Data do sorteio no formato YYYY-MM-DD
        numbers: Tupla com as 15 dezenas sorteadas (ordenadas)
    """
    concurso: int
    data: str
    numbers: Tuple[int, ...]

    def __post_init__(self):
        """Valida as regras mínimas do concurso após inicialização."""
        self._validate_concurso()
        self._validate_data()
        self._validate_numbers()

    def _validate_concurso(self):
        """Valida o número do concurso."""
        if not isinstance(self.concurso, int) or self.concurso <= 0:
            raise ValueError(f"Concurso deve ser um inteiro positivo: {self.concurso}")

    def _validate_data(self):
        """Valida o formato e validade da data."""
        try:
            datetime.strptime(self.data, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Data inválida. Use formato YYYY-MM-DD: {self.data}")

    def _validate_numbers(self):
        """Valida as dezenas conforme regras da Lotofácil."""
        # Verifica se é uma tupla/lista
        if not isinstance(self.numbers, (tuple, list)):
            raise TypeError(f"Dezenas devem ser uma tupla ou lista: {type(self.numbers)}")
        
        # Converte para tupla se for lista
        if isinstance(self.numbers, list):
            object.__setattr__(self, 'numbers', tuple(self.numbers))
        
        # Verifica quantidade exata de 15 dezenas
        if len(self.numbers) != 15:
            raise ValueError(f"Devem ser exatamente 15 dezenas. Encontradas: {len(self.numbers)}")
        
        # Verifica se todos são inteiros
        for num in self.numbers:
            if not isinstance(num, int):
                raise TypeError(f"Todas as dezenas devem ser inteiros: {num} ({type(num)})")
        
        # Verifica range (1-25)
        for num in self.numbers:
            if num < 1 or num > 25:
                raise ValueError(f"Dezena fora do intervalo [1-25]: {num}")
        
        # Verifica duplicidade
        if len(set(self.numbers)) != len(self.numbers):
            raise ValueError(f"Existem dezenas duplicadas: {self.numbers}")
        
        # Verifica ordenação
        if list(self.numbers) != sorted(self.numbers):
            raise ValueError(f"As dezenas devem estar ordenadas: {self.numbers}")

    def to_dict(self) -> dict:
        """Converte o objeto para dicionário (formato JSON)."""
        return {
            "concurso": self.concurso,
            "data": self.data,
            "dezenas": list(self.numbers)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Game':
        """Cria uma instância Game a partir de um dicionário."""
        return cls(
            concurso=data["concurso"],
            data=data["data"],
            numbers=tuple(data["dezenas"])
        )

    def __str__(self) -> str:
        return f"Concurso {self.concurso} ({self.data}): {self.numbers}"
