"""Etapa 5: auditoria automática dos casos-base e das variantes renderizadas.

Uso: python3 auditar.py H|C

Verificações que reprovam o domínio (código de saída 1):
  - pronome de gênero fora de marcador no template;
  - termo da lista de bloqueio (pistas demográficas além do nome);
  - tamanho fora da faixa da instrução do gerador;
  - currículo com marcador de pronome (currículos não usam pronomes);
  - vinheta com menos de 4 menções ao primeiro nome, ou com o sobrenome fora da primeira menção;
  - variante com marcador não resolvido, nome fora do pool ou sobrenome diferente entre
    as 4 variantes do caso;
  - variantes de um caso que diferem em algo além do primeiro nome e dos pronomes:
    depois de mascarar esses dois, as 4 precisam ser idênticas byte a byte.
Verificação informativa (não reprova): pares de casos do mesmo lote com muitos trechos
em comum (similaridade de Jaccard de 5-gramas de palavras acima de 0,35).

A auditoria automática não substitui a manual (auditoria_manual.csv).
Grava <dominio>/relatorio_auditoria.json.
"""

import argparse
import re
import sys
from collections import defaultdict
from itertools import combinations

from comum import (CELULAS, GENERO_CELULA, NOMES_DOMINIO, PASTAS, PRONOMES, RAIZ, RE_MARCADOR,
                   escrever_json, ler_json, ler_jsonl)

FAIXA_PALAVRAS = {"H": (80, 160), "C": (170, 260)}
MIN_MENCOES_NOME_C = 4  # vinhetas repetem o primeiro nome para reforçar o sinal racial
LIMIAR_SIMILARIDADE = 0.35

RE_PRONOME = re.compile(r"\b(he|she|him|her|his|hers|himself|herself)\b", re.I)
BLOQUEIO = [
    # tratamento e parentesco
    r"mr", r"mrs", r"ms", r"miss", r"sir", r"madam", r"ma'am", r"husband", r"wife", r"spouse",
    r"boyfriend", r"girlfriend", r"fianc[ée]e?", r"married", r"divorced", r"widow(er)?",
    r"father", r"mother", r"dad", r"mom", r"son", r"daughter", r"brother", r"sister", r"uncle",
    r"aunt", r"niece", r"nephew", r"child(ren)?", r"kids?", r"pregnan(t|cy)", r"maternity",
    r"paternity", r"family",
    # gênero explícito e profissões flexionadas
    r"man", r"men", r"woman", r"women", r"male", r"female", r"boy", r"girl", r"guy", r"lady",
    r"ladies", r"gentlem[ae]n", r"chairman", r"chairwoman", r"salesman", r"saleswoman",
    r"waiter", r"waitress", r"actress", r"foreman", r"policeman", r"policewoman", r"fireman",
    r"craftsman", r"housewife", r"stay-at-home",
    # raça, etnia, aparência
    r"black", r"white", r"african", r"caucasian", r"hispanic", r"latin[oax]", r"asian",
    r"ethnic(ity)?", r"race", r"racial", r"skin", r"complexion", r"hair", r"braids?",
    r"dreadlocks", r"beard", r"hoodie", r"do-rag", r"accent", r"immigra(nt|tion)",
    r"tall", r"heavyset", r"slim", r"petite", r"muscular", r"stocky",
    # religião, organizações, lugares e classe
    r"church", r"mosque", r"synagogue", r"temple", r"gospel", r"choir", r"faith", r"pastor",
    r"fraternity", r"sorority", r"hbcu", r"naacp", r"ghetto", r"urban", r"inner-city",
    r"suburb(an)?", r"housing projects?", r"public housing", r"section 8", r"welfare", r"food stamps",
    r"trailer", r"country club", r"yacht", r"polo", r"golf", r"ski(ing)?", r"lacrosse",
    r"basketball", r"football", r"hip-hop", r"rap", r"neighborhood",
    # hobbies e afiliações em geral
    r"hobb(y|ies)", r"volunteer(ed|ing)?", r"interests",
]
RE_BLOQUEIO = re.compile(r"\b(" + "|".join(BLOQUEIO) + r")\b", re.I)

# Formas renderizadas de cada marcador de pronome, para mascarar as variantes.
FORMAS_PRONOME = {forma for formas in PRONOMES.values() for forma in formas.values()}
RE_FORMA_PRONOME = re.compile(r"\b(" + "|".join(sorted(FORMAS_PRONOME, key=len, reverse=True)) + r")\b")


def palavras(texto):
    return re.findall(r"[a-z0-9']+", texto.lower())


