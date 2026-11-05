"""Etapa 5 (Fase 2, Seção 2.3): perturbação, verificação por diff (H2) e congelamento.

Para cada caso-base gera:
  neutros.jsonl  versão neutra (todos os slots omitidos), usada na seleção piloto;
  pares.jsonl    3 atributos x 2 níveis = 6 entradas por caso, no formato da Fase 2:
                 case_id, domain, stratum, attribute, level, variant, text, job_id (só H), sha256;
  manifest.json  contagens, hash SHA-256 de cada arquivo e do conjunto, resultado do diff,
                 diferença de comprimento B x A.

Uso:
  python renderizar.py H|C                         -> <dominio>/candidatos/ (todos os casos-base)
  python renderizar.py H|C --casos lista.txt --saida final
                                                   -> <dominio>/final/ (casos selecionados no piloto)
"""

import argparse
import hashlib
import json
import statistics
from datetime import datetime, timezone

from comum import (ATRIBUTOS, NIVEIS, PASTAS, RAIZ, carregar_lexicos, escrever_jsonl, ler_jsonl, linha_slot,
                   render, sha256_arquivo, sha256_registro, tokens_aprox, variante_do_caso)


def checar_diff(texto_b, texto_a, linha_b, linha_a):
    """O par deve diferir exclusivamente na linha do slot."""
    lb, la = texto_b.split("\n"), texto_a.split("\n")
    if len(lb) != len(la):
        return False
    difs = [(x, y) for x, y in zip(lb, la) if x != y]
    return difs == [(linha_b, linha_a)] or (linha_b == linha_a and not difs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dominio", choices=["H", "C"])
    ap.add_argument("--casos", help="arquivo com um case_id por linha (seleção piloto)")
    ap.add_argument("--saida", default="candidatos")
    args = ap.parse_args()

    pasta = PASTAS[args.dominio]
    lexicos = carregar_lexicos()
    casos = ler_jsonl(pasta / "casos_base.jsonl")
    if args.casos:
        ids = [l.strip() for l in open(args.casos, encoding="utf-8") if l.strip()]
        por_id = {c["case_id"]: c for c in casos}
        faltando = [i for i in ids if i not in por_id]
        if faltando:
            raise SystemExit(f"ERRO: casos selecionados sem caso-base: {faltando[:5]}")
        casos = [por_id[i] for i in ids]

    neutros, pares, falhas_diff, dif_tokens = [], [], [], {p: [] for p in ATRIBUTOS[args.dominio]}
    for c in casos:
        meta = {"case_id": c["case_id"], "domain": args.dominio, "stratum": c["stratum"]}
        extra = {"job_id": c["job_id"]} if args.dominio == "H" else {}

        neutro = {**meta, "text": render(c["text_base"], lexicos, args.dominio, c["genero"]), **extra}
        neutro["sha256"] = sha256_registro(neutro)
        neutros.append(neutro)

        for p in ATRIBUTOS[args.dominio]:
            v = variante_do_caso(c["case_id"], p)
            textos = {}
            for nivel in NIVEIS:
                texto = render(c["text_base"], lexicos, args.dominio, c["genero"], p, nivel, v)
                textos[nivel] = texto
                reg = {**meta, "attribute": p, "level": nivel, "variant": v, "text": texto, **extra}
                reg["sha256"] = sha256_registro(reg)
                pares.append(reg)
            lb = linha_slot(lexicos[p], "B", v, c["genero"])
            la = linha_slot(lexicos[p], "A", v, c["genero"])
            if not checar_diff(textos["B"], textos["A"], lb, la):
                falhas_diff.append(f"{c['case_id']}/{p}")
            dif_tokens[p].append(tokens_aprox(textos["A"]) - tokens_aprox(textos["B"]))

    destino = pasta / args.saida
    escrever_jsonl(destino / "neutros.jsonl", neutros)
    escrever_jsonl(destino / "pares.jsonl", pares)

    hash_conjunto = hashlib.sha256("".join(r["sha256"] for r in pares).encode()).hexdigest()
    n_pares = len(casos) * len(ATRIBUTOS[args.dominio])
    manifest = {
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dominio": args.dominio,
        "saida": args.saida,
        "n_casos_base": len(casos),
        "n_entradas_perturbadas": len(pares),
        "n_pares_contrafactuais": n_pares,
        "diff_restrito_ao_slot": {"aprovados": n_pares - len(falhas_diff), "total": n_pares,
                                  "falhas": falhas_diff},
        "diferenca_comprimento_A_menos_B": {
            "metodo": "tokens aproximados (palavras + pontuação); conferir com o tokenizer do Llama-3.1-8B",
            **{p: {"min": min(d), "max": max(d), "media": round(statistics.mean(d), 2),
                   "abs_max": max(abs(x) for x in d)} for p, d in dif_tokens.items() if d},
        },
        "sha256": {
            "conjunto_pares": hash_conjunto,
            "pares.jsonl": sha256_arquivo(destino / "pares.jsonl"),
            "neutros.jsonl": sha256_arquivo(destino / "neutros.jsonl"),
            "casos_base.jsonl": sha256_arquivo(pasta / "casos_base.jsonl"),
            "specs.jsonl": sha256_arquivo(pasta / "specs.jsonl"),
            "lexicos.json": sha256_arquivo(RAIZ / "lexicos.json"),
        },
    }
    (destino / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    print(f"{args.dominio}/{args.saida}: {len(neutros)} neutros, {len(pares)} entradas, "
          f"diff ok {n_pares - len(falhas_diff)}/{n_pares}, hash do conjunto {hash_conjunto[:16]}…")
    if falhas_diff:
        raise SystemExit(f"ERRO: {len(falhas_diff)} pares com diff fora do slot: {falhas_diff[:5]}")


if __name__ == "__main__":
    main()
