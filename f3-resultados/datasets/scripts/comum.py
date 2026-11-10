"""Funções compartilhadas do pipeline de geração dos datasets (Fase 2, Seção 2).

Apenas biblioteca padrão. Todas as etapas são determinísticas dada a SEMENTE.
"""

import hashlib
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent  # f3-resultados/datasets
FONTES = RAIZ / "fontes"
SEMENTE = 959

PASTAS = {"H": RAIZ / "curriculo", "C": RAIZ / "analise_penal"}
NOMES_DOMINIO = {"H": "contratacao", "C": "penal"}
ARQ_CONTEXTOS = {"H": "vagas.json", "C": "cenarios.json"}

# Células demográficas da Fase 2: raça (W/B) × gênero (M/F)
CELULAS = ["WM", "WF", "BM", "BF"]
GENERO_CELULA = {"WM": "M", "WF": "F", "BM": "M", "BF": "F"}
RACA_CELULA = {"WM": "white", "WF": "white", "BM": "black", "BF": "black"}

N_CONTEXTOS = 5          # vagas (H) ou cenários-base (C)
CASOS_POR_CONTEXTO = 10  # N = 5 × 10 = 50 casos-base por domínio

# Marcadores dos casos-base. {NAME} e {SURNAME} recebem o nome sorteado;
# os pronomes são escritos na forma masculina e flexionados pelo gênero da célula.
PRONOMES = {
    "{he}": {"M": "he", "F": "she"},
    "{He}": {"M": "He", "F": "She"},
    "{him}": {"M": "him", "F": "her"},
    "{his}": {"M": "his", "F": "her"},
    "{His}": {"M": "His", "F": "Her"},
    "{himself}": {"M": "himself", "F": "herself"},
}
MARCADORES = {"{NAME}", "{SURNAME}", *PRONOMES}
RE_MARCADOR = re.compile(r"\{[^{}]*\}")


def ler_json(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def escrever_json(caminho, obj):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ler_jsonl(caminho):
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(linha) for linha in f if linha.strip()]


def escrever_jsonl(caminho, registros):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def json_canonico(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_registro(registro):
    """Hash SHA-256 do registro canônico, sem o próprio campo sha256."""
    corpo = {k: v for k, v in registro.items() if k != "sha256"}
    return hashlib.sha256(json_canonico(corpo).encode("utf-8")).hexdigest()


def sha256_arquivo(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def contar_palavras(texto):
    return len(re.findall(r"[A-Za-z0-9$%'’.-]*[A-Za-z0-9]", texto))


def render(template, nome, sobrenome, genero):
    """Substitui nome, sobrenome e pronomes de um caso-base."""
    texto = template.replace("{NAME}", nome).replace("{SURNAME}", sobrenome)
    for marcador, formas in PRONOMES.items():
        texto = texto.replace(marcador, formas[genero])
    return texto
