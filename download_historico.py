"""
Script para baixar o histórico completo da Lotofácil da API da Caixa
e salvar em SQLite.

Uso:
    python download_historico.py                # Baixa tudo do concurso 1 até o último
    python download_historico.py --inicio 100   # Começa do concurso 100
    python download_historico.py --delay 0.8    # Delay de 0.8s entre requisições
    python download_historico.py --db dados.db  # Banco customizado
"""

import argparse
import sys
import time
from dataclasses import dataclass
from typing import Callable, Optional

from caixa_api import CaixaAPIClient, CaixaAPIError
from database import Database


@dataclass
class DownloadResult:
    """Resumo do download de concursos."""
    baixados: int
    erros: int
    total_banco: int
    inicio: int
    ultimo: int
    tempo_total: float


def baixar_concursos(
    db_path: str = "lotofacil.db",
    inicio: int = 1,
    delay: float = 0.5,
    timeout: int = 10,
    progress_callback: Optional[Callable[[int, int, int, int], None]] = None,
    log_callback: Optional[Callable[[str], None]] = None,
) -> DownloadResult:
    """Baixa concursos da API da Caixa e salva no SQLite.

    Args:
        db_path: Caminho do banco SQLite.
        inicio: Concurso inicial (se não houver dados salvos).
        delay: Segundos entre requisições.
        timeout: Timeout HTTP.
        progress_callback: Callable(curso_atual, total, baixados, erros).
            Chamado a cada concurso baixado.
        log_callback: Callable(msg) para mensagens de log.

    Returns:
        DownloadResult com estatísticas do download.
    """
    client = CaixaAPIClient(delay=delay, timeout=timeout)

    def log(msg: str) -> None:
        if log_callback:
            log_callback(msg)
        else:
            print(msg, flush=True)

    log("[*] Consultando último concurso...")
    ultimo = client.get_ultimo_numero()
    log(f"[*] Último concurso disponível: {ultimo}")

    with Database(db_path) as db:
        ultimo_salvo = db.get_ultimo_numero()
        if ultimo_salvo:
            log(f"[*] Banco já possui concursos até: {ultimo_salvo}")
            inicio_efetivo = max(inicio, ultimo_salvo + 1)
        else:
            inicio_efetivo = inicio

        baixados = 0
        erros = 0
        inicio_tempo = time.time()

        if inicio_efetivo > ultimo:
            log("[OK] Banco já está atualizado. Nada a fazer.")
            return DownloadResult(
                baixados=0,
                erros=0,
                total_banco=db.count(),
                inicio=inicio_efetivo,
                ultimo=ultimo,
                tempo_total=0.0,
            )

        log(f"[*] Baixando concursos de {inicio_efetivo} até {ultimo}...")
        log(f"[*] Delay entre requisições: {delay}s")

        total = ultimo - inicio_efetivo + 1

        for numero in range(inicio_efetivo, ultimo + 1):
            try:
                payload = client.get_concurso(numero)
                db.upsert_concurso(payload)
                baixados += 1

                if progress_callback:
                    progress_callback(numero, ultimo, baixados, erros)

                if baixados % 50 == 0 or numero == ultimo:
                    decorrido = time.time() - inicio_tempo
                    log(
                        f"  [OK] Concurso {numero}/{ultimo} "
                        f"({baixados} baixados, {erros} erros, "
                        f"{decorrido:.0f}s)"
                    )

            except CaixaAPIError as e:
                erros += 1
                log(f"  [ERRO] Concurso {numero}: {e}")

            client.wait()

        tempo_total = time.time() - inicio_tempo

        log("")
        log("[OK] Download concluído!")
        log(f"     Concursos baixados: {baixados}")
        log(f"     Erros: {erros}")
        log(f"     Total no banco: {db.count()}")
        log(f"     Tempo total: {tempo_total:.0f}s")

        return DownloadResult(
            baixados=baixados,
            erros=erros,
            total_banco=db.count(),
            inicio=inicio_efetivo,
            ultimo=ultimo,
            tempo_total=tempo_total,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa o histórico da Lotofácil da API da Caixa para SQLite."
    )
    parser.add_argument(
        "--inicio", type=int, default=1,
        help="Concurso inicial (default: 1, ou o próximo após o último salvo)."
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="Delay em segundos entre requisições (default: 0.5)."
    )
    parser.add_argument(
        "--db", type=str, default="lotofacil.db",
        help="Caminho do arquivo SQLite (default: lotofacil.db)."
    )
    parser.add_argument(
        "--timeout", type=int, default=10,
        help="Timeout HTTP em segundos (default: 10)."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        baixar_concursos(
            db_path=args.db,
            inicio=args.inicio,
            delay=args.delay,
            timeout=args.timeout,
        )
        return 0
    except CaixaAPIError as e:
        print(f"[ERRO] Falha ao consultar último concurso: {e}", flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())