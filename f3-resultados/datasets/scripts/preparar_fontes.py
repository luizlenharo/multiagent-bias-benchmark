"""Etapa 0: extrai das fontes externas as tabelas usadas na seleção de nomes.

Entradas (baixadas à parte, ver README):
  --gaddis    PDF de Gaddis (2017), Sociological Science 4:469-489
  --hayes     pasta com nameratings.tab e lastname_traitratings.tab de
              Hayes & Elder (2023), doi:10.7910/DVN/0LCYN5 (formato original, CSV)
  --censo     Names_2010Census.csv (U.S. Census Bureau, sobrenomes de 2010)

Saídas em datasets/fontes/:
  gaddis2017_percepcao.csv   taxa de percepção congruente de cada nome nas três
                             condições de sobrenome, medida nos pixels das Figuras 1 e 2
  hayes_elder2023_nomes.csv  gênero (cadastro eleitoral da Carolina do Norte) e raça
                             percebida dos nomes de Gaddis cobertos por Hayes & Elder
  hayes_elder2023_sobrenomes.csv  raça percebida dos sobrenomes avaliados
  censo2010_sobrenomes.csv   composição racial no Censo de 2010 desses sobrenomes

As figuras de Gaddis não trazem os valores numéricos. O script renderiza as páginas
10 e 11 do PDF a 300 dpi (pdftoppm, do poppler), localiza as barras pela cor e
converte o comprimento em porcentagem pelas linhas de grade. A extração é validada
contra os valores citados no texto do artigo (linha OVERALL, Cheyanne e Maxwell).
"""

import argparse
import csv
import subprocess
import tempfile
from pathlib import Path

from comum import FONTES

# Rótulos das Figuras 1 e 2, de cima para baixo, transcritos das imagens.
ROTULOS_FIG1 = """Bria Sade Kaylah Lyric Jasmine Nia Kiara Reginald Aniya Hakim Malia Octavia Jalen
Chanel Amari Maurice Quincy Tevin Andre Cedric Shania Malcolm Kimani Savion Wendell Marques Dwayne
Delroy Jabari Leroy Jerome Monique Kevon OVERALL Erykah Jada Jermaine Kenya Aaliyah Divine Marquise
Darius Precious Terell Lamar Darnell Tamia Aisha Keisha Jaleel Ashanti Unique Heaven Taniya Denisha
Kareem Ebony Tyra D'Andre Rasheed Shanice DeShawn Terrell Latonya Tionna Keyana Latoya Jayvon Latrell
Denzel Keyshawn Tyrone DeAndre Tamika Janae Lakisha DaQuan Jamal Tremayne Tanisha DaShawn""".split()
ROTULOS_FIG2 = """Cheyanne Maxwell Mayer Irvin Chloe Edgar Caleb Edwin Deborah Melany Jordy August
Ronny Daniel Brenda Robert Charlie Geoffrey Joan Carrie Charlotte Katie Marlene Lisa Jay OVERALL Brian
Lesly Aubrey Greg Spencer Wyatt Madeline Erica Brad Cassie Angie Cody Mary Brendan Harper Paul Erin
Finn Barbara Graham Luke Anne Steven Allison Susan Heidi Neil Connor Amy Ethan Margaret Meredith Brett
Dustin Hilary Jill Molly Scott Sarah Ryan Emily Kristen Megan Logan Abigail Stephanie Matthew Laurie
Todd Zachary Seth Jake Claire Hunter Katelyn""".split()

