# Avaliação da Proposta — Fase 1

## Avaliação geral

Proposta madura, estrutura clara, citações fortes. Abaixo pontos fortes, pontos fracos e nota por critério.

## Pontos positivos

**Seção 1 (Cenário e Contexto)** — liga tema a 3 ODS distintos, cita dado quantitativo concreto (redução 41%/44%/38% custo-tempo-tokens trocando só orquestração). Contextualização sólida, não genérica.

**Seção 3 (Caracterização do Problema), parágrafo 2** — melhor trecho do documento. Delimita lacuna com precisão cirúrgica: compara com `li2026aligned` (trabalho mais próximo) e explica exatamente onde diverge (rótulo categórico explícito vs. comparação pareada contrafactual sem categorização). Isso é o que separa proposta de mestrado de redação de graduação.

**Seção 4 (Proposta de Solução)** — cada arquitetura vem com hipótese mecanicista própria ("testando se..."), não é só lista de topologias decorativas. Métrica (CFR/MASD) já formalizada na literatura, não inventada ad-hoc.

**Seção 5 (Estado da Arte)** — segue template à risca: critério/extraído/adaptação por referência. Trata explicitamente da ausência de viés na lista-base antes de justificar fontes externas — atende exigência do enunciado sem que o professor precise perguntar "por que essas referências não estão na lista?".

**Escopo explícito (Seção 3, fim)** — delimita "fora do escopo" (deployment, fine-tuning, explicação causal, outros eixos de viés). Poucos alunos fazem isso sem serem cobrados.

## Pontos de melhoria

**Seção 3, item (i), linha 113** — "**analize** controlada via comparação pareada contrafactual" — erro ortográfico (correto: "análise"). Mais grave que typo isolado: esse item *descreve a solução* (comparação pareada contrafactual, variando característica) dentro da seção de Caracterização do Problema. Template é explícito: "**Não descreva a solução nesta seção.**" Método pareado contrafactual já reaparece idêntico na Seção 4 — reescrever esse item em termos de *limite do problema* (que variável, que domínios), sem antecipar o desenho metodológico.

**Confiabilidade das citações** — texto depende fortemente de papers com data 2025/2026 (`gao2026hiring`, `li2026aligned`, `okawa2026emergence`, `morla2026agentfairbench`, `mayilvaghanan2026counterfactual`, `hu2025judicial`) com estatísticas muito específicas (85,1%, 177.100 casos, 16 LLMs, ~2,4x). Antes da defesa: confirmar que essas refs existem, foram lidas na íntegra (não só abstract/resumo de terceiro), e que os números foram transcritos corretamente. Densidade de citações recentíssimas levanta suspeita de bibliografia não verificada linha a linha.

**Seção 2 (Motivação)** — atende ao pedido do template, mas fator "científico/tecnológico" e fator "prático" se sobrepõem bastante (ambos giram em torno de "não sabemos se multiagente muda o viés"). Diferenciar melhor os três fatores ou fundir dois deles.

**Título em inglês num documento em português** — inconsistente com `babel[brazilian]` do resto do texto. Padronizar idioma do título com o idioma do corpo, ou justificar a escolha (comum em papers PT-BR manter título em inglês para indexação — se for esse o motivo, não é erro, mas fica implícito).

**Métricas do estado da arte não comparadas entre si** — CFR e MASD são citadas mas o texto não diz qual será usada como principal nem por quê ambas seriam necessárias (redundantes? complementares?). Seção 4 usa as duas sem hierarquia.

**Comentário de bibliografia no código-fonte (linha 170)** — "`aasjournal.bst não instalado no sistema; trocado por estilo natbib`" é comentário de build, não afeta conteúdo, mas indica que o `.bst` exigido pelo template não foi resolvido, só contornado. Verificar se o padrão de citação exigido pela disciplina permite essa troca.

## Avaliação por critério (2 pts cada)

| Critério | Nota | Justificativa |
|---|---|---|
| Definição do cenário e contexto | 2,0/2,0 | Contextualização rica, multi-ODS, cita evidência quantitativa relevante, não genérica. |
| Definição da motivação | 1,5/2,0 | Atende estrutura pedida (critério+relevância+impacto+beneficiário+mecanismo), mas fatores se sobrepõem — falta discriminação mais nítida entre eles. |
| Definição da problemática | 1,5/2,0 | Delimitação de lacuna é o ponto mais forte do documento, mas item (i) da delimitação de escopo vaza descrição de solução, contra instrução explícita do template. |
| Definição da proposta de solução | 2,0/2,0 | 5 arquiteturas com racional causal por trás de cada uma, métrica formalizada, sem detalhe de implementação — exatamente o pedido. |
| Clareza do posicionamento com estado da arte | 2,0/2,0 | Segue formato critério/extraído/adaptação rigorosamente, trata ausência da lista-base primeiro, diferenciação com trabalho mais próximo (`li2026aligned`, `morla2026agentfairbench`) é precisa. |

**Nota final: 9,0/10**

Desconto concentrado no vazamento de solução na Seção 3 e sobreposição de fatores na Seção 2. Corrigir esses dois pontos é rápido (reescrita local, não requer nova pesquisa) — recomendo prioridade antes da entrega.