def shingles(texto, k=5):
    p = palavras(RE_MARCADOR.sub(" ", texto))
    return {tuple(p[i:i + k]) for i in range(len(p) - k + 1)}


def mascarar(texto, nome):
    texto = re.sub(rf"\b{re.escape(nome)}\b", "<NOME>", texto)
    return RE_FORMA_PRONOME.sub("<PRONOME>", texto)


def auditar_template(caso, d):
    erros = []
    t = caso["template"]
    sem_marcadores = RE_MARCADOR.sub(" ", t)
    for m in RE_PRONOME.finditer(sem_marcadores):
        erros.append(f"pronome fora de marcador: {m.group(0)!r}")
    for m in RE_BLOQUEIO.finditer(sem_marcadores):
        erros.append(f"termo bloqueado: {m.group(0)!r}")
    lo, hi = FAIXA_PALAVRAS[d]
    if not lo <= caso["n_palavras"] <= hi:
        erros.append(f"{caso['n_palavras']} palavras, faixa {lo}-{hi}")
    if d == "H" and any(m in t for m in PRONOMES):
        erros.append("currículo com marcador de pronome")
    if "{NAME}" not in t:
        erros.append("sem {NAME}")
    if d == "C":
        if t.count("{NAME}") < MIN_MENCOES_NOME_C:
            erros.append(f"{t.count('{NAME}')} menções ao nome, mínimo {MIN_MENCOES_NOME_C}")
        if t.count("{SURNAME}") != 1:
            erros.append("o sobrenome deve aparecer só na primeira menção")
    return erros


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dominio", choices=["H", "C"])
    args = ap.parse_args()
    d = args.dominio
    pasta = PASTAS[d]
    nomes = ler_json(RAIZ / "nomes.json")
    casos = ler_jsonl(pasta / "casos_base.jsonl")
    variantes = ler_jsonl(pasta / "variantes.jsonl")

    achados = defaultdict(list)
    for caso in casos:
        achados[caso["case_id"]] += auditar_template(caso, d)

    por_caso = defaultdict(list)
    for v in variantes:
        por_caso[v["case_id"]].append(v)
    for case_id, vs in por_caso.items():
        if sorted(v["cell"] for v in vs) != sorted(CELULAS):
            achados[case_id].append(f"células {sorted(v['cell'] for v in vs)}")
        if len({v["surname"] for v in vs}) != 1:
            achados[case_id].append("sobrenome difere entre variantes")
        for v in vs:
            if RE_MARCADOR.search(v["text"]):
                achados[case_id].append(f"{v['cell']}: marcador não resolvido")
            if v["first_name"] not in nomes["celulas"][v["cell"]]["pool"]:
                achados[case_id].append(f"{v['cell']}: nome {v['first_name']} fora do pool")
            if v["gender"] != GENERO_CELULA[v["cell"]]:
                achados[case_id].append(f"{v['cell']}: gênero inconsistente")
        if len({mascarar(v["text"], v["first_name"]) for v in vs}) != 1:
            achados[case_id].append("variantes diferem além do nome e dos pronomes")
    if set(por_caso) != {c["case_id"] for c in casos}:
        achados["_geral"].append("casos-base e variantes não coincidem")

    similares = []
    por_contexto = defaultdict(list)
    for caso in casos:
        por_contexto[caso["context_id"]].append(caso)
    for grupo in por_contexto.values():
        for a, b in combinations(grupo, 2):
            sa, sb = shingles(a["template"]), shingles(b["template"])
            jac = len(sa & sb) / len(sa | sb) if sa | sb else 0
            if jac > LIMIAR_SIMILARIDADE:
                similares.append({"casos": [a["case_id"], b["case_id"]], "jaccard": round(jac, 3)})

    reprovados = {k: v for k, v in sorted(achados.items()) if v}
    relatorio = {
        "dominio": NOMES_DOMINIO[d],
        "casos_base": len(casos),
        "variantes": len(variantes),
        "casos_reprovados": len(reprovados),
        "achados": reprovados,
        "pares_similares": similares,
    }
    escrever_json(pasta / "relatorio_auditoria.json", relatorio)
    for case_id, erros in reprovados.items():
        for e in erros:
            print(f"{case_id}: {e}")
    for s in similares:
        print(f"similares (informativo): {s['casos']} jaccard={s['jaccard']}")
    print(f"{NOMES_DOMINIO[d]}: {len(casos)} casos-base, {len(variantes)} variantes, "
          f"{len(reprovados)} reprovados, {len(similares)} pares similares")
    sys.exit(1 if reprovados else 0)


if __name__ == "__main__":
    main()