# Em cada linha, as barras aparecem na ordem verde, vermelha, azul.
# Fig. 1 (nomes negros): verde = sobrenome branco, vermelha = sobrenome negro.
# Fig. 2 (nomes brancos): verde = sobrenome negro, vermelha = sobrenome branco.
CORES = {"verde": (155, 187, 89), "vermelha": (192, 80, 77), "azul": (79, 129, 189)}
FIGURAS = [
    {"pagina": 10, "raca": "black", "rotulos": ROTULOS_FIG1,
     "condicao": {"verde": "pct_sobrenome_incongruente", "vermelha": "pct_sobrenome_congruente",
                  "azul": "pct_sem_sobrenome"}},
    {"pagina": 11, "raca": "white", "rotulos": ROTULOS_FIG2,
     "condicao": {"verde": "pct_sobrenome_incongruente", "vermelha": "pct_sobrenome_congruente",
                  "azul": "pct_sem_sobrenome"}},
]
# Valores citados no texto de Gaddis (2017, p. 480), usados para validar a extração.
VALIDACAO = [
    ("black", "OVERALL", "pct_sem_sobrenome", 75.0),
    ("black", "OVERALL", "pct_sobrenome_congruente", 82.5),
    ("black", "OVERALL", "pct_sobrenome_incongruente", 66.5),
    ("white", "OVERALL", "pct_sem_sobrenome", 87.3),
    ("white", "OVERALL", "pct_sobrenome_congruente", 92.4),
    ("white", "OVERALL", "pct_sobrenome_incongruente", 67.9),
    ("white", "Cheyanne", "pct_sobrenome_congruente", 55.6),
    ("white", "Maxwell", "pct_sobrenome_congruente", 74.3),
]
TOLERANCIA = 1.0  # pontos percentuais; o maior desvio observado é 0,8 (OVERALL negro, sem sobrenome)


def ler_ppm(caminho):
    dados = Path(caminho).read_bytes()
    _, dims, _, pixels = dados.split(b"\n", 3)
    largura, altura = map(int, dims.split())
    return largura, altura, pixels


def perto(pixel, cor, tol=12):
    return all(abs(a - b) <= tol for a, b in zip(pixel, cor))


def extrair_figura(ppm, fig):
    largura, altura, px = ler_ppm(ppm)
    # 1. barras: faixas horizontais contíguas de uma mesma cor
    barras = []
    for y in range(altura):
        linha = px[y * largura * 3:(y + 1) * largura * 3]
        for nome_cor, cor in CORES.items():
            xs = [x for x in range(largura) if perto(linha[x * 3:x * 3 + 3], cor)]
            if len(xs) <= 20:
                continue
            b = barras[-1] if barras else None
            if b and b["cor"] == nome_cor and y - b["y1"] <= 1:
                b["y1"], b["x1"] = y, max(b["x1"], max(xs))
            else:
                barras.append({"cor": nome_cor, "y0": y, "y1": y, "x1": max(xs)})
    rotulos = fig["rotulos"]
    if len(barras) != 3 * len(rotulos):
        raise SystemExit(f"página {fig['pagina']}: {len(barras)} barras, esperava {3 * len(rotulos)}")
    # 2. eixo: linhas de grade verticais em cinza (0%, 10%, ..., 100%)
    y0, y1 = barras[0]["y0"], barras[-1]["y1"]
    contagem = []
    for x in range(largura):
        n = 0
        for y in range(y0, y1, 2):
            p = px[(y * largura + x) * 3:(y * largura + x) * 3 + 3]
            n += p[0] == p[1] == p[2] and p[0] < 200
        contagem.append(n)
    grades = [x for x in range(largura) if contagem[x] > 0.5 * (y1 - y0) / 2]
    x_zero, x_cem = grades[0] + 1, grades[-1]
    # 3. porcentagens, linha a linha
    linhas = []
    for i, rotulo in enumerate(rotulos):
        trio = barras[3 * i:3 * i + 3]
        if [b["cor"] for b in trio] != ["verde", "vermelha", "azul"]:
            raise SystemExit(f"página {fig['pagina']}, linha {rotulo}: ordem de cores inesperada")
        reg = {"nome": rotulo, "raca": fig["raca"]}
        for b in trio:
            reg[fig["condicao"][b["cor"]]] = round(100 * (b["x1"] - x_zero + 1) / (x_cem - x_zero + 1), 1)
        linhas.append(reg)
    return linhas


