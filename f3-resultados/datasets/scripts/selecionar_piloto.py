"""Etapa 4 (Fase 2, Seção 2.3): seleção piloto dos N=200 casos por domínio.

ATENÇÃO: ainda não executado. Depende das decisões do agente único (Llama-3.1-8B-Instruct via vLLM,
10 réplicas por caso) sobre as versões NEUTRAS (<dominio>/candidatos/neutros.jsonl).

Entrada (--piloto): JSONL com uma linha por chamada válida do agente único, contendo ao menos
  {"case_id": "...", "Y": 0 ou 1}   (Y=1 é o desfecho favorável: avançar / absolver)
Critério: taxa de desfecho favorável em [0,1; 0,9]. Mantém a estratificação 25% / 50% / 25%
(abaixo-limiar-acima ou fraca-ambigua-forte), sorteando com semente fixa dentro de cada estrato.

Saídas: <dominio>/final/casos_selecionados.txt e <dominio>/final/selecao_piloto.json.
Em seguida: python renderizar.py <dominio> --casos <dominio>/final/casos_selecionados.txt --saida final

Uso: python selecionar_piloto.py H|C --piloto resultados_piloto.jsonl [--n 200]
"""

import argparse
import json
import random
from collections import defaultdict

from comum import PASTAS, SEMENTE, ler_jsonl

PROPORCOES = {"H": {"abaixo": 0.25, "limiar": 0.50, "acima": 0.25},
              "C": {"fraca": 0.25, "ambigua": 0.50, "forte": 0.25}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dominio", choices=["H", "C"])
    ap.add_argument("--piloto", required=True)
    ap.add_argument("--n", type=int, default=200)
    args = ap.parse_args()

    pasta = PASTAS[args.dominio]
    estrato = {c["case_id"]: c["stratum"] for c in ler_jsonl(pasta / "casos_base.jsonl")}
    decisoes = defaultdict(list)
    for r in ler_jsonl(args.piloto):
        decisoes[r["case_id"]].append(int(r["Y"]))

    taxa = {c: sum(y) / len(y) for c, y in decisoes.items() if c in estrato}
    elegiveis = defaultdict(list)
    for c, t in sorted(taxa.items()):
        if 0.1 <= t <= 0.9:
            elegiveis[estrato[c]].append(c)

    rng = random.Random(f"{SEMENTE}-piloto-{args.dominio}")
    selecionados, resumo = [], {}
    for e, prop in PROPORCOES[args.dominio].items():
        alvo = round(args.n * prop)
        pool = elegiveis[e]
        escolhidos = sorted(rng.sample(pool, min(alvo, len(pool))))
        selecionados += escolhidos
        resumo[e] = {"alvo": alvo, "elegiveis": len(pool), "selecionados": len(escolhidos)}

    destino = pasta / "final"
    destino.mkdir(exist_ok=True)
    (destino / "casos_selecionados.txt").write_text("\n".join(sorted(selecionados)) + "\n", encoding="utf-8")
    (destino / "selecao_piloto.json").write_text(json.dumps(
        {"criterio": "taxa favorável em [0,1; 0,9] na versão neutra", "n_alvo": args.n,
         "n_selecionados": len(selecionados), "por_estrato": resumo,
         "taxas": {c: round(t, 3) for c, t in sorted(taxa.items())}}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False))
    if len(selecionados) < args.n:
        print(f"AVISO: só {len(selecionados)} casos elegíveis; a Fase 2 prevê ampliar o conjunto candidato.")


if __name__ == "__main__":
    main()
