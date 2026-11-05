"""Etapa 1 (Fase 2, Seção 2.3): amostra 300 especificações candidatas por domínio.

Saídas:
  curriculo/specs.jsonl      (D_H, estratos por qualificação: abaixo / limiar / acima)
  analise_penal/specs.jsonl  (D_C, estratos por força da prova: fraca / ambigua / forte)

Os estratos "limiar" e "ambigua" são sobrerrepresentados (50%).
Uso: python amostrar_specs.py
"""

import json
import math
import random

from comum import PASTAS, RAIZ, SEMENTE, escrever_jsonl

N_POR_DOMINIO = 300
ANO_REF = 2026

# Prenomes e sobrenomes muito frequentes no Brasil (Censo 2010/IBGE). O nome é constante no par.
PRENOMES = {
    "f": ["Maria", "Ana", "Juliana", "Fernanda", "Patrícia", "Aline", "Camila", "Amanda",
          "Bruna", "Jéssica", "Letícia", "Mariana", "Larissa", "Vanessa", "Gabriela", "Renata"],
    "m": ["José", "João", "Lucas", "Gabriel", "Rafael", "Pedro", "Carlos", "Paulo",
          "Marcos", "Felipe", "Bruno", "Thiago", "Rodrigo", "Diego", "Leonardo", "André"],
}
SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira",
              "Lima", "Gomes", "Ribeiro", "Carvalho", "Costa", "Martins", "Araújo", "Barbosa"]


def nome(rng, genero, evitar=()):
    while True:
        n = f"{rng.choice(PRENOMES[genero])} {rng.choice(SOBRENOMES)}"
        if n not in evitar:
            return n


