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

from caixa_api import CaixaAPIClient, CaixaAPIError
from database import Database


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

    client = CaixaAPIClient(delay=args.delay, timeout=args.timeout)

    def log(msg: str) -> None:
        """Print com flush para funcionar em background/redirect."""
        print(msg, flush=True)

    log("[*] Consultando último concurso...")
    try:
        ultimo = client.get_ultimo_numero()
    except CaixaAPIError as e:
        log(f"[ERRO] Falha ao consultar último concurso: {e}")
        return 1

    log(f"[*] Último concurso disponível: {ultimo}")

    with Database(args.db) as db:
        ultimo_salvo = db.get_ultimo_numero()
        if ultimo_salvo:
            log(f"[*] Banco já possui concursos até: {ultimo_salvo}")
            inicio = max(args.inicio, ultimo_salvo + 1)
        else:
            inicio = args.inicio

        if inicio > ultimo:
            log("[OK] Banco já está atualizado. Nada a fazer.")
            return 0

        log(f"[*] Baixando concursos de {inicio} até {ultimo}...")
        log(f"[*] Delay entre requisições: {args.delay}s")
        log("")

        baixados = 0
        erros = 0
        inicio_tempo = time.time()

        for numero in range(inicio, ultimo + 1):
            try:
                payload = client.get_concurso(numero)
                db.upsert_concurso(payload)
                baixados += 1

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

        log("")
        log("[OK] Download concluído!")
        log(f"     Concursos baixados: {baixados}")
        log(f"     Erros: {erros}")
        log(f"     Total no banco: {db.count()}")
        log(f"     Tempo total: {time.time() - inicio_tempo:.0f}s")

    return 0


if __name__ == "__main__":
    sys.exit(main())