"""
Testes para o módulo de análise do histórico (analise.py).
"""

import json

import pandas as pd
import pytest

from analise import AnaliseLotofacil
from database import Database

# Payload real da API da Caixa (concurso 1)
PAYLOAD_CONCURSO_1 = {
    "acumulado": False,
    "dataApuracao": "29/09/2003",
    "dezenasSorteadasOrdemSorteio": ["18", "20", "25"],
    "listaDezenas": ["02", "03", "05", "06", "09", "10", "11",
                     "13", "14", "16", "18", "20", "23", "24", "25"],
    "listaRateioPremio": [
        {"descricaoFaixa": "15 acertos", "faixa": 1,
         "numeroDeGanhadores": 5, "valorPremio": 49765.82},
        {"descricaoFaixa": "14 acertos", "faixa": 2,
         "numeroDeGanhadores": 154, "valorPremio": 689.84},
        {"descricaoFaixa": "13 acertos", "faixa": 3,
         "numeroDeGanhadores": 4645, "valorPremio": 10.0},
        {"descricaoFaixa": "12 acertos", "faixa": 4,
         "numeroDeGanhadores": 48807, "valorPremio": 4.0},
        {"descricaoFaixa": "11 acertos", "faixa": 5,
         "numeroDeGanhadores": 257593, "valorPremio": 2.0},
    ],
    "localSorteio": "Caminhão da Sorte",
    "nomeMunicipioUFSorteio": "CRUZ ALTA, RS",
    "numero": 1,
    "valorArrecadado": 0.0,
    "valorAcumuladoConcursoEspecial": 0.0,
    "valorAcumuladoProximoConcurso": 0.0,
}


def _criar_banco_teste(tmp_path, concursos: list) -> str:
    """Cria um banco SQLite de teste com os concursos fornecidos."""
    db_path = str(tmp_path / "test.db")
    with Database(db_path) as db:
        for n in concursos:
            payload = dict(PAYLOAD_CONCURSO_1)
            payload["numero"] = n
            db.upsert_concurso(payload)
    return db_path


