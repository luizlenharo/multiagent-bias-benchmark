"""Verifica a fidelidade entre cada spec e o texto-base gerado (complementa montar_casos_base.py).

Checagens mecânicas, por palavra-chave. Um achado indica um caso a reler, não necessariamente um erro.
Uso: python checar_fidelidade.py H|C
"""

import re
import sys

from comum import PASTAS, ler_jsonl

# ---------------------------------------------------------------- D_H

DESEJAVEIS = {
    "assistente_administrativo": {"D1": r"SAP|TOTVS", "D2": r"contas a pagar", "D3": r"[Ii]nglês intermediário"},
    "analista_dados_jr": {"D1": r"Python", "D2": r"Power BI|Tableau", "D3": r"[Ii]nglês intermediário"},
    "tecnico_enfermagem": {"D1": r"UTI|pronto-socorro|pronto atendimento|urgência", "D2": r"BLS",
                           "D3": r"12x36"},
    "vendedor": {"D1": r"\bmetas?\b", "D2": r"eletroeletrônicos|eletrônicos", "D3": r"técnicas de vendas|negociação"},
    "assistente_rh": {"D1": r"folha de pagamento|eSocial", "D2": r"[Cc]ondu[zç]", "D3": r"ATS|ponto eletrônico"},
}
HABILIDADE = {  # requisito do tipo habilidade/registro: id, padrão "atende", padrão "parcial", raiz que não pode aparecer se "nao_atende"
    "assistente_administrativo": ("O3", r"Excel intermediário", r"Excel básico", r"Excel"),
    "assistente_rh": ("O3", r"Excel intermediário", r"Excel básico", r"Excel"),
    "analista_dados_jr": ("O2", r"SQL intermediário", r"SQL básico", r"SQL"),
    "vendedor": ("O3", r"sistemas de ponto de venda, e-mail, pacote Office", r"sem experiência com sistemas de ponto de venda", r"ponto de venda"),
    "tecnico_enfermagem": ("O2", r"COREN-SP ativo", r"inscrição em andamento", r"COREN"),
}
MASC = r"\b(Estagiário|Técnico de enfermagem|Vendedor|Consultor|Operador|Repositor|Monitor|Cuidador|administrativo)\b"
FEM = r"\b(Estagiária|Técnica de enfermagem|Vendedora|Consultora|Operadora|Repositora|Monitora|Cuidadora|administrativa)\b"
DURACAO = re.compile(r"\((?:(\d+) anos?(?: e (\d+) m(?:ês|eses))?|(\d+) m(?:ês|eses))")


def checar_h(spec, texto):
    achados = []
    if f"Idade: {spec['idade']} anos" not in texto:
        achados.append("idade divergente")
    for did, pad in DESEJAVEIS[spec["job_id"]].items():
        tem = re.search(pad, texto) is not None
        if tem != (did in spec["requisitos_desejaveis_atendidos"]):
            achados.append(f"desejável {did} {'presente sem estar na spec' if tem else 'ausente'}")
    oid, ok, parcial, raiz = HABILIDADE[spec["job_id"]]
    st = spec["requisitos_obrigatorios"][oid]
    if st == "atende" and not re.search(ok, texto):
        achados.append(f"{oid} atende sem '{ok}'")
    if st == "parcial" and not re.search(parcial, texto):
        achados.append(f"{oid} parcial sem '{parcial}'")
    if st == "nao_atende" and re.search(raiz, texto):
        achados.append(f"{oid} nao_atende mas cita '{raiz}'")
    for f in spec["formacao"]:
        if "conclusao" in f and str(f["conclusao"]) not in texto:
            achados.append(f"ano de conclusão {f['conclusao']} ausente")
    meses_txt = sorted(int(a or 0) * 12 + int(b or 0) + int(c or 0) for a, b, c in DURACAO.findall(texto))
    meses_spec = sorted(e["meses"] for e in spec["experiencias"])
    if meses_txt != meses_spec:
        achados.append(f"durações {meses_txt} != spec {meses_spec}")
    linhas_exp = [l for l in texto.split("\n") if l.startswith(("- ", "Objetivo:")) and ("(" in l or "Objetivo" in l)]
    pad = MASC if spec["genero"] == "f" else FEM
    for l in linhas_exp:
        if re.search(pad, l) and "Técnico em Enfermagem" not in l:
            achados.append(f"flexão de gênero: {l.strip()[:60]}")
    return achados


# ---------------------------------------------------------------- D_C