def extrair_gaddis(pdf):
    registros = []
    with tempfile.TemporaryDirectory() as tmp:
        for fig in FIGURAS:
            prefixo = Path(tmp) / f"p{fig['pagina']}"
            subprocess.run(["pdftoppm", "-r", "300", "-f", str(fig["pagina"]), "-l", str(fig["pagina"]),
                            "-singlefile", str(pdf), str(prefixo)], check=True)
            registros += extrair_figura(prefixo.with_suffix(".ppm"), fig)
    indice = {(r["raca"], r["nome"]): r for r in registros}
    for raca, nome, campo, esperado in VALIDACAO:
        obtido = indice[(raca, nome)][campo]
        if abs(obtido - esperado) > TOLERANCIA:
            raise SystemExit(f"validação falhou: {nome} ({raca}) {campo} = {obtido}, texto diz {esperado}")
        print(f"  ok: {nome} ({raca}) {campo} = {obtido} (texto: {esperado})")
    return registros


def ler_csv(caminho):
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def escrever_csv(caminho, registros, campos):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
        w.writeheader()
        w.writerows(registros)


def num(valor, casas):
    return "" if valor in ("", "NA", "(S)") else str(round(float(valor), casas))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gaddis", required=True, type=Path)
    ap.add_argument("--hayes", required=True, type=Path)
    ap.add_argument("--censo", required=True, type=Path)
    args = ap.parse_args()

    print("Gaddis (2017), Figuras 1 e 2:")
    gaddis = extrair_gaddis(args.gaddis)
    campos_g = ["nome", "raca", "pct_sobrenome_congruente", "pct_sobrenome_incongruente", "pct_sem_sobrenome"]
    escrever_csv(FONTES / "gaddis2017_percepcao.csv", gaddis, campos_g)

    nomes_gaddis = {r["nome"].lower() for r in gaddis if r["nome"] != "OVERALL"}
    hayes = []
    for r in ler_csv(args.hayes / "nameratings.tab"):
        if r["name"].lower() in nomes_gaddis:
            hayes.append({"nome": r["name"], "genero_nc": r["gender"], "pct_f_nc": num(r["pct_f"], 4),
                          "raca_percebida": r["race"], "nota_african_american": num(r["African.American"], 2),
                          "nota_white": num(r["white"], 2), "nota_a_man": num(r["a.man"], 2),
                          "nota_a_woman": num(r["a.woman"], 2)})
    escrever_csv(FONTES / "hayes_elder2023_nomes.csv", hayes, list(hayes[0]))

    sobrenomes = []
    for r in ler_csv(args.hayes / "lastname_traitratings.tab"):
        sobrenomes.append({"sobrenome": r["name"], "nota_african_american": num(r["African American"], 2),
                           "nota_white": num(r["white"], 2), "nota_hispanic": num(r["Hispanic"], 2),
                           "nota_asian": num(r["Asian"], 2)})
    escrever_csv(FONTES / "hayes_elder2023_sobrenomes.csv", sobrenomes, list(sobrenomes[0]))

    alvo = {s["sobrenome"].upper() for s in sobrenomes}
    censo = [{"sobrenome": r["name"].title(), "posicao": r["rank"], "pctwhite": r["pctwhite"],
              "pctblack": r["pctblack"], "pcthispanic": r["pcthispanic"], "pctapi": r["pctapi"]}
             for r in ler_csv(args.censo) if r["name"] in alvo]
    escrever_csv(FONTES / "censo2010_sobrenomes.csv", censo, list(censo[0]))

    print(f"{len(gaddis)} linhas de Gaddis, {len(hayes)} nomes e {len(sobrenomes)} sobrenomes de "
          f"Hayes & Elder, {len(censo)} sobrenomes do Censo -> {FONTES}")


if __name__ == "__main__":
    main()
