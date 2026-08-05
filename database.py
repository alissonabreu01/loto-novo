"""
Persistência dos concursos da Lotofácil em SQLite.

Tabela `concursos`:
    - numero          INTEGER PRIMARY KEY
    - data            TEXT (YYYY-MM-DD)
    - dezenas         TEXT (JSON array de 15 números)
    - arrecadacao     REAL
    - ganhadores_15   INTEGER
    - ganhadores_14   INTEGER
    - ganhadores_13   INTEGER
    - ganhadores_12   INTEGER
    - ganhadores_11   INTEGER
    - premio_15       REAL
    - premio_14       REAL
    - premio_13       REAL
    - premio_12       REAL
    - premio_11       REAL
    - acumulado       REAL
    - json_original   TEXT (payload completo da API)
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class Database:
    """Gerencia a conexão e operações no banco SQLite."""

    def __init__(self, db_path: str = "lotofacil.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> "Database":
        """Abre a conexão e cria a tabela se necessário."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_table()
        return self

    def close(self) -> None:
        """Fecha a conexão."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "Database":
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _create_table(self) -> None:
        """Cria a tabela de concursos se não existir."""
        assert self._conn is not None
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS concursos (
                numero          INTEGER PRIMARY KEY,
                data            TEXT NOT NULL,
                dezenas         TEXT NOT NULL,
                arrecadacao     REAL,
                ganhadores_15   INTEGER,
                ganhadores_14   INTEGER,
                ganhadores_13   INTEGER,
                ganhadores_12   INTEGER,
                ganhadores_11   INTEGER,
                premio_15       REAL,
                premio_14       REAL,
                premio_13       REAL,
                premio_12       REAL,
                premio_11       REAL,
                acumulado       REAL,
                json_original   TEXT
            )
        """)
        self._conn.commit()

    @staticmethod
    def _normalize_date(data: str) -> str:
        """Converte data DD/MM/YYYY para YYYY-MM-DD."""
        if not data:
            return ""
        try:
            dia, mes, ano = data.split("/")
            return f"{ano}-{mes}-{dia}"
        except (ValueError, AttributeError):
            return data

    def _parse_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai os campos relevantes do JSON da API da Caixa."""
        # Dezenas sorteadas (lista de strings no campo 'listaDezenas')
        dezenas_raw = payload.get("listaDezenas", [])
        dezenas = [int(d) for d in dezenas_raw]

        # Rateio de prêmios (lista de dicts com 'faixa' de 1 a 5)
        # faixa 1 = 15 acertos, faixa 2 = 14, ..., faixa 5 = 11
        rateio = payload.get("listaRateioPremio", [])
        ganhadores = {1: None, 2: None, 3: None, 4: None, 5: None}
        premios = {1: None, 2: None, 3: None, 4: None, 5: None}

        for faixa in rateio:
            try:
                faixa_num = int(faixa.get("faixa", 0))
                if faixa_num in ganhadores:
                    ganhadores[faixa_num] = faixa.get("numeroDeGanhadores")
                    premios[faixa_num] = faixa.get("valorPremio")
            except (ValueError, TypeError):
                continue

        return {
            "numero": int(payload["numero"]),
            "data": self._normalize_date(payload.get("dataApuracao", "")),
            "dezenas": dezenas,
            "arrecadacao": payload.get("valorArrecadado"),
            "ganhadores_15": ganhadores[1],
            "ganhadores_14": ganhadores[2],
            "ganhadores_13": ganhadores[3],
            "ganhadores_12": ganhadores[4],
            "ganhadores_11": ganhadores[5],
            "premio_15": premios[1],
            "premio_14": premios[2],
            "premio_13": premios[3],
            "premio_12": premios[4],
            "premio_11": premios[5],
            "acumulado": payload.get("valorAcumuladoConcursoEspecial")
            or payload.get("valorAcumuladoProximoConcurso"),
            "json_original": json.dumps(payload, ensure_ascii=False),
        }

    def upsert_concurso(self, payload: Dict[str, Any]) -> None:
        """Insere ou atualiza um concurso a partir do payload da API."""
        assert self._conn is not None
        data = self._parse_payload(payload)

        self._conn.execute("""
            INSERT INTO concursos (
                numero, data, dezenas, arrecadacao,
                ganhadores_15, ganhadores_14, ganhadores_13,
                ganhadores_12, ganhadores_11,
                premio_15, premio_14, premio_13, premio_12, premio_11,
                acumulado, json_original
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(numero) DO UPDATE SET
                data = excluded.data,
                dezenas = excluded.dezenas,
                arrecadacao = excluded.arrecadacao,
                ganhadores_15 = excluded.ganhadores_15,
                ganhadores_14 = excluded.ganhadores_14,
                ganhadores_13 = excluded.ganhadores_13,
                ganhadores_12 = excluded.ganhadores_12,
                ganhadores_11 = excluded.ganhadores_11,
                premio_15 = excluded.premio_15,
                premio_14 = excluded.premio_14,
                premio_13 = excluded.premio_13,
                premio_12 = excluded.premio_12,
                premio_11 = excluded.premio_11,
                acumulado = excluded.acumulado,
                json_original = excluded.json_original
        """, (
            data["numero"], data["data"], json.dumps(data["dezenas"]),
            data["arrecadacao"],
            data["ganhadores_15"], data["ganhadores_14"],
            data["ganhadores_13"], data["ganhadores_12"],
            data["ganhadores_11"],
            data["premio_15"], data["premio_14"], data["premio_13"],
            data["premio_12"], data["premio_11"],
            data["acumulado"], data["json_original"],
        ))
        self._conn.commit()

    def get_concurso(self, numero: int) -> Optional[Dict[str, Any]]:
        """Retorna um concurso pelo número, ou None se não existir."""
        assert self._conn is not None
        row = self._conn.execute(
            "SELECT * FROM concursos WHERE numero = ?", (numero,)
        ).fetchone()
        return dict(row) if row else None

    def get_ultimo_numero(self) -> Optional[int]:
        """Retorna o maior número de concurso salvo, ou None se vazio."""
        assert self._conn is not None
        row = self._conn.execute(
            "SELECT MAX(numero) AS max_num FROM concursos"
        ).fetchone()
        return row["max_num"] if row and row["max_num"] is not None else None

    def get_todos(self) -> List[Dict[str, Any]]:
        """Retorna todos os concursos ordenados por número."""
        assert self._conn is not None
        rows = self._conn.execute(
            "SELECT * FROM concursos ORDER BY numero"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_dezenas(self, numero: int) -> Optional[List[int]]:
        """Retorna as dezenas de um concurso como lista de ints."""
        row = self.get_concurso(numero)
        if not row:
            return None
        return json.loads(row["dezenas"])

    def count(self) -> int:
        """Retorna o total de concursos salvos."""
        assert self._conn is not None
        row = self._conn.execute(
            "SELECT COUNT(*) AS total FROM concursos"
        ).fetchone()
        return row["total"]