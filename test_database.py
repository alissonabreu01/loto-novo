"""
Testes para a persistência SQLite (database.py) e cliente da API (caixa_api.py).
"""

import json
import sqlite3
from unittest.mock import Mock, patch

import pytest

from caixa_api import CaixaAPIClient, CaixaAPIError
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


class TestDatabaseParsing:
    """Testes de parse do payload da API."""

    def test_parse_payload_dezenas(self, tmp_path):
        db = Database(str(tmp_path / "test.db")).connect()
        parsed = db._parse_payload(PAYLOAD_CONCURSO_1)
        assert parsed["dezenas"] == [2, 3, 5, 6, 9, 10, 11, 13, 14,
                                     16, 18, 20, 23, 24, 25]
        assert len(parsed["dezenas"]) == 15
        db.close()

    def test_parse_payload_data_normalizada(self, tmp_path):
        db = Database(str(tmp_path / "test.db")).connect()
        parsed = db._parse_payload(PAYLOAD_CONCURSO_1)
        assert parsed["data"] == "2003-09-29"
        db.close()

    def test_parse_payload_rateio(self, tmp_path):
        db = Database(str(tmp_path / "test.db")).connect()
        parsed = db._parse_payload(PAYLOAD_CONCURSO_1)
        assert parsed["ganhadores_15"] == 5
        assert parsed["ganhadores_14"] == 154
        assert parsed["ganhadores_13"] == 4645
        assert parsed["premio_15"] == 49765.82
        assert parsed["premio_11"] == 2.0
        db.close()

    def test_normalize_date(self):
        assert Database._normalize_date("29/09/2003") == "2003-09-29"
        assert Database._normalize_date("") == ""
        assert Database._normalize_date("data-invalida") == "data-invalida"


class TestDatabaseCRUD:
    """Testes de CRUD no SQLite."""

    def test_upsert_insert(self, tmp_path):
        with Database(str(tmp_path / "test.db")) as db:
            db.upsert_concurso(PAYLOAD_CONCURSO_1)
            assert db.count() == 1
            row = db.get_concurso(1)
            assert row["numero"] == 1
            assert row["data"] == "2003-09-29"

    def test_upsert_update_existente(self, tmp_path):
        with Database(str(tmp_path / "test.db")) as db:
            db.upsert_concurso(PAYLOAD_CONCURSO_1)

            # Atualiza o mesmo concurso com dados diferentes
            payload2 = dict(PAYLOAD_CONCURSO_1)
            payload2["listaRateioPremio"][0]["numeroDeGanhadores"] = 10
            payload2["listaRateioPremio"][0]["valorPremio"] = 99999.0
            db.upsert_concurso(payload2)

            assert db.count() == 1  # não duplica
            row = db.get_concurso(1)
            assert row["ganhadores_15"] == 10
            assert row["premio_15"] == 99999.0

    def test_upsert_multiplos(self, tmp_path):
        with Database(str(tmp_path / "test.db")) as db:
            for n in [1, 2, 3]:
                payload = dict(PAYLOAD_CONCURSO_1)
                payload["numero"] = n
                db.upsert_concurso(payload)
            assert db.count() == 3

    def test_get_concurso_inexistente(self, tmp_path):
        with Database(str(tmp_path / "test.db")) as db:
            assert db.get_concurso(999) is None

    def test_get_ultimo_numero_vazio(self, tmp_path):
        with Database(str(tmp_path / "test.db")) as db:
            assert db.get_ultimo_numero() is None

    def test_get_ultimo_numero(self, tmp_path):
        with Database(str(tmp_path / "test.db")) as db:
            for n in [5, 3, 10, 1]:
                payload = dict(PAYLOAD_CONCURSO_1)
                payload["numero"] = n
                db.upsert_concurso(payload)
            assert db.get_ultimo_numero() == 10

    def test_get_dezenas(self, tmp_path):
        with Database(str(tmp_path / "test.db")) as db:
            db.upsert_concurso(PAYLOAD_CONCURSO_1)
            dezenas = db.get_dezenas(1)
            assert dezenas == [2, 3, 5, 6, 9, 10, 11, 13, 14,
                               16, 18, 20, 23, 24, 25]

    def test_get_todos_ordenados(self, tmp_path):
        with Database(str(tmp_path / "test.db")) as db:
            for n in [3, 1, 2]:
                payload = dict(PAYLOAD_CONCURSO_1)
                payload["numero"] = n
                db.upsert_concurso(payload)
            todos = db.get_todos()
            assert [t["numero"] for t in todos] == [1, 2, 3]

    def test_json_original_armazenado(self, tmp_path):
        with Database(str(tmp_path / "test.db")) as db:
            db.upsert_concurso(PAYLOAD_CONCURSO_1)
            row = db.get_concurso(1)
            original = json.loads(row["json_original"])
            assert original["localSorteio"] == "Caminhão da Sorte"
            assert original["numero"] == 1


class TestCaixaAPIClient:
    """Testes do cliente da API da Caixa (com mocks)."""

    def test_get_ultimo_numero(self):
        client = CaixaAPIClient(delay=0)
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.content = json.dumps({"numero": 3752}).encode("utf-8")

        with patch.object(client.session, "get", return_value=mock_resp):
            assert client.get_ultimo_numero() == 3752

    def test_get_concurso_ok(self):
        client = CaixaAPIClient(delay=0)
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.content = json.dumps(PAYLOAD_CONCURSO_1).encode("utf-8")

        with patch.object(client.session, "get", return_value=mock_resp):
            data = client.get_concurso(1)
            assert data["numero"] == 1
            assert len(data["listaDezenas"]) == 15

    def test_get_concurso_decodifica_latin1(self):
        """A API retorna ISO-8859-1; deve ser decodificado corretamente."""
        client = CaixaAPIClient(delay=0)
        mock_resp = Mock()
        mock_resp.status_code = 200
        # "Caminhão" em ISO-8859-1
        payload = json.dumps(
            {"numero": 1, "localSorteio": "Caminhão da Sorte"},
            ensure_ascii=False,
        ).encode("iso-8859-1")
        mock_resp.content = payload

        with patch.object(client.session, "get", return_value=mock_resp):
            data = client.get_concurso(1)
            assert data["localSorteio"] == "Caminhão da Sorte"

    def test_get_concurso_404(self):
        client = CaixaAPIClient(delay=0)
        mock_resp = Mock()
        mock_resp.status_code = 404
        mock_resp.content = b""

        with patch.object(client.session, "get", return_value=mock_resp):
            with pytest.raises(CaixaAPIError):
                client.get_concurso(99999)

    def test_get_concurso_erro_http(self):
        client = CaixaAPIClient(delay=0)
        mock_resp = Mock()
        mock_resp.status_code = 500
        mock_resp.content = b""

        with patch.object(client.session, "get", return_value=mock_resp):
            with pytest.raises(CaixaAPIError):
                client.get_concurso(1)

    def test_wait_com_delay_zero(self):
        """Delay 0 não deve dormir."""
        client = CaixaAPIClient(delay=0)
        with patch("caixa_api.time.sleep") as mock_sleep:
            client.wait()
            mock_sleep.assert_not_called()

    def test_wait_com_delay(self):
        client = CaixaAPIClient(delay=0.5)
        with patch("caixa_api.time.sleep") as mock_sleep:
            client.wait()
            mock_sleep.assert_called_once_with(0.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])