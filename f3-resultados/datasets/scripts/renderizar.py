"""Etapa 4: injeção determinística dos nomes. Gera as 4 variantes de cada caso-base.

Uso: python3 renderizar.py H|C

Para cada caso-base, sorteia um nome do pool de cada célula (WM, WF, BM, BF) e um
sobrenome neutro, fixo nas quatro variantes. O sorteio é balanceado: em cada domínio,
cada nome do pool aparece em 16 ou 17 dos 50 casos, e cada sobrenome em 25. A ordem
vem de random.Random com semente derivada de SEMENTE, do domínio e da célula.

Saídas em <dominio>/:
  variantes.jsonl   200 registros (50 casos × 4 células), um por texto entregue aos agentes
  sorteio.json      nome e sobrenome sorteados por caso, a ser reaproveitado em todas as topologias
  manifest.json     contagens, hashes SHA-256 e distribuição dos nomes
"""

import argparse
import hashlib
import random
from collections import Counter

from comum import (ARQ_CONTEXTOS, CELULAS, GENERO_CELULA, NOMES_DOMINIO, PASTAS, RACA_CELULA, RAIZ,
                   SEMENTE, escrever_json, escrever_jsonl, ler_json, ler_jsonl, render, sha256_arquivo,
                   sha256_registro)


def sorteio_balanceado(opcoes, n, semente):
    """Lista de n itens com cada opção repetida o mais igualmente possível, em ordem sorteada."""
    lista = [opcoes[i % len(opcoes)] for i in range(n)]
    random.Random(semente).shuffle(lista)
    return lista


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dominio", choices=["H", "C"])
    args = ap.parse_args()
    d = args.dominio
    pasta = PASTAS[d]
    nomes = ler_json(RAIZ / "nomes.json")
    casos = sorted(ler_jsonl(pasta / "casos_base.jsonl"), key=lambda c: c["case_id"])
    n = len(casos)

    sobrenomes = [s["sobrenome"] for s in nomes["sobrenomes"]]
    sorteio_sobrenome = sorteio_balanceado(sobrenomes, n, f"{SEMENTE}-{d}-sobrenome")
    sorteio_nome = {c: sorteio_balanceado(nomes["celulas"][c]["pool"], n, f"{SEMENTE}-{d}-{c}")
                    for c in CELULAS}

    sorteio, variantes = {}, []
    for i, caso in enumerate(casos):
        sobrenome = sorteio_sobrenome[i]
        sorteio[caso["case_id"]] = {"surname": sobrenome,
                                    **{c: sorteio_nome[c][i] for c in CELULAS}}
        for celula in CELULAS:
            nome = sorteio_nome[celula][i]
            genero = GENERO_CELULA[celula]
            reg = {
                "case_id": caso["case_id"],
                "domain": d,
                "context_id": caso["context_id"],
                "cell": celula,
                "race": RACA_CELULA[celula],
                "gender": genero,
                "first_name": nome,
                "surname": sobrenome,
                "text": render(caso["template"], nome, sobrenome, genero),
            }
            reg["sha256"] = sha256_registro(reg)
            variantes.append(reg)

    escrever_jsonl(pasta / "variantes.jsonl", variantes)
    escrever_json(pasta / "sorteio.json", sorteio)

    hash_conjunto = hashlib.sha256("".join(sorted(v["sha256"] for v in variantes)).encode()).hexdigest()
    manifest = {
        "dominio": NOMES_DOMINIO[d],
        "semente": SEMENTE,
        "casos_base": n,
        "variantes": len(variantes),
        "por_contexto": dict(sorted(Counter(c["context_id"] for c in casos).items())),
        "palavras_caso_base": {"min": min(c["n_palavras"] for c in casos),
                               "mediana": sorted(c["n_palavras"] for c in casos)[n // 2],
                               "max": max(c["n_palavras"] for c in casos)},
        "uso_nomes": {c: dict(sorted(Counter(sorteio_nome[c]).items())) for c in CELULAS},
        "uso_sobrenomes": dict(sorted(Counter(sorteio_sobrenome).items())),
        "sha256": {
            "nomes.json": sha256_arquivo(RAIZ / "nomes.json"),
            ARQ_CONTEXTOS[d]: sha256_arquivo(pasta / ARQ_CONTEXTOS[d]),
            "casos_base.jsonl": sha256_arquivo(pasta / "casos_base.jsonl"),
            "variantes.jsonl": sha256_arquivo(pasta / "variantes.jsonl"),
            "conjunto_variantes": hash_conjunto,
        },
    }
    escrever_json(pasta / "manifest.json", manifest)
    print(f"{NOMES_DOMINIO[d]}: {n} casos-base, {len(variantes)} variantes -> {pasta}")


if __name__ == "__main__":
    main()
