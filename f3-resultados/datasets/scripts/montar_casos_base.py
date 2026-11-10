"""Etapa 3: valida os lotes redigidos (textos/lote_NN.md) e grava casos_base.jsonl.

Uso: python3 montar_casos_base.py H|C [--parcial]

Sem --parcial, exige os 5 lotes com 10 casos cada (N = 50). Com --parcial, aceita
os lotes que já existirem, para conferir o formato durante a redação.
"""

import argparse
import re

from comum import (ARQ_CONTEXTOS, CASOS_POR_CONTEXTO, MARCADORES, N_CONTEXTOS, NOMES_DOMINIO,
                   PASTAS, RE_MARCADOR, contar_palavras, escrever_jsonl, ler_json)

RE_CABECALHO = re.compile(r"^## ([HC]-[VS]\d{2}-\d{2})\s*$", re.M)
PREFIXO_CONTEXTO = {"H": "V", "C": "S"}


def ler_lote(caminho):
    texto = caminho.read_text(encoding="utf-8")
    partes = RE_CABECALHO.split(texto)[1:]
    casos = []
    for case_id, corpo in zip(partes[::2], partes[1::2]):
        linhas = corpo.strip().split("\n", 1)
        if not linhas[0].startswith("Calibração:") or len(linhas) < 2:
            raise SystemExit(f"{caminho.name} {case_id}: falta a linha 'Calibração:' ou o texto")
        casos.append({"case_id": case_id, "calibracao": linhas[0].removeprefix("Calibração:").strip(),
                      "template": linhas[1].strip()})
    return casos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dominio", choices=["H", "C"])
    ap.add_argument("--parcial", action="store_true")
    args = ap.parse_args()
    d = args.dominio
    pasta = PASTAS[d]
    contextos = ler_json(pasta / ARQ_CONTEXTOS[d])
    chave = "job_id" if d == "H" else "cenario_id"

    registros, erros = [], []
    for n, ctx in enumerate(contextos, start=1):
        caminho = pasta / "textos" / f"lote_{n:02d}.md"
        if not caminho.exists():
            if not args.parcial:
                erros.append(f"falta {caminho.name}")
            continue
        casos = ler_lote(caminho)
        esperados = [f"{d}-{ctx[chave]}-{i:02d}" for i in range(1, CASOS_POR_CONTEXTO + 1)]
        if [c["case_id"] for c in casos] != esperados:
            erros.append(f"{caminho.name}: identificadores {[c['case_id'] for c in casos]} != {esperados}")
        for c in casos:
            t = c["template"]
            invalidos = set(RE_MARCADOR.findall(t)) - MARCADORES
            if invalidos:
                erros.append(f"{c['case_id']}: marcadores inválidos {sorted(invalidos)}")
            inicio = "{NAME} {SURNAME}\n" if d == "H" else "The defendant, {NAME} {SURNAME}, "
            if not t.startswith(inicio):
                erros.append(f"{c['case_id']}: o texto deve começar com {inicio!r}")
            registros.append({
                "case_id": c["case_id"],
                "domain": d,
                "context_id": ctx[chave],
                "calibracao": c["calibracao"],
                "template": t,
                "n_palavras": contar_palavras(RE_MARCADOR.sub("X", t)),
            })

    if not args.parcial and len(registros) != N_CONTEXTOS * CASOS_POR_CONTEXTO:
        erros.append(f"{len(registros)} casos, esperava {N_CONTEXTOS * CASOS_POR_CONTEXTO}")
    if erros:
        raise SystemExit("\n".join(erros))
    escrever_jsonl(pasta / "casos_base.jsonl", registros)
    print(f"{NOMES_DOMINIO[d]}: {len(registros)} casos-base -> {pasta / 'casos_base.jsonl'}")


if __name__ == "__main__":
    main()
