# Faltantes — Fase 1 (template-fase1.tex)

## Bloqueadores de conteúdo (não inventados, precisa preencher)

1. **RA do Felipe** — linha do autor(b), ainda placeholder. **feito**
2. **Citações de viés em LLM** (Seção Cenário/Contexto e Caracterização do Problema)
   - Estudos de viés em triagem de currículo por LLM.
   - Estudos de viés racial/socioeconômico em decisão penal (tipo COMPAS na literatura de ML tradicional, mas precisa achar equivalente em LLM/agentes).
   - Não inventei nenhum título/autor/ano — precisa localizar e confirmar.
3. **Estado da Arte** (Seção 5) — travada até resolver:
   - Lista Awesome Agentic Systems (32 artigos) **não tem nenhum paper sobre viés/fairness**.
   - Só 3 candidatos tangenciais sobre topologia: AutoGen, MetaGPT, "The Harness Effect".
   - Confirmar quais desses (se algum) foi de fato **lido** pelo grupo — template exige só artigos lidos.
   - Ainda faltam referências de fora da lista sobre viés algorítmico em RH/justiça penal (permitido pelo enunciado, mas não levantado).
   - Pra cada artigo selecionado, falta preencher: critério de seleção / o que foi extraído / adaptação exigida.
4. **Arquiteturas finais** (Seção Proposta) — esbocei 5 candidatas como rascunho:
   - Agente único (baseline)
   - Pipeline sequencial
   - Debate/adversarial
   - Revisão hierárquica
   - Ensemble/votação
   - Decisão final de quais entram é do grupo.
5. **Métrica de viés** — não definida. Opções em aberto: diferença média de score, razão de impacto adverso, teste de significância estatística (considerando múltiplas execuções por caso dada estocasticidade do LLM).
6. **Datasets** — nenhum escolhido para as duas tarefas (triagem de emprego, veredicto penal). Precisa suportar os **mesmos eixos de perturbação socioeconômica** nos dois domínios, senão comparação cross-scenario quebra.
7. **Escopo de eixos de viés** — decidir se inclui raça/gênero além de socioeconômico, ou só socioeconômico puro.

## Bloqueadores técnicos (compilação)

8. **`references.bib`** não existe no repo. Compila hoje só porque não há `\cite`. Quebra assim que adicionar citação.
9. **`aasjournal.bst`** não instalado no sistema — é estilo de astronomia, provavelmente não é o ideal para este tipo de trabalho. Vale reconsiderar `\bibliographystyle` (ex. `abnt-alf`, `plainnat`, etc).
10. **Pacotes texlive faltando** (pendente de instalação):
    - `texlive-babel-portuges`
    - `texlive-ec`
    - `texlive-hyphen-portuguese`
    - Rodar: `sudo dnf install -y texlive-babel-portuges texlive-ec texlive-hyphen-portuguese`

## Decisões já tomadas (confirmar se concorda)

- ODS 10 (Redução das Desigualdades) como guarda-chuva; ODS 8 para vaga de emprego; ODS 16 para júri penal.
- Idioma do corpo: português.
- Adicionado `\usepackage[utf8]{inputenc}` e `\usepackage[T1]{fontenc}` ao preâmbulo (faltavam, acentos não renderizavam).