CHAVES_PROVA = [
    ("DNA", r"DNA"), ("comparação facial", r"comparação facial"), ("local exato", r"local exato"),
    ("impressão digital da pessoa acusada", r"impressão digital d[oa] acusad[oa]"),
    ("reconhece com segurança", r"com segurança"), ("cerca de 20 metros", r"cerca de 20 metros"),
    ("discutido dias antes", r"discutido dias antes"), ("baixa resolução", r"baixa resolução"),
    ("cobertura ampla", r"cobertura ampla"), ("segunda testemunha", r"segunda testemunha"),
    ("inconclusiva", r"inconclusiva"), ("de relance", r"de relance"),
    ("apresentada sozinha", r"apresentad[oa] sozinh[oa]|apresentada sozinha"),
    ("outro local, distante", r"outro local, distante"), ("estabelecimento vizinho", r"estabelecimento vizinho"),
    ("iniciou a agressão", r"iniciou a agressão"), ("estava desarmada", r"estava desarmada"),
    ("múltiplos golpes", r"múltiplos (golpes|disparos)"), ("voltar minutos depois", r"voltar (minutos depois )?com"),
    ("nenhuma lesão", r"nenhuma lesão"), ("divergem", r"divergem"),
    ("sem impressões digitais aproveitáveis", r"sem impressões digitais aproveitáveis"),
    ("escoriações leves", r"escoriações leves"), ("dois golpes", r"dois (golpes|disparos)"),
    ("apenas o final", r"apenas o final"), ("avançou primeiro", r"avançou primeiro"),
    ("perseguindo", r"perseguindo"), ("ferimentos de defesa", r"ferimentos de defesa"),
    ("único golpe", r"único (golpe|disparo)"), ("acionou a polícia", r"acionou a polícia"),
    ("instrumento do crime não foi encontrado", r"não foi encontrad[oa]"),
]
TESE = {"negativa_de_autoria": r"\bnega\b", "insuficiencia_de_provas": r"permaneceu em silêncio",
        "legitima_defesa": r"\badmite\b"}
ARTIGO = {None: r"art\. 121, caput", "motivo fútil": r"§ 2º, II\b", "recurso que dificultou a defesa da vítima": r"§ 2º, IV\b"}


def secao(texto, titulo):
    m = re.search(rf"^{titulo}\n(.*?)(?=\n\n|\Z)", texto, re.S | re.M)
    return m.group(1) if m else ""


def checar_c(spec, texto):
    achados = []
    r, v = spec["reu"], spec["vitima"]
    if f"{'Acusada' if r['genero'] == 'f' else 'Acusado'}: {r['nome']}, {r['idade']} anos" not in texto:
        achados.append("cabeçalho do réu divergente")
    if v["nome"] not in texto or f"{v['idade']} anos" not in texto:
        achados.append("vítima: nome ou idade ausente")
    imput = secao(texto, "Imputação")
    if spec["consumado"] == ("Tentativa" in imput):
        achados.append("consumado/tentado divergente na imputação")
    if not re.search(ARTIGO[spec["qualificadora"]], imput):
        achados.append("artigo/qualificadora divergente")
    provas = secao(texto, "Provas produzidas")
    mat = "necroscópico" if spec["consumado"] else "corpo de delito"
    if mat not in provas:
        achados.append(f"materialidade sem '{mat}'")
    n_bullets = provas.count("\n- ") + provas.startswith("- ")
    if n_bullets != 1 + len(spec["provas"]):
        achados.append(f"{n_bullets} provas no texto, {1 + len(spec['provas'])} esperadas")
    for p in spec["provas"]:
        for chave, pad in CHAVES_PROVA:
            if chave in p and not re.search(pad, provas):
                achados.append(f"prova sem '{chave}'")
                break
    if not re.search(TESE[spec["tese_defesa"]], secao(texto, "Tese da defesa")):
        achados.append(f"tese da defesa não corresponde a {spec['tese_defesa']}")
    if re.search(r"inquérito|indicaram", secao(texto, "Tese da acusação")):
        achados.append("acusação cita elemento fora das provas listadas")
    return achados


def main():
    dominio = sys.argv[1]
    pasta = PASTAS[dominio]
    specs = {s["case_id"]: s for s in ler_jsonl(pasta / "specs.jsonl")}
    total = 0
    for c in ler_jsonl(pasta / "casos_base.jsonl"):
        s = specs[c["case_id"]]
        achados = checar_h(s, c["text_base"]) if dominio == "H" else checar_c(s, c["text_base"])
        for a in achados:
            print(f"{c['case_id']}: {a}")
        total += len(achados)
    print(f"{dominio}: {total} achados")


if __name__ == "__main__":
    main()
