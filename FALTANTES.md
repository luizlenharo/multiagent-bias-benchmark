# Faltantes — Fase 1 (template-fase1.tex)

## Bloqueadores de conteúdo

1. **RA do Felipe** — **feito**.
2. **Citação de viés racial/socioeconômico em decisão penal por LLM** — **feito**.
   - `hu2025judicial` (LLMs on Trial: Evaluating Judicial Fairness for Large Language Models, arXiv:2507.10852) — LLM atuando como juiz, dataset JudiFair (177.100 casos reais), viés significativo em etnia e riqueza (`defendant_wealth`) do réu em 10/13 modelos. Inserido no `references.bib` e citado na linha 88 do `template-fase1.tex`, substituindo o FALTA.
   - Candidatos anteriores descartados: Ganguli et al. 2022, arXiv:2202.07785 (abstract não menciona COMPAS/reincidência) e ICE-Guard, arXiv:2603.18530 (abstract não confirma o eixo penal do projeto). Nota residual sobre eles na linha 157 (seção Estado da Arte) removida do `.tex` — ficou obsoleta com `hu2025judicial` resolvendo o FALTA.
   - Mesma citação reaproveitada na linha 109 (parte 1 do FALTA daquela linha: "referências específicas de viés em triagem de currículo e/ou decisão penal") junto com `wilson2024gender`/`gao2026hiring`.
   - Parte 2 do FALTA da linha 109 (ineditismo do cruzamento topologia×viés) — **feito**: `li2026aligned` (Aligned Agents, Biased Swarm, arXiv:2604.08963) mostra que topologia amplifica viés demográfico (idade/gênero/raça) em cenários sintéticos genéricos, sem cobrir eixo socioeconômico nem domínio penal. Reformulamos a alegação de ineditismo do projeto: não é mais "topologia afeta viés" (já demonstrado), é "topologia afeta viés **socioeconômico** especificamente, comparado entre emprego e justiça penal sob o mesmo desenho de perturbação contrafactual" — isso continua sem cobertura na literatura.
3. **Estado da Arte** (Seção 5) — parcialmente resolvida:
   - Lista Awesome Agentic Systems (32 artigos) não tem nenhum paper sobre viés/fairness — confirmado.
   - AutoGen, MetaGPT, e Sayed Ali et al. 2026 (Harness Effect) citados como candidatos de topologia — **falta confirmar se foram de fato lidos** pelo grupo (template exige só artigos lidos).
   - 6 referências externas à lista já inseridas com critério/extraído/adaptação: Wilson & Caliskan 2024, Gallegos et al. 2024, Morla et al. 2026 (AgentFairBench), Okawa 2026, Madigan et al. 2025, Bonil et al. 2025 — todas verificadas (arXiv ID real, título/autor batem). Ver ressalvas de domínio no ponto 4.
   - Falta a referência de decisão penal (ver item 2).
4. **Ressalvas de domínio nas referências já inseridas** — nenhuma cobre exatamente emprego+penal juntos:
   - Wilson & Caliskan 2024 — só currículo, não penal.
   - Morla et al. 2026 (AgentFairBench) — hiring/lending/medical triage, **sem penal**. É o desenho mais próximo do projeto, mas precisa estender pro domínio penal.
   - Madigan et al. 2025 — domínio é finanças (credit scoring/income), não emprego/penal. Serve só como argumento por analogia (viés emergente não redutível a componentes individuais).
   - Mayilvaghanan et al. 2026 (CFR/MASD) — domínio é QA de contact center. Serve só pra definição das métricas, não como evidência do domínio do projeto.
   - `Can LLMs Hire Fairly?` (Gao, Jiang & Yan, arXiv:2606.28978) — real, 14 LLMs, mas achado é **reversão** entre gerações de modelo (2023: viés pró-branco; 2024+: reversão pró-preto ou nulo), não viés simples. Ainda não formalizada como entrada `.bib` — decidir como enquadrar o achado antes de citar.
5. **Arquiteturas finais** (Seção Proposta) — esbocei 5 candidatas como rascunho:
   - Agente único (baseline)
   - Pipeline sequencial
   - Debate/adversarial
   - Revisão hierárquica
   - Ensemble/votação
   - Decisão final de quais entram é do grupo.
6. **Métrica de viés** — candidatas formais já citadas (CFR e MASD, de Mayilvaghanan et al. 2026 e Morla et al. 2026), mas falta decidir: adotar como estão ou adaptar; como a estocasticidade do LLM (múltiplas execuções por caso) entra no teste estatístico.
7. **Datasets** — nenhum escolhido para as duas tarefas (triagem de emprego, veredicto penal). Precisa suportar os **mesmos eixos de perturbação socioeconômica** nos dois domínios, senão comparação cross-scenario quebra.
8. **Escopo de eixos de viés** — decidir se inclui raça/gênero além de socioeconômico, ou só socioeconômico puro.

## Bloqueadores técnicos (compilação) — todos resolvidos

9. ~~`references.bib` não existia~~ — **feito**: criado com 8 entradas verificadas (arXiv ID + título/autor conferidos via metadata bruta do arXiv, não só resumo de IA).
10. ~~`aasjournal.bst` não instalado~~ — **feito**: trocado por `plainnat` (natbib, já disponível no sistema).
11. ~~Pacotes texlive faltando (`babel-portuges`, `ec`, `hyphen-portuguese`)~~ — **feito**, instalados pelo usuário.
12. ~~`bibtex` binário não instalado (`texlive-bibtex`)~~ — **feito**, instalado pelo usuário.
13. Compilação atual: `pdflatex` → `bibtex` → `pdflatex` ×2 — **7 páginas, 0 erro, 0 warning** (nem missing character, nem undefined citation, nem overfull hbox).

## Decisões já tomadas (confirmar se concorda)

- ODS 10 (Redução das Desigualdades) como guarda-chuva; ODS 8 para vaga de emprego; ODS 16 para júri penal.
- Idioma do corpo: português.
- Adicionado `\usepackage[utf8]{inputenc}` e `\usepackage[T1]{fontenc}` ao preâmbulo (faltavam, acentos não renderizavam).
- `\bibliographystyle{plainnat}` no lugar de `aasjournal`.
