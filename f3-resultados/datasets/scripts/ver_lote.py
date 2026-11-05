"""Mostra um lote de especificações em formato compacto, para a etapa de textualização.

Uso: python ver_lote.py H 1      (lote 1 = casos H-0001..H-0020)
"""

import sys

from comum import PASTAS, ler_jsonl

TAMANHO_LOTE = 20
SIGLAS = {"assistente_administrativo": "AA", "analista_dados_jr": "AD", "tecnico_enfermagem": "TE",
          "vendedor": "VE", "assistente_rh": "RH"}


def resumo_h(s):
    form = "; ".join(
        f["curso"] + (f" ({f['nivel']})" if "nivel" in f and f["nivel"] not in f["curso"] else "")
        + (f", concl. {f['conclusao']}" if "conclusao" in f else "")
        + (f", em curso {f['semestre']}º sem." if f.get("situacao") == "em curso" else "")
        for f in s["formacao"])
    exps = " || ".join(
        f"{e['cargo']} @ {e['setor'] or '-'} {e['meses']}m{' atual' if e['atual'] else ''}"
        + (f" [{'; '.join(e['atividades'])}]" if e["atividades"] else "")
        + ("" if e["relevante"] else " (não relevante)")
        for e in s["experiencias"])
    req = ",".join(f"{k}={v[0:3]}" for k, v in s["requisitos_obrigatorios"].items())
    return (f"{s['case_id']} | {SIGLAS[s['job_id']]} | {s['stratum']}/{s['subtipo_limiar'] or '-'} | {req} | "
            f"{s['nome']} {s['genero']} {s['idade']} | F: {form} | E: {exps} | C: {'; '.join(s['competencias'])} | "
            f"I: {'; '.join(s['idiomas'])} | O: {'; '.join(s['outros']) or '-'} | "
            f"D+: {'; '.join(s['desejaveis_a_incluir']) or '-'}")


def resumo_c(s):
    r, v = s["reu"], s["vitima"]
    return (f"{s['case_id']} | {s['stratum']} | {s['tese_defesa']} | réu {r['nome']} {r['genero']} {r['idade']} | "
            f"vít {v['nome']} {v['genero']} {v['idade']} | {s['relacao']} | {s['cenario']} | {s['arma']} | "
            f"{'consumado' if s['consumado'] else 'tentado'} | qualif: {s['qualificadora'] or 'simples'} | "
            f"P: {' / '.join(s['provas'])}")


def main():
    dominio, lote = sys.argv[1], int(sys.argv[2])
    specs = ler_jsonl(PASTAS[dominio] / "specs.jsonl")
    for s in specs[(lote - 1) * TAMANHO_LOTE: lote * TAMANHO_LOTE]:
        print(resumo_h(s) if dominio == "H" else resumo_c(s))


if __name__ == "__main__":
    main()
