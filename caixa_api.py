"""
Cliente para a API pública da Caixa Econômica Federal - Lotofácil.

Endpoints:
    GET /lotofacil/          -> Último concurso
    GET /lotofacil/{numero}  -> Concurso específico
"""

import json
import time
from typing import Any, Dict

import requests


class CaixaAPIError(Exception):
    """Erro genérico da API da Caixa."""


class CaixaAPIClient:
    """Cliente para a API pública da Caixa (Lotofácil)."""

    BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"

    def __init__(
        self,
        delay: float = 0.5,
        timeout: int = 10,
        max_retries: int = 3,
    ):
        """
        Args:
            delay: Segundos de espera entre requisições (evita bloqueio de IP).
            timeout: Timeout HTTP em segundos.
            max_retries: Máximo de tentativas por requisição (backoff exponencial).
        """
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
        })

    def _request(self, url: str) -> Dict[str, Any]:
        """Faz uma requisição com retry e backoff exponencial.

        A API da Caixa retorna JSON codificado em ISO-8859-1 (Latin-1),
        por isso decodificamos o conteúdo bruto antes do parse.
        """
        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, timeout=self.timeout)

                if resp.status_code == 200:
                    # A API retorna ISO-8859-1 mesmo declarando UTF-8
                    raw = resp.content.decode("iso-8859-1")
                    return json.loads(raw)

                if resp.status_code == 404:
                    raise CaixaAPIError(f"Concurso não encontrado: {url}")

                raise CaixaAPIError(
                    f"Erro HTTP {resp.status_code} em {url}"
                )

            except (requests.RequestException, ValueError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait = 2 ** attempt  # 1s, 2s, 4s...
                    print(f"  [AVISO] Tentativa {attempt + 1} falhou ({e}). "
                          f"Tentando novamente em {wait}s...")
                    time.sleep(wait)

        raise CaixaAPIError(
            f"Falha após {self.max_retries} tentativas: {last_error}"
        )

    def get_ultimo_concurso(self) -> Dict[str, Any]:
        """Busca o último concurso sorteado (JSON completo)."""
        return self._request(self.BASE_URL)

    def get_concurso(self, numero: int) -> Dict[str, Any]:
        """Busca um concurso específico pelo número."""
        return self._request(f"{self.BASE_URL}/{numero}")

    def get_ultimo_numero(self) -> int:
        """Retorna apenas o número do último concurso."""
        data = self.get_ultimo_concurso()
        return int(data["numero"])

    def wait(self) -> None:
        """Aguarda o delay configurado entre requisições."""
        if self.delay > 0:
            time.sleep(self.delay)