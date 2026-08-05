"""
Testes para a classe Game - Modelo Central de Dados
"""

import pytest
from game import Game


class TestGameCreation:
    """Testes de criação válida de objetos Game."""

    def test_create_valid_game(self):
        """Cria um jogo válido com dados corretos."""
        game = Game(
            concurso=3300,
            data="2026-08-04",
            numbers=(1, 2, 3, 5, 8, 9, 10, 13, 14, 17, 19, 21, 23, 24, 25)
        )
        assert game.concurso == 3300
        assert game.data == "2026-08-04"
        assert len(game.numbers) == 15
        assert isinstance(game.numbers, tuple)

    def test_create_game_from_list(self):
        """Deve converter lista para tupla automaticamente."""
        game = Game(
            concurso=1,
            data="2003-09-29",
            numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        )
        assert isinstance(game.numbers, tuple)

    def test_create_game_from_dict(self):
        """Cria jogo a partir de dicionário."""
        data = {
            "concurso": 3300,
            "data": "2026-08-04",
            "dezenas": [1, 2, 3, 5, 8, 9, 10, 13, 14, 17, 19, 21, 23, 24, 25]
        }
        game = Game.from_dict(data)
        assert game.concurso == 3300
        assert game.to_dict() == data


class TestGameValidation:
    """Testes de validação das regras de negócio."""

    def test_invalid_concurso_zero(self):
        """Concurso zero deve falhar."""
        with pytest.raises(ValueError):
            Game(concurso=0, data="2026-08-04", numbers=tuple(range(1, 16)))

    def test_invalid_concurso_negative(self):
        """Concurso negativo deve falhar."""
        with pytest.raises(ValueError):
            Game(concurso=-1, data="2026-08-04", numbers=tuple(range(1, 16)))

    def test_invalid_data_format(self):
        """Data em formato inválido deve falhar."""
        with pytest.raises(ValueError):
            Game(concurso=1, data="04/08/2026", numbers=tuple(range(1, 16)))

    def test_invalid_date_nonexistent(self):
        """Data inexistente deve falhar."""
        with pytest.raises(ValueError):
            Game(concurso=1, data="2026-02-30", numbers=tuple(range(1, 16)))

    def test_wrong_quantity_14_numbers(self):
        """14 dezenas devem falhar."""
        with pytest.raises(ValueError):
            Game(concurso=1, data="2026-08-04", numbers=tuple(range(1, 15)))

    def test_wrong_quantity_16_numbers(self):
        """16 dezenas devem falhar."""
        with pytest.raises(ValueError):
            Game(concurso=1, data="2026-08-04", numbers=tuple(range(1, 17)))

    def test_number_out_of_range_low(self):
        """Dezena 0 deve falhar."""
        with pytest.raises(ValueError):
            Game(concurso=1, data="2026-08-04", 
                 numbers=(0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))

    def test_number_out_of_range_high(self):
        """Dezena 26 deve falhar."""
        with pytest.raises(ValueError):
            Game(concurso=1, data="2026-08-04", 
                 numbers=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 26))

    def test_duplicate_numbers(self):
        """Dezenas duplicadas devem falhar."""
        with pytest.raises(ValueError):
            Game(concurso=1, data="2026-08-04", 
                 numbers=(1, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))

    def test_unordered_numbers(self):
        """Dezenas não ordenadas devem falhar."""
        with pytest.raises(ValueError):
            Game(concurso=1, data="2026-08-04", 
                 numbers=(2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))

    def test_non_integer_number(self):
        """Dezena não inteira deve falhar."""
        with pytest.raises(TypeError):
            Game(concurso=1, data="2026-08-04", 
                 numbers=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, "15"))


class TestGameImmutability:
    """Testes de imutabilidade do dataclass frozen."""

    def test_cannot_modify_concurso(self):
        """Não deve permitir modificar concurso após criação."""
        game = Game(concurso=1, data="2026-08-04", numbers=tuple(range(1, 16)))
        with pytest.raises(AttributeError):
            game.concurso = 2

    def test_cannot_modify_numbers(self):
        """Não deve permitir modificar números após criação."""
        game = Game(concurso=1, data="2026-08-04", numbers=tuple(range(1, 16)))
        with pytest.raises(AttributeError):
            game.numbers = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
