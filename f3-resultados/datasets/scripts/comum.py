"""Funções compartilhadas do pipeline de geração dos datasets (Fase 2, Seção 2).

Apenas biblioteca padrão. Todas as etapas são determinísticas dada a SEMENTE.
"""

import hashlib
import json
import random
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent  # f3-resultados/datasets
SEMENTE = 959

PASTAS = {"H": RAIZ / "curriculo", "C": RAIZ / "analise_penal"}
NOMES_DOMINIO = {"H": "contratacao", "C": "penal"}
ATRIBUTOS = {"H": ["H1", "H2", "H3"], "C": ["C1", "C2", "C3"]}
NIVEIS = ["B", "A"]
N_VARIANTES = 5


def carregar_lexicos():
    dados = json.loads((RAIZ / "lexicos.json").read_text(encoding="utf-8"))
    return {k: v for k, v in dados.items() if not k.startswith("_")}


def ler_jsonl(caminho):
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(linha) for linha in f if linha.strip()]


def escrever_jsonl(caminho, registros):
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


def valor_superficie(lexico, nivel, variante, genero):
    entrada = lexico[nivel][variante - 1]
    return entrada[genero] if isinstance(entrada, dict) else entrada


def linha_slot(lexico, nivel, variante, genero):
    return lexico["rotulo"].format(valor=valor_superficie(lexico, nivel, variante, genero))


def _padrao_linha(marcador):
    return re.compile(r"^[ \t]*" + re.escape(marcador) + r"[ \t]*$", re.M)


def normalizar(texto):
    texto = "\n".join(linha.rstrip() for linha in texto.split("\n"))
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def render(texto_base, lexicos, dominio, genero, atributo=None, nivel=None, variante=None):
    """render(s, p, l, v): insere o nível l do atributo p e omite os demais slots.

    Com atributo=None produz a versão neutra (todos os slots omitidos), usada no piloto.
    Cada marcador ocupa uma linha própria; omitir um slot remove a linha inteira.
    """
    texto = texto_base
    for p in ATRIBUTOS[dominio]:
        lex = lexicos[p]
        padrao = _padrao_linha(lex["slot"])
        if p == atributo:
            linha = linha_slot(lex, nivel, variante, genero)
            texto = padrao.sub(lambda _m: linha, texto)
        else:
            texto = re.sub(r"^[ \t]*" + re.escape(lex["slot"]) + r"[ \t]*\n?", "", texto, flags=re.M)
    return normalizar(texto)


def variante_do_caso(case_id, atributo):
    """Variante de superfície sorteada por caso e atributo, com semente fixa (mesma em B e A)."""
    return random.Random(f"{SEMENTE}-{case_id}-{atributo}").randint(1, N_VARIANTES)


def tokens_aprox(texto):
    """Contagem aproximada de tokens (palavras + pontuação). Não é o tokenizer do Llama."""
    return len(re.findall(r"\w+|[^\w\s]", texto))
