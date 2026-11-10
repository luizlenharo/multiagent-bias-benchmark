"""Cria auditoria_manual.csv, a planilha da auditoria manual dos casos-base (Fase 2, Seção 2).

Uso: python3 planilha_auditoria.py [--forcar]

Uma linha por caso-base dos dois domínios. Cada autor preenche, de forma independente:
  limitrofe_<autor>  "sim" ou "nao": o caso é de fato limítrofe? (item i)
  pistas_<autor>     "sim" ou "nao": há pista de raça ou gênero além do nome? (item ii)
Depois, os dois preenchem juntos a decisao ("manter", "reescrever" ou "descartar") e as notas.

Não sobrescreve uma planilha existente, que pode já ter sido preenchida, sem --forcar.
"""

import argparse
import csv

from comum import PASTAS, RAIZ, ler_jsonl

CAMPOS = ["case_id", "dominio", "contexto", "calibracao",
          "limitrofe_luiz", "pistas_luiz", "limitrofe_felipe", "pistas_felipe", "decisao", "notas"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forcar", action="store_true")
    args = ap.parse_args()
    destino = RAIZ / "auditoria_manual.csv"
    if destino.exists() and not args.forcar:
        raise SystemExit(f"{destino} já existe; use --forcar para recriar")
    with open(destino, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n")
        w.writeheader()
        for d in ["H", "C"]:
            for c in ler_jsonl(PASTAS[d] / "casos_base.jsonl"):
                w.writerow({"case_id": c["case_id"], "dominio": d, "contexto": c["context_id"],
                            "calibracao": c["calibracao"]})
    print(f"planilha -> {destino}")


if __name__ == "__main__":
    main()
