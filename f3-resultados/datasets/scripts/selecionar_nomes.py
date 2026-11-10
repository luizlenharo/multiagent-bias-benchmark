"""Etapa 1: escolhe os M = 3 nomes de cada célula demográfica e os sobrenomes neutros.

Lê as tabelas de datasets/fontes/ (geradas por preparar_fontes.py) e grava nomes.json.

Regra dos primeiros nomes, por célula (raça × gênero):
  1. candidatos: nomes de Gaddis (2017) da raça da célula;
  2. gênero validado por Hayes & Elder (2023): proporção feminina no cadastro eleitoral
     da Carolina do Norte >= 0,95 (F) ou <= 0,05 (M); nomes sem esse dado são excluídos;
  3. raça percebida em Hayes & Elder igual à da célula (replicação da percepção);
  4. pontuação = min(percepção sem sobrenome, percepção com sobrenome incongruente)
     em Gaddis. Os sobrenomes do benchmark não são congruentes com a raça do nome,
     então a condição congruente (a que ordena as figuras do artigo) não é usada;
  5. ficam os M nomes de maior pontuação.

Regra dos sobrenomes: sobrenomes avaliados por Hayes & Elder com notas de "African
American" e "white" que diferem em no máximo 0,10, e que no Censo de 2010 têm ao menos
30% de portadores brancos e 30% de portadores negros.
"""

import csv

from comum import CELULAS, FONTES, GENERO_CELULA, RACA_CELULA, RAIZ, escrever_json

M = 3
LIMIAR_GENERO = 0.05
DIF_MAX_SOBRENOME = 0.10
PCT_MIN_CENSO = 30.0


def ler_csv(nome):
    with open(FONTES / nome, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def genero_ok(hayes, genero):
    pct_f = float(hayes["pct_f_nc"])
    return pct_f >= 1 - LIMIAR_GENERO if genero == "F" else pct_f <= LIMIAR_GENERO


def main():
    gaddis = ler_csv("gaddis2017_percepcao.csv")
    hayes = {r["nome"].lower(): r for r in ler_csv("hayes_elder2023_nomes.csv")}

    celulas = {}
    for celula in CELULAS:
        raca, genero = RACA_CELULA[celula], GENERO_CELULA[celula]
        candidatos = []
        for g in gaddis:
            h = hayes.get(g["nome"].lower())
            if g["raca"] != raca or g["nome"] == "OVERALL" or not h:
                continue
            if not genero_ok(h, genero) or h["raca_percebida"] != raca:
                continue
            sem, inc = float(g["pct_sem_sobrenome"]), float(g["pct_sobrenome_incongruente"])
            candidatos.append({
                "nome": g["nome"],
                "pontuacao": min(sem, inc),
                "gaddis_pct_sem_sobrenome": sem,
                "gaddis_pct_sobrenome_incongruente": inc,
                "gaddis_pct_sobrenome_congruente": float(g["pct_sobrenome_congruente"]),
                "hayes_pct_f_nc": float(h["pct_f_nc"]),
                "hayes_nota_african_american": float(h["nota_african_american"]),
                "hayes_nota_white": float(h["nota_white"]),
            })
        candidatos.sort(key=lambda c: (-c["pontuacao"], c["nome"]))
        celulas[celula] = {
            "raca": raca,
            "genero": genero,
            "pool": [c["nome"] for c in candidatos[:M]],
            "ranking": candidatos[:M + 4],  # os 3 escolhidos e os 4 seguintes, para referência
        }

    censo = {r["sobrenome"]: r for r in ler_csv("censo2010_sobrenomes.csv")}
    sobrenomes = []
    for s in ler_csv("hayes_elder2023_sobrenomes.csv"):
        aa, wh = float(s["nota_african_american"]), float(s["nota_white"])
        c = censo.get(s["sobrenome"])
        if not c or abs(aa - wh) > DIF_MAX_SOBRENOME:
            continue
        if float(c["pctwhite"]) < PCT_MIN_CENSO or float(c["pctblack"]) < PCT_MIN_CENSO:
            continue
        sobrenomes.append({"sobrenome": s["sobrenome"], "hayes_nota_african_american": aa,
                           "hayes_nota_white": wh, "censo_pctwhite": float(c["pctwhite"]),
                           "censo_pctblack": float(c["pctblack"])})

    saida = {
        "_descricao": "Pools de primeiros nomes por célula e sobrenomes neutros. Gerado por "
                      "scripts/selecionar_nomes.py; a regra está na docstring do script.",
        "M": M,
        "celulas": celulas,
        "sobrenomes": sobrenomes,
    }
    escrever_json(RAIZ / "nomes.json", saida)
    for celula, d in celulas.items():
        print(f"{celula}: {', '.join(d['pool'])}")
    print("sobrenomes:", ", ".join(s["sobrenome"] for s in sobrenomes))


if __name__ == "__main__":
    main()
