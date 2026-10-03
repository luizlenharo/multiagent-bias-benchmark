# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Course project for UNICAMP MO810A/MC959A (Sistemas Multiagentes com Modelos de Linguagem, Prof. Julio Cesar dos Reis), by Luiz Felipe Lenharo (237896) and Felipe Rocha Verol (248552). Project: a counterfactual benchmark measuring socioeconomic bias across multi-agent LLM topologies in résumé screening and criminal verdict tasks ("Does Topology Matter?").

No implementation code exists yet — the repo currently holds the phased written deliverables (LaTeX reports, HTML slides, exported PDFs). Documents are written in Brazilian Portuguese (`babel[brazilian]`); the project title is intentionally kept in English (justified in a footnote in `proposta/template-fase1.tex`).

## Deliverable phases

Each phase is a filled-in copy of the course LaTeX template, kept in its own folder with its exported PDFs and phase-specific material. The italic `<...>` blocks preceded by `%isso deve ser removido` are the professor's instructions for each section — replace them with content and delete the instruction text.

- `proposta/` — Fase 1 (Proposta):
  - `template-fase1.tex` — cenário, motivação, problema, solução conceitual, estado da arte. Final PDFs exported as `fase1_relatorio_luiz-lenharo_felipe-verol.pdf` and `fase1_slides_luiz-lenharo_felipe-verol.pdf` (same folder).
  - `slides.html` — self-contained HTML/JS slide deck (inline CSS/JS, no build) for the Fase 1 presentation; exported to PDF manually.
  - `avaliação.md` — AI-generated critique of the Fase 1 proposal (strengths, weaknesses, per-criterion grades). Useful checklist of pitfalls to avoid in later phases, e.g.: don't describe the solution inside "Caracterização do Problema"; differentiate the motivation factors; state which metric (CFR vs. MASD) is primary and why; verify every 2025/2026 citation and statistic against the actual paper.
- `metodologia/` — Fase 2 (Metodologia), in progress: `template-fase2.tex` — visão geral, dados, arquitetura multiagente, orquestração/ferramentas, procedimentos de avaliação.
- Later phases get their own folder following the same pattern.
- `references.bib` (repo root) — shared bibliography for all phases; each phase file loads it with `\bibliography{../references}`.

Exported PDFs follow the naming `faseN_<relatorio|slides>_luiz-lenharo_felipe-verol.pdf` and live in the phase folder.

## Building

```sh
cd metodologia && latexmk -pdf template-fase2.tex   # pdflatex + bibtex; run from the phase folder
latexmk -c                                          # clean aux files (they are gitignored anyway)
```

Bibliography style gotcha: the course template uses `\bibliographystyle{aasjournal}`, but `aasjournal.bst` is not installed locally (it ships with `texlive-aastex`), so BibTeX fails and the bibliography comes out empty. Both `proposta/template-fase1.tex` and `metodologia/template-fase2.tex` work around this with `plainnat` (with a TODO to confirm with the course).

Citations use `natbib` (`\citet` / `\citep`) with keys from `references.bib` (e.g. `li2026aligned`, `morla2026agentfairbench`, `gao2026hiring`).
