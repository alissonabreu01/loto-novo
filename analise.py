"""
Módulo de análise do histórico da Lotofácil.

Lê os concursos do SQLite, calcula as features de cada um
e retorna um DataFrame pandas com as análises.
"""

import json
from typing import List, Optional

import pandas as pd

from database import Database
from feature_extractor import FeatureExtractor
from game import Game


class AnaliseLotofacil:
    """Gera análises estatísticas a partir do histórico salvo no SQLite."""

    def __init__(self, db_path: str = "lotofacil.db"):
        self.db_path = db_path
        self.extractor = FeatureExtractor()

    def _carregar_games(self) -> List[Game]:
        """Carrega todos os concursos do banco como objetos Game."""
        games = []
        with Database(self.db_path) as db:
            concursos = db.get_todos()
            for row in concursos:
                dezenas = json.loads(row["dezenas"])
                games.append(Game(
                    concurso=row["numero"],
                    data=row["data"],
                    numbers=tuple(dezenas),
                ))
        return games

    def gerar_dataframe(self) -> pd.DataFrame:
        """
        Calcula as features de todos os concursos e retorna um DataFrame.

        Colunas:
            concurso, data, soma, pares, impares, amplitude,
            repetidas, novas, linhas_1..5, colunas_1..5,
            moldura, miolo, primos, fibonacci,
            multiplos_3, multiplos_4, multiplos_5
        """
        games = self._carregar_games()
        if not games:
            return pd.DataFrame()

        registros = []
        for i, game in enumerate(games):
            # Concurso anterior para calcular repetidas/novas
            previous = games[i - 1] if i > 0 else None
            feats = self.extractor.extract(game, previous_game=previous)

            registro = {
                "concurso": feats.concurso,
                "data": feats.data,
                # Estruturais
                "soma": feats.soma,
                "pares": feats.pares,
                "impares": feats.impares,
                "amplitude": feats.amplitude,
                "repetidas": feats.repetidas,
                "novas": feats.novas,
                # Espaciais
                "moldura": feats.moldura,
                "miolo": feats.miolo,
                # Numéricas especiais
                "primos": feats.primos,
                "fibonacci": feats.fibonacci,
                "multiplos_3": feats.multiplos_3,
                "multiplos_4": feats.multiplos_4,
                "multiplos_5": feats.multiplos_5,
            }

            # Linhas e colunas (1 a 5)
            for idx, count in enumerate(feats.linhas, 1):
                registro[f"linha_{idx}"] = count
            for idx, count in enumerate(feats.colunas, 1):
                registro[f"coluna_{idx}"] = count

            registros.append(registro)

        return pd.DataFrame(registros)

    def resumo_estatistico(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Retorna estatísticas descritivas (média, min, max, etc.)
        das features numéricas.
        """
        if df is None:
            df = self.gerar_dataframe()
        if df.empty:
            return pd.DataFrame()

        colunas_numericas = [
            "soma", "pares", "impares", "amplitude",
            "repetidas", "novas",
            "moldura", "miolo",
            "primos", "fibonacci",
            "multiplos_3", "multiplos_4", "multiplos_5",
            "linha_1", "linha_2", "linha_3", "linha_4", "linha_5",
            "coluna_1", "coluna_2", "coluna_3", "coluna_4", "coluna_5",
        ]
        colunas_existentes = [c for c in colunas_numericas if c in df.columns]
        return df[colunas_existentes].describe().T

    def frequencias(self, df: Optional[pd.DataFrame] = None) -> dict:
        """
        Retorna a frequência de cada valor para cada feature.

        Ex: para 'pares', quantas vezes apareceu 5, 6, 7, 8, 9, 10...
        """
        if df is None:
            df = self.gerar_dataframe()
        if df.empty:
            return {}

        colunas = [
            "soma", "pares", "impares", "amplitude",
            "repetidas", "novas",
            "moldura", "miolo",
            "primos", "fibonacci",
            "multiplos_3", "multiplos_4", "multiplos_5",
        ]
        resultado = {}
        for col in colunas:
            if col in df.columns:
                resultado[col] = (
                    df[col].value_counts().sort_index().to_dict()
                )
        return resultado