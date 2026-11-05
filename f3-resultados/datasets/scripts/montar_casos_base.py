"""Junta os lotes textualizados (textos/lote_NN.md) às specs e grava casos_base.jsonl.

Validações (falham com erro):
  - case_id do lote existe nas specs e não aparece duplicado;
  - cada marcador de slot do domínio aparece exatamente uma vez, numa linha própria;
  - nenhum outro marcador {{...}} no texto;
  - o nome da pessoa avaliada (spec) aparece no texto.

Uso: python montar_casos_base.py H|C [--completo]
  --completo exige que todas as specs tenham texto (sem ele, lista as pendentes).
"""

import re
import sys

from comum import ATRIBUTOS, PASTAS, carregar_lexicos, escrever_jsonl, ler_jsonl

CABECALHO = re.compile(r"^=== ([HC]-\d{4}) ===[ \t]*$", re.M)


def ler_lotes(pasta):
    textos = {}
    for arq in sorted((pasta / "textos").glob("lote_*.md")):
        partes = CABECALHO.split(arq.read_text(encoding="utf-8"))
        for case_id, corpo in zip(partes[1::2], partes[2::2]):
            if case_id in textos:
                raise SystemExit(f"ERRO: {case_id} duplicado ({arq.name})")
            textos[case_id] = (corpo.strip(), arq.name)
    return textos


def validar(dominio, spec, texto, lexicos):
    erros = []
    linhas = [l.strip() for l in texto.split("\n")]
    marcadores = set()
    for p in ATRIBUTOS[dominio]:
        m = lexicos[p]["slot"]
        marcadores.add(m)
        if texto.count(m) != 1:
            erros.append(f"{m} aparece {texto.count(m)} vezes")
        elif m not in linhas:
            erros.append(f"{m} não está numa linha própria")
    extras = set(re.findall(r"\{\{[^}]*\}\}", texto)) - marcadores
    if extras:
        erros.append(f"marcadores desconhecidos: {sorted(extras)}")
    nome = spec["nome"] if dominio == "H" else spec["reu"]["nome"]
    if nome not in texto:
        erros.append(f"nome '{nome}' ausente")
    return erros


def main():
    dominio = sys.argv[1]
    completo = "--completo" in sys.argv
    pasta = PASTAS[dominio]
    lexicos = carregar_lexicos()
    specs = {s["case_id"]: s for s in ler_jsonl(pasta / "specs.jsonl")}
    textos = ler_lotes(pasta)

    desconhecidos = sorted(set(textos) - set(specs))
    if desconhecidos:
        raise SystemExit(f"ERRO: case_id sem spec: {desconhecidos}")

    registros, falhas = [], []
    for case_id, spec in specs.items():
        if case_id not in textos:
            continue
        texto, lote = textos[case_id]
        erros = validar(dominio, spec, texto, lexicos)
        if erros:
            falhas.append(f"{case_id} ({lote}): {'; '.join(erros)}")
            continue
        reg = {"case_id": case_id, "domain": dominio, "stratum": spec["stratum"]}
        if dominio == "H":
            reg["job_id"] = spec["job_id"]
            reg["genero"] = spec["genero"]
        else:
            reg["genero"] = spec["reu"]["genero"]
        reg["text_base"] = texto
        reg["palavras"] = len(texto.split())
        registros.append(reg)

    if falhas:
        raise SystemExit("ERRO de validação:\n  " + "\n  ".join(falhas))
    pendentes = [c for c in specs if c not in textos]
    if completo and pendentes:
        raise SystemExit(f"ERRO: {len(pendentes)} specs sem texto (primeira: {pendentes[0]})")

    escrever_jsonl(pasta / "casos_base.jsonl", registros)
    palavras = sorted(r["palavras"] for r in registros) or [0]
    print(f"{dominio}: {len(registros)} casos-base gravados; {len(pendentes)} pendentes; "
          f"palavras min/mediana/max = {palavras[0]}/{palavras[len(palavras) // 2]}/{palavras[-1]}")


if __name__ == "__main__":
    main()