class TestAnaliseDataframe:
    """Testes do DataFrame gerado pela análise."""

    def test_gerar_dataframe_vazio(self, tmp_path):
        """Banco vazio retorna DataFrame vazio."""
        db_path = str(tmp_path / "vazio.db")
        with Database(db_path):
            pass
        analise = AnaliseLotofacil(db_path)
        df = analise.gerar_dataframe()
        assert df.empty

    def test_gerar_dataframe_colunas(self, tmp_path):
        """DataFrame tem todas as colunas esperadas."""
        db_path = _criar_banco_teste(tmp_path, [1, 2, 3])
        analise = AnaliseLotofacil(db_path)
        df = analise.gerar_dataframe()

        colunas_esperadas = [
            "concurso", "data", "soma", "pares", "impares", "amplitude",
            "repetidas", "novas", "moldura", "miolo",
            "primos", "fibonacci", "multiplos_3", "multiplos_4", "multiplos_5",
            "linha_1", "linha_2", "linha_3", "linha_4", "linha_5",
            "coluna_1", "coluna_2", "coluna_3", "coluna_4", "coluna_5",
        ]
        for col in colunas_esperadas:
            assert col in df.columns, f"Coluna {col} ausente"

    def test_gerar_dataframe_quantidade(self, tmp_path):
        """DataFrame tem 1 linha por concurso."""
        db_path = _criar_banco_teste(tmp_path, [1, 2, 3, 4, 5])
        analise = AnaliseLotofacil(db_path)
        df = analise.gerar_dataframe()
        assert len(df) == 5

    def test_gerar_dataframe_ordenado(self, tmp_path):
        """Concursos ordenados por número."""
        db_path = _criar_banco_teste(tmp_path, [3, 1, 2])
        analise = AnaliseLotofacil(db_path)
        df = analise.gerar_dataframe()
        assert list(df["concurso"]) == [1, 2, 3]

    def test_repetidas_novas_primeiro_concurso(self, tmp_path):
        """Primeiro concurso tem repetidas/novas = None."""
        db_path = _criar_banco_teste(tmp_path, [1, 2])
        analise = AnaliseLotofacil(db_path)
        df = analise.gerar_dataframe()

        assert pd.isna(df.iloc[0]["repetidas"])
        assert pd.isna(df.iloc[0]["novas"])

    def test_repetidas_novas_calculadas(self, tmp_path):
        """Repetidas/novas calculadas a partir do concurso anterior."""
        db_path = _criar_banco_teste(tmp_path, [1, 2])
        analise = AnaliseLotofacil(db_path)
        df = analise.gerar_dataframe()

        # Concurso 2 tem valores calculados
        assert not pd.isna(df.iloc[1]["repetidas"])
        assert not pd.isna(df.iloc[1]["novas"])
        # repetidas + novas = 15
        assert df.iloc[1]["repetidas"] + df.iloc[1]["novas"] == 15

    def test_features_estruturais(self, tmp_path):
        """Soma, pares, ímpares e amplitude calculados corretamente."""
        db_path = _criar_banco_teste(tmp_path, [1])
        analise = AnaliseLotofacil(db_path)
        df = analise.gerar_dataframe()

        # Concurso 1: [2, 3, 5, 6, 9, 10, 11, 13, 14, 16, 18, 20, 23, 24, 25]
        assert df.iloc[0]["soma"] == 199
        assert df.iloc[0]["pares"] == 8
        assert df.iloc[0]["impares"] == 7
        assert df.iloc[0]["amplitude"] == 23

    def test_features_espaciais(self, tmp_path):
        """Moldura, miolo, linhas e colunas calculados."""
        db_path = _criar_banco_teste(tmp_path, [1])
        analise = AnaliseLotofacil(db_path)
        df = analise.gerar_dataframe()

        # Concurso 1: moldura 11, miolo 4
        assert df.iloc[0]["moldura"] == 11
        assert df.iloc[0]["miolo"] == 4
        # Soma das linhas = 15
        assert sum(df.iloc[0][f"linha_{i}"] for i in range(1, 6)) == 15
        # Soma das colunas = 15
        assert sum(df.iloc[0][f"coluna_{i}"] for i in range(1, 6)) == 15

    def test_features_numericas(self, tmp_path):
        """Primos, fibonacci e múltiplos calculados."""
        db_path = _criar_banco_teste(tmp_path, [1])
        analise = AnaliseLotofacil(db_path)
        df = analise.gerar_dataframe()

        # Concurso 1: primos 6, fibonacci 4, mult_3 5, mult_4 3, mult_5 4
        assert df.iloc[0]["primos"] == 6
        assert df.iloc[0]["fibonacci"] == 4
        assert df.iloc[0]["multiplos_3"] == 5
        assert df.iloc[0]["multiplos_4"] == 3
        assert df.iloc[0]["multiplos_5"] == 4


class TestAnaliseResumo:
    """Testes do resumo estatístico."""

    def test_resumo_estatistico(self, tmp_path):
        """Resumo retorna estatísticas descritivas."""
        db_path = _criar_banco_teste(tmp_path, [1, 2, 3])
        analise = AnaliseLotofacil(db_path)
        df = analise.gerar_dataframe()
        resumo = analise.resumo_estatistico(df)

        assert "soma" in resumo.index
        assert "pares" in resumo.index
        assert "mean" in resumo.columns
        assert "min" in resumo.columns
        assert "max" in resumo.columns

    def test_resumo_estatistico_vazio(self, tmp_path):
        """Resumo de banco vazio retorna DataFrame vazio."""
        db_path = str(tmp_path / "vazio.db")
        with Database(db_path):
            pass
        analise = AnaliseLotofacil(db_path)
        resumo = analise.resumo_estatistico()
        assert resumo.empty

    def test_frequencias(self, tmp_path):
        """Frequências retornam contagem por valor."""
        db_path = _criar_banco_teste(tmp_path, [1, 2, 3])
        analise = AnaliseLotofacil(db_path)
        df = analise.gerar_dataframe()
        freq = analise.frequencias(df)

        assert "pares" in freq
        assert "soma" in freq
        # Soma das frequências de pares = total de concursos
        assert sum(freq["pares"].values()) == 3

    def test_frequencias_vazio(self, tmp_path):
        """Frequências de banco vazio retornam dict vazio."""
        db_path = str(tmp_path / "vazio.db")
        with Database(db_path):
            pass
        analise = AnaliseLotofacil(db_path)
        assert analise.frequencias() == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])