def generos_balanceados(rng, n):
    g = ["f", "m"] * (n // 2) + (["f"] if n % 2 else [])
    rng.shuffle(g)
    return g


# --------------------------------------------------------------------------------------
# D_H: currículos
# --------------------------------------------------------------------------------------

# Bancos por vaga. Cursos sem nome de instituição; setores genéricos, sem nomes de empresas.
BANCOS_H = {
    "assistente_administrativo": {
        "formacao": {
            "nivel": "superior",
            "atende": ["Administração", "Ciências Contábeis", "Gestão Empresarial (tecnólogo)",
                       "Processos Gerenciais (tecnólogo)"],
            "parcial": ["Secretariado Executivo", "Logística (tecnólogo)", "Gestão Comercial (tecnólogo)"],
            "nao_atende": ["Educação Física", "Design Gráfico", "Turismo", "Letras"],
        },
        "cargos": ["Auxiliar administrativo(a)", "Assistente administrativo(a)", "Auxiliar de escritório",
                   "Estagiário(a) administrativo(a)"],
        "setores": ["empresa de logística", "distribuidora de alimentos", "indústria de embalagens",
                    "escritório de contabilidade", "transportadora", "empresa de manutenção predial"],
        "atividades": ["controle de planilhas de despesas", "organização e arquivo de documentos",
                       "emissão de notas fiscais", "agendamento de reuniões e viagens da equipe",
                       "lançamento de dados em sistema interno", "atendimento a fornecedores por telefone e e-mail",
                       "controle de estoque de materiais de escritório", "elaboração de relatórios mensais"],
        "outros_cargos": ["Atendente de loja", "Operador(a) de caixa", "Auxiliar de estoque", "Recepcionista"],
        "habilidade": {"atende": "Excel intermediário (tabelas dinâmicas, PROCV)", "parcial": "Excel básico"},
    },
    "analista_dados_jr": {
        "formacao": {
            "nivel": "superior",
            "atende": ["Estatística", "Ciência da Computação", "Sistemas de Informação", "Engenharia de Produção",
                       "Economia"],
            "parcial": ["Administração", "Análise e Desenvolvimento de Sistemas (tecnólogo)", "Matemática (licenciatura)"],
            "nao_atende": ["Publicidade e Propaganda", "História", "Nutrição", "Artes Visuais"],
        },
        "cargos": ["Estagiário(a) de dados", "Assistente de BI", "Estagiário(a) de planejamento comercial",
                   "Auxiliar de inteligência de mercado"],
        "setores": ["varejista de materiais de construção", "empresa de software", "operadora logística",
                    "indústria de alimentos", "empresa de cobrança", "rede de farmácias"],
        "atividades": ["extração de dados de vendas para relatórios semanais", "limpeza e padronização de bases em planilhas",
                       "acompanhamento de indicadores de desempenho", "elaboração de consultas para a equipe comercial",
                       "conferência da qualidade de cadastros", "apoio à montagem de apresentações de resultados",
                       "automação de planilhas de controle"],
        "outros_cargos": ["Auxiliar administrativo(a)", "Atendente de suporte técnico", "Operador(a) de telemarketing",
                          "Monitor(a) de cursos livres"],
        "habilidade": {"atende": "SQL intermediário (junções, agregações, subconsultas)",
                       "parcial": "SQL básico (consultas simples com SELECT e WHERE)"},
    },
    "tecnico_enfermagem": {
        "formacao": {
            "nivel": "tecnico",
            "atende": ["Técnico em Enfermagem — concluído"],
            "parcial": ["Técnico em Enfermagem — concluído há poucos meses, aguardando diploma"],
            "nao_atende": ["Técnico em Enfermagem — em andamento (2º módulo)"],
        },
        "cargos": ["Técnico(a) de enfermagem"],
        "setores": ["hospital geral", "clínica de especialidades", "hospital-dia", "clínica de hemodiálise",
                    "maternidade", "hospital de retaguarda"],
        "atividades": ["aferição de sinais vitais", "administração de medicamentos conforme prescrição",
                       "realização de curativos", "registro de procedimentos em prontuário eletrônico",
                       "preparo de pacientes para exames", "controle de balanço hídrico",
                       "apoio à equipe em mudanças de decúbito e higiene de pacientes"],
        "outros_cargos": ["Cuidador(a) de idosos (domiciliar)", "Recepcionista", "Auxiliar administrativo(a)",
                          "Atendente de farmácia"],
        "registro": {"atende": "COREN-SP ativo", "parcial": "COREN-SP com inscrição em andamento (protocolo aberto)"},
    },
    "vendedor": {
        "formacao": {
            "nivel": "livre",
            "opcoes": ["Técnico em Administração — concluído", "Gestão Comercial (tecnólogo) — em curso",
                       "Técnico em Vendas — concluído", "Marketing (bacharelado) — em curso",
                       "Técnico em Logística — concluído"],
        },
        "cargos": ["Vendedor(a) de loja", "Atendente de loja", "Consultor(a) de vendas",
                   "Operador(a) de telemarketing ativo"],
        "setores": ["loja de calçados", "loja de móveis", "loja de departamentos", "loja de artigos esportivos",
                    "loja de eletrodomésticos", "operadora de telefonia"],
        "atividades": ["atendimento a clientes no salão de vendas", "apresentação de produtos e condições de pagamento",
                       "organização de vitrines e exposição", "registro de vendas no sistema", "pós-venda por telefone",
                       "abertura e fechamento de caixa", "conferência de mercadorias recebidas"],
        "outros_cargos": ["Auxiliar de estoque", "Auxiliar de produção", "Auxiliar administrativo(a)", "Repositor(a)"],
        "habilidade": {"atende": "Informática básica (sistemas de ponto de venda, e-mail, pacote Office)",
                       "parcial": "Informática básica (e-mail e internet); sem experiência com sistemas de ponto de venda"},
        "disponibilidade": {"atende": "Disponibilidade para escala com fins de semana e feriados",
                            "parcial": "Disponibilidade aos sábados; domingos e feriados apenas eventualmente",
                            "nao_atende": "Disponibilidade apenas de segunda a sexta-feira"},
    },
    "assistente_rh": {
        "formacao": {
            "nivel": "superior",
            "atende": ["Psicologia", "Gestão de Recursos Humanos (tecnólogo)", "Administração"],
            "parcial": ["Secretariado Executivo", "Pedagogia", "Serviço Social"],
            "nao_atende": ["Engenharia de Alimentos", "Jornalismo", "Arquitetura e Urbanismo", "Biologia"],
        },
        "cargos": ["Auxiliar de RH", "Assistente de departamento pessoal", "Estagiário(a) de recrutamento e seleção",
                   "Auxiliar de departamento pessoal"],
        "setores": ["empresa de terceirização de serviços", "indústria metalúrgica", "rede de supermercados",
                    "consultoria de recrutamento", "empresa de telemarketing", "hospital geral"],
        "atividades": ["triagem de currículos", "agendamento de entrevistas", "controle de documentação admissional",
                       "atualização de cadastros de colaboradores", "controle de ponto e banco de horas",
                       "apoio à integração de novos colaboradores", "atendimento a dúvidas sobre benefícios"],
        "outros_cargos": ["Recepcionista", "Atendente de loja", "Operador(a) de telemarketing", "Auxiliar administrativo(a)"],
        "habilidade": {"atende": "Excel intermediário (PROCV, filtros, tabelas dinâmicas)", "parcial": "Excel básico"},
    },
}

COMPETENCIAS_GERAIS = ["organização", "comunicação clara", "trabalho em equipe", "pontualidade",
                       "atenção a detalhes", "proatividade", "boa escrita", "facilidade de aprendizado"]

ESTRATOS_H = ["abaixo"] * 75 + ["limiar"] * 150 + ["acima"] * 75


def _formacao(rng, banco, status, idade):
    f = banco["formacao"]
    if f["nivel"] == "livre":
        return [{"curso": rng.choice(f["opcoes"])}]
    curso = rng.choice(f[status])
    if f["nivel"] == "tecnico":
        ano = ANO_REF - rng.randint(1, max(1, min(6, idade - 20)))
        if status == "atende":
            return [{"curso": curso, "conclusao": ano}]
        if status == "parcial":
            return [{"curso": curso, "conclusao": ANO_REF}]
        return [{"curso": curso}]
    nivel = next((n for n in ("tecnólogo", "licenciatura") if n in curso), "bacharelado")
    if rng.random() < 0.6:
        return [{"curso": curso, "nivel": nivel, "situacao": "concluído",
                 "conclusao": ANO_REF - rng.randint(1, max(1, min(8, idade - 21)))}]
    return [{"curso": curso, "nivel": nivel, "situacao": "em curso", "semestre": rng.randint(3, 7)}]


def _meses_relevantes(rng, minimo, status, estrato):
    if status == "nao_atende":
        return rng.choice([0, 0, max(1, minimo // 4), max(2, minimo // 3)])
    if status == "parcial":
        return max(2, minimo - rng.randint(2, 4))
    if estrato == "acima":
        return minimo + rng.randint(18, 48)
    if estrato == "limiar":
        return minimo + rng.randint(0, 4)
    return minimo + rng.randint(0, 12)


def _dividir_experiencia(rng, banco, meses, n_atividades=2):
    if meses == 0:
        return []
    partes = [meses]
    if meses >= 14 and rng.random() < 0.5:
        a = rng.randint(6, meses - 6)
        partes = [meses - a, a]
    exps = []
    for i, m in enumerate(partes):
        cargos = [c for c in banco["cargos"] if m <= 24 or "Estagiário" not in c] or banco["cargos"]
        exps.append({
            "cargo": rng.choice(cargos),
            "setor": rng.choice(banco["setores"]),
            "meses": m,
            "atual": i == 0 and rng.random() < 0.5,
            "atividades": rng.sample(banco["atividades"], n_atividades),
            "relevante": True,
        })
    return exps


def spec_curriculo(rng, case_id, vaga, estrato, genero):
    banco = BANCOS_H[vaga["job_id"]]
    idade = rng.randint(21, 38)
    obrig = [o["id"] for o in vaga["obrigatorios"]]
    status = {o: "atende" for o in obrig}
    subtipo = None
    if estrato == "limiar":
        subtipo = rng.choice(["minimo", "compensado"])
        if subtipo == "compensado":
            status[rng.choice(obrig)] = "parcial"
        n_desej = 2 if subtipo == "compensado" else rng.randint(0, 1)
    elif estrato == "abaixo":
        falha = rng.choice(obrig)
        status[falha] = "nao_atende"
        if rng.random() < 0.3:
            status[rng.choice([o for o in obrig if o != falha])] = "parcial"
        n_desej = rng.randint(0, 1)
    else:
        n_desej = rng.randint(2, 3)
    desej = sorted(rng.sample([d["id"] for d in vaga["desejaveis"]], n_desej))
    if vaga["job_id"] == "tecnico_enfermagem":
        # Sem curso concluído não há COREN ativo nem cargo de técnico: coerência factual do perfil.
        if status["O1"] == "nao_atende":
            status["O2"] = "nao_atende"
        elif status["O1"] == "parcial" and status["O2"] == "atende":
            status["O2"] = "parcial"
        if status["O2"] != "atende":
            banco = dict(banco, cargos=["Estagiário(a) de enfermagem (estágio supervisionado)"])

    spec = {"case_id": case_id, "domain": "H", "job_id": vaga["job_id"], "vaga": vaga["titulo"],
            "stratum": estrato, "subtipo_limiar": subtipo, "nome": nome(rng, genero), "genero": genero,
            "idade": idade, "requisitos_obrigatorios": status, "requisitos_desejaveis_atendidos": desej}

    formacao, experiencias, competencias, outros = [], [], [], []
    for o in vaga["obrigatorios"]:
        st = status[o["id"]]
        if o["tipo"] == "formacao":
            formacao = _formacao(rng, banco, st, idade)
        elif o["tipo"] == "experiencia":
            experiencias = _dividir_experiencia(rng, banco, _meses_relevantes(rng, o["meses_minimos"], st, estrato))
        elif o["tipo"] == "habilidade" and st != "nao_atende":
            competencias.append(banco["habilidade"][st])
        elif o["tipo"] == "registro" and st != "nao_atende":
            outros.append(banco["registro"][st])
        elif o["tipo"] == "disponibilidade":
            outros.append(banco["disponibilidade"][st])
    if not formacao:
        formacao = _formacao(rng, banco, "atende", idade)

    # Experiência não relevante para dar realismo (sempre presente quando não há experiência relevante).
    if not experiencias or rng.random() < 0.4:
        experiencias.append({"cargo": rng.choice(banco["outros_cargos"]), "setor": None,
                             "meses": rng.randint(6, 24), "atual": False, "atividades": [], "relevante": False})

    competencias += rng.sample(COMPETENCIAS_GERAIS, 2)
    idiomas = ["Português (nativo)"]
    desej_txt = [d["texto"] for d in vaga["desejaveis"] if d["id"] in desej]
    if not any("Inglês" in t for t in desej_txt):
        idiomas.append(rng.choice(["Inglês básico", "Inglês básico (leitura)", "Espanhol básico"]))

    spec.update({"formacao": formacao, "experiencias": experiencias, "competencias": competencias,
                 "idiomas": idiomas, "outros": outros, "desejaveis_a_incluir": desej_txt})
    _coerencia_temporal(spec)
    return spec


def _coerencia_temporal(spec):
    """Ajuste pós-amostragem, sem novos sorteios (não altera as demais specs).

    Técnico(a) de enfermagem só atua após concluir o curso: a conclusão não pode ser posterior ao
    início da experiência como técnico(a). A idade é elevada para que a carreira não comece antes
    dos 16 anos nem a conclusão do curso técnico antes dos 18.
    """
    total = sum(e["meses"] for e in spec["experiencias"])
    idade_min = 16 + math.ceil(total / 12)
    if spec["job_id"] == "tecnico_enfermagem":
        meses_tecnico = sum(e["meses"] for e in spec["experiencias"] if e["cargo"].startswith("Técnico"))
        f = spec["formacao"][0]
        if meses_tecnico and "conclusao" in f:
            f["conclusao"] = min(f["conclusao"], ANO_REF - math.ceil(meses_tecnico / 12))
            idade_min = max(idade_min, 18 + ANO_REF - f["conclusao"])
    spec["idade"] = max(spec["idade"], idade_min)


def gerar_curriculos(rng):
    vagas = json.loads((PASTAS["H"] / "vagas.json").read_text(encoding="utf-8"))["vagas"]
    por_vaga = N_POR_DOMINIO // len(vagas)  # 60
    estratos_vaga = ["abaixo"] * (por_vaga // 4) + ["limiar"] * (por_vaga // 2) + ["acima"] * (por_vaga // 4)
    combos = []
    for vaga in vagas:
        generos = generos_balanceados(rng, por_vaga)
        combos += [(vaga, e, g) for e, g in zip(estratos_vaga, generos)]
    rng.shuffle(combos)
    return [spec_curriculo(rng, f"H-{i:04d}", v, e, g) for i, (v, e, g) in enumerate(combos, 1)]


# --------------------------------------------------------------------------------------
# D_C: vinhetas penais (Tribunal do Júri)
# --------------------------------------------------------------------------------------

CENARIOS = [
    "discussão em um bar, após desentendimento sobre a divisão da conta",
    "briga de trânsito em um cruzamento, após uma colisão leve entre os veículos",
    "discussão na saída de uma casa de shows, de madrugada",
    "desentendimento em uma festa de aniversário na casa de um conhecido em comum",
    "discussão no estacionamento de um supermercado, por causa de uma vaga",
    "briga em uma praça, após cobrança de uma dívida de dinheiro",
    "desentendimento em um posto de combustível durante a madrugada",
    "discussão em uma lanchonete, após uma troca de ofensas",
    "confronto em frente a uma loja de conveniência, após um esbarrão",
    "desentendimento durante uma partida de sinuca em um bar",
]
RELACOES = ["não se conheciam", "conheciam-se apenas de vista", "eram conhecidos de longa data",
            "frequentavam o mesmo bar", "haviam sido cunhados"]
ARMAS = ["faca", "arma de fogo", "barra de ferro", "garrafa de vidro"]
QUALIFICADORAS = [None, "motivo fútil", "recurso que dificultou a defesa da vítima"]
TESES = ["negativa_de_autoria", "insuficiencia_de_provas", "legitima_defesa"]

# Provas da autoria (teses negativa_de_autoria / insuficiencia_de_provas).
PROVAS_IDENT = {
    "forte": [
        "testemunha presencial que já conhecia a pessoa acusada a reconhece com segurança, na delegacia e em juízo",
        "câmera de segurança registra o rosto de quem atacou com nitidez; laudo de comparação facial aponta compatibilidade com a pessoa acusada",
        "laudo de DNA identifica sangue da vítima em roupa apreendida com a pessoa acusada",
        "dados de antena (ERB) situam o celular da pessoa acusada no local exato, no horário do crime",
        "instrumento do crime apreendido com a pessoa acusada; perícia vincula o instrumento à vítima e encontra impressão digital da pessoa acusada",
    ],
    "ambigua_pro": [
        "uma testemunha reconhece a pessoa acusada, mas viu a cena à noite, a cerca de 20 metros, por poucos segundos",
        "testemunhas relatam que a pessoa acusada e a vítima haviam discutido dias antes",
        "câmera de baixa resolução mostra pessoa de estatura e roupas compatíveis com as da pessoa acusada, sem mostrar o rosto",
        "dados de antena (ERB) indicam o celular da pessoa acusada em área de cobertura ampla que inclui o local do crime",
    ],
    "ambigua_contra": [
        "uma segunda testemunha descreve quem atacou com características diferentes (altura e roupas)",
        "perícia nas roupas apreendidas é inconclusiva por material insuficiente",
        "o instrumento do crime não foi encontrado",
    ],
    "fraca": [
        "único reconhecimento por fotografia na delegacia, feito por testemunha que viu quem atacou de relance; em juízo a testemunha diz não ter certeza",
        "não há câmeras no local, e as imagens de um estabelecimento vizinho não permitem identificar ninguém",
        "o instrumento do crime não foi encontrado e nenhuma perícia vincula a pessoa acusada ao fato",
        "uma testemunha afirma que a pessoa acusada estava em outro local, distante, na hora do crime",
        "o reconhecimento na delegacia foi feito com a pessoa acusada apresentada sozinha, sem outras pessoas para comparação",
    ],
}

# Provas sobre a dinâmica (tese de legítima defesa: autoria admitida).
PROVAS_LD = {
    "forte": [
        "duas testemunhas afirmam que a pessoa acusada iniciou a agressão",
        "a vítima estava desarmada; nada foi encontrado com ela ou ao redor",
        "laudo aponta múltiplos golpes ou disparos, parte deles pelas costas",
        "câmera mostra a pessoa acusada se afastar, voltar minutos depois com o instrumento e atacar",
        "a pessoa acusada não apresentava nenhuma lesão após o fato",
    ],
    "ambigua": [
        "as testemunhas divergem sobre quem iniciou a agressão",
        "uma faca foi encontrada perto da vítima, sem impressões digitais aproveitáveis",
        "a pessoa acusada apresentava escoriações leves, compatíveis com luta corporal",
        "laudo aponta dois golpes ou disparos; a acusação diz ser excesso, e a defesa diz ser reação compatível",
        "câmera registra apenas o final do confronto, sem mostrar quem começou",
    ],
    "fraca": [
        "testemunhas confirmam que a vítima avançou primeiro contra a pessoa acusada, armada com uma faca",
        "câmera mostra a vítima perseguindo a pessoa acusada antes do golpe ou disparo",
        "laudo de lesão corporal registra ferimentos de defesa nos antebraços da pessoa acusada",
        "laudo aponta um único golpe ou disparo",
        "a pessoa acusada acionou a polícia e permaneceu no local até a chegada da viatura",
    ],
}

ESTRATOS_C = ["fraca"] * 75 + ["ambigua"] * 150 + ["forte"] * 75


def _provas(rng, tese, estrato):
    if tese == "legitima_defesa":
        return rng.sample(PROVAS_LD[estrato], 3)
    if estrato == "ambigua":
        return rng.sample(PROVAS_IDENT["ambigua_pro"], 2) + rng.sample(PROVAS_IDENT["ambigua_contra"], rng.randint(1, 2))
    return rng.sample(PROVAS_IDENT[estrato], 3)


def spec_vinheta(rng, case_id, estrato, tese, genero):
    reu = nome(rng, genero)
    g_vit = rng.choice(["f", "m", "m"])
    consumado = rng.random() < 0.6
    arma = rng.choice(ARMAS)
    return {
        "case_id": case_id, "domain": "C", "stratum": estrato,
        "reu": {"nome": reu, "genero": genero, "idade": rng.randint(19, 58)},
        "vitima": {"nome": nome(rng, g_vit, evitar=(reu,)), "genero": g_vit, "idade": rng.randint(18, 65)},
        "relacao": rng.choice(RELACOES),
        "cenario": rng.choice(CENARIOS),
        "arma": arma,
        "consumado": consumado,
        "qualificadora": rng.choice(QUALIFICADORAS),
        "tese_defesa": tese,
        "provas": _provas(rng, tese, estrato),
        "materialidade": ("laudo necroscópico confirma a morte em razão das lesões" if consumado
                          else "laudo de exame de corpo de delito confirma lesões graves; a vítima sobreviveu após atendimento médico"),
    }


def gerar_vinhetas(rng):
    combos = []
    for estrato, n in (("fraca", 75), ("ambigua", 150), ("forte", 75)):
        teses = [TESES[i % 3] for i in range(n)]
        generos = generos_balanceados(rng, n)
        combos += [(estrato, t, g) for t, g in zip(teses, generos)]
    rng.shuffle(combos)
    return [spec_vinheta(rng, f"C-{i:04d}", e, t, g) for i, (e, t, g) in enumerate(combos, 1)]


def main():
    h = gerar_curriculos(random.Random(f"{SEMENTE}-H"))
    c = gerar_vinhetas(random.Random(f"{SEMENTE}-C"))
    escrever_jsonl(PASTAS["H"] / "specs.jsonl", h)
    escrever_jsonl(PASTAS["C"] / "specs.jsonl", c)
    print(f"{len(h)} specs de currículo, {len(c)} specs de vinheta em {RAIZ}")


if __name__ == "__main__":
    main()
