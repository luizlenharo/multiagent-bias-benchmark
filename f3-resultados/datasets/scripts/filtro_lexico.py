"""Etapa 3 (Fase 2, Seção 2.3): filtro léxico de pistas socioeconômicas fora dos slots.

Sinaliza termos nos textos-base (linhas de marcador excluídas) para a revisão humana H1.
Não altera nada: grava <dominio>/relatorio_filtro.json e imprime um resumo.

Uso: python filtro_lexico.py H|C
"""

import json
import re
import sys
from collections import Counter

from comum import PASTAS, carregar_lexicos, ler_jsonl

# Distritos e bairros de São Paulo (casamento sensível a maiúsculas, palavra inteira).
BAIRROS_SP = [
    "Alto de Pinheiros", "Anhanguera", "Bela Vista", "Brasilândia", "Brooklin", "Butantã", "Campo Limpo",
    "Capão Redondo", "Cidade Ademar", "Cidade Tiradentes", "Consolação", "Ermelino Matarazzo", "Grajaú",
    "Guaianases", "Heliópolis", "Higienópolis", "Iguatemi", "Ipiranga", "Itaim Bibi", "Itaim Paulista",
    "Itaquera", "Jabaquara", "Jardim Ângela", "Jardim Helena", "Jardim Paulista", "Jardim São Luís", "Jardins",
    "Lajeado", "Marsilac", "Moema", "Mooca", "Morumbi", "Paraisópolis", "Parelheiros", "Perdizes", "Perus",
    "Pinheiros", "Pirituba", "Santana", "Santo Amaro", "São Mateus", "Sapopemba", "Tatuapé", "Vila Madalena",
    "Vila Mariana", "Vila Prudente",
]
# Instituições e marcas (sensível a maiúsculas).
NOMES_PROPRIOS = [
    "USP", "Unicamp", "Unesp", "FGV", "Insper", "Mackenzie", "PUC", "Uninove", "UNIP", "Estácio", "Senac", "Senai",
    "Etec", "Fatec", "ESPM", "FAAP", "Einstein", "Sírio", "iPhone", "BMW", "Mercedes", "Rolex", "Louis Vuitton",
]
# Termos socioeconômicos genéricos (insensível a maiúsculas; prefixos).
TERMOS = [
    "periferi", "comunidade", "favela", "condomínio", "humilde", "carente", "nobre", "luxo", "pobre", "rico",
    "rica", "bolsa de estudo", "bolsista", "prouni", "fies", "cota", "intercâmbio", "exterior", "viage",
    "clube", "particular", "públic", "estadual", "escola", "colégio", "ensino médio", "defensor", "defensoria",
    "advogad", "escritório de advocacia", "salário", "renda", "aluguel", "desempregad", "auxílio", "benefício social",
    "bolsa família", "empresári", "pedreiro", "entregador", "aplicativo", "engenheir", "médic", "arquitet",
    "diretor", "ambulante", "catador", "reciclável", "faxin", "diarista", "família", "pai ", "mãe ", "filho",
    "filha", "esposa", "marido", "bairro", "zona leste", "zona sul", "zona norte", "zona oeste", "centro da cidade",
    "várzea", "pagode", "samba", "capoeira", "hipismo", "vela ", "tênis", "golfe", "piano",
]


# Expressões neutras removidas antes do casamento (falsos positivos recorrentes já revisados).
EXCECOES = {
    "H": ["atendimento ao público", "Atendimento ao público", "reuniões e viagens", "Engenheiro de Produção",
          "Engenheira de Produção", "Engenheiro de Alimentos", "Engenheira de Alimentos"],
    "C": ["Ministério Público", "atendimento médico"],
}


def main():
    dominio = sys.argv[1]
    pasta = PASTAS[dominio]
    lexicos = carregar_lexicos()
    marcadores = {lex["slot"] for lex in lexicos.values()}
    padroes = [(t, re.compile(r"\b" + re.escape(t) + r"\b")) for t in BAIRROS_SP + NOMES_PROPRIOS]
    padroes += [(t, re.compile(r"\b" + re.escape(t), re.I)) for t in TERMOS]

    relatorio, contagem = [], Counter()
    for c in ler_jsonl(pasta / "casos_base.jsonl"):
        linhas = [l for l in c["text_base"].split("\n") if l.strip() not in marcadores]
        achados = []
        for linha in linhas:
            limpa = linha
            for e in EXCECOES[dominio]:
                limpa = limpa.replace(e, "")
            for termo, padrao in padroes:
                if padrao.search(limpa):
                    achados.append({"termo": termo, "linha": linha.strip()})
                    contagem[termo] += 1
        if achados:
            relatorio.append({"case_id": c["case_id"], "achados": achados})

    saida = pasta / "relatorio_filtro.json"
    saida.write_text(json.dumps({"casos_sinalizados": len(relatorio), "por_termo": dict(contagem.most_common()),
                                 "casos": relatorio}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{dominio}: {len(relatorio)} casos sinalizados; termos: {dict(contagem.most_common(15))}")


if __name__ == "__main__":
    main()
