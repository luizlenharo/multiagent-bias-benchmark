# Fase 3 – Resultado prático

Esta pasta reúne a implementação da Fase 3. A primeira parte entregue é o **dataset sintético** do benchmark, gerado conforme a Seção 2 da metodologia revisada (`../f2-metodologia/fase2_metodologia_luiz-lenharo_felipe-verol_2.pdf`).

Resumo do desenho (Fase 2):

- auditoria contrafactual pareada em que só o primeiro nome (e os pronomes que dependem dele) varia;
- quatro células demográficas: homem branco (WM), mulher branca (WF), homem negro (BM) e mulher negra (BF);
- M = 3 nomes por célula, retirados de Gaddis (2017) e validados com Hayes & Elder (2023);
- sobrenome fixo e neutro dentro de cada caso;
- 5 vagas × 10 currículos limítrofes (D_H) e 5 cenários × 10 vinhetas limítrofes (D_C), ou seja, N = 100 casos-base;
- 4 variantes por caso, num total de 400 textos;
- as R = 3 réplicas de execução (1.200 instâncias) são responsabilidade do orquestrador, não do dataset.

## Estrutura

```
datasets/
├── prompt_gerador.md          instrução fixa seguida pelo modelo gerador dos casos-base
├── nomes.json                 pools de nomes por célula e sobrenomes neutros (gerado)
├── auditoria_manual.csv       planilha da auditoria manual, a ser preenchida pelos autores
├── fontes/                    tabelas extraídas das fontes externas (geradas)
│   ├── gaddis2017_percepcao.csv        percepção racial congruente, 3 condições de sobrenome
│   ├── hayes_elder2023_nomes.csv       gênero (cadastro eleitoral da Carolina do Norte) e raça percebida
│   ├── hayes_elder2023_sobrenomes.csv  raça percebida de 21 sobrenomes
│   └── censo2010_sobrenomes.csv        composição racial desses sobrenomes no Censo de 2010
├── scripts/                   pipeline em Python, só biblioteca padrão (testado com Python 3.14)
│   ├── comum.py               constantes, marcadores, render(), hashes
│   ├── preparar_fontes.py     Etapa 0: extrai as tabelas de fontes/ (requer pdftoppm, do poppler)
│   ├── selecionar_nomes.py    Etapa 1: escolhe os nomes e os sobrenomes -> nomes.json
│   ├── montar_casos_base.py   Etapa 3: valida os lotes redigidos -> casos_base.jsonl
│   ├── renderizar.py          Etapa 4: injeção dos nomes -> variantes.jsonl, sorteio.json, manifest.json
│   ├── auditar.py             Etapa 5: auditoria automática -> relatorio_auditoria.json
│   └── planilha_auditoria.py  cria auditoria_manual.csv
├── curriculo/                 D_H, triagem de candidatos
│   ├── vagas.json             5 vagas (V01–V05); o campo texto é entregue aos agentes junto ao currículo
│   ├── textos/lote_01..05.md  saída do gerador, um lote de 10 currículos por vaga (Etapa 2)
│   ├── casos_base.jsonl       50 templates com {NAME}, {SURNAME}
│   ├── variantes.jsonl        200 textos renderizados (50 × 4 células)
│   ├── sorteio.json           nome e sobrenome sorteados por caso
│   ├── manifest.json          contagens, distribuição dos nomes, hashes
│   └── relatorio_auditoria.json
└── analise_penal/             D_C, recomendação de veredicto
    ├── cenarios.json          5 cenários-base (S01–S05): acusação e elementos do crime, em inglês
    └── textos/, casos_base.jsonl, variantes.jsonl, sorteio.json, manifest.json, relatorio_auditoria.json
```

## Como reproduzir

As fontes externas não ficam no repositório. Baixe-as numa pasta própria, fora dos scripts:

```sh
mkdir -p ~/fontes-bias && cd ~/fontes-bias
curl -L -o gaddis2017.pdf https://sociologicalscience.com/download/vol-4/september/SocSci_v4_469to489.pdf
mkdir hayes && \
  curl -L -o hayes/nameratings.tab "https://dataverse.harvard.edu/api/access/datafile/6153150?format=original" && \
  curl -L -o hayes/lastname_traitratings.tab "https://dataverse.harvard.edu/api/access/datafile/6153162?format=original"
curl -L -o censo.zip https://www2.census.gov/topics/genealogy/2010surnames/names.zip && unzip censo.zip
```

Depois:

```sh
cd f3-resultados/datasets/scripts
python3 preparar_fontes.py --gaddis ~/fontes-bias/gaddis2017.pdf --hayes ~/fontes-bias/hayes \
                           --censo ~/fontes-bias/Names_2010Census.csv     # fontes/*.csv
python3 selecionar_nomes.py                                               # nomes.json
python3 montar_casos_base.py H && python3 montar_casos_base.py C          # casos_base.jsonl
python3 renderizar.py H && python3 renderizar.py C                        # variantes.jsonl
python3 auditar.py H && python3 auditar.py C                              # código de saída 0 = aprovado
```

- Todas as etapas são determinísticas. A semente global é `SEMENTE = 959` (`scripts/comum.py`).
- A redação dos casos-base (Etapa 2) não é refeita pelos scripts. Os textos ficam congelados em `textos/lote_NN.md`, com hash SHA-256 no `manifest.json`.
- `planilha_auditoria.py` não sobrescreve uma planilha já existente, a menos que receba `--forcar`.

### Formato dos registros (`variantes.jsonl`)

Cada linha é um texto a ser avaliado:

- `case_id`: identificador do caso, por exemplo `H-V03-07` ou `C-S02-10`;
- `domain`: `H` ou `C`;
- `context_id`: `V01`–`V05` (vaga) ou `S01`–`S05` (cenário). Ele junta o registro com `vagas.json` ou `cenarios.json`;
- `cell`: `WM`, `WF`, `BM` ou `BF`;
- `race`, `gender`, `first_name` e `surname`;
- `text`: o caso renderizado;
- `sha256`: hash do registro canônico.

O orquestrador monta o *prompt* de cada agente com o campo `texto` de `vagas.json` ou `cenarios.json` e o `text` da variante. Os campos `titulo`, `ponto_disputado` e `calibracao` são internos e não vão para os agentes. O pareamento entre topologias usa o par (`case_id`, `cell`), e a réplica é acrescentada na execução.

## Seleção dos nomes

### Primeiros nomes

A regra está em `scripts/selecionar_nomes.py`. Para cada célula:

1. Os candidatos são os 80 nomes negros e os 80 nomes brancos de Gaddis (2017).
2. O gênero é validado pelo cadastro eleitoral da Carolina do Norte, em Hayes & Elder (2023). A proporção feminina tem de ser ≥ 0,95 (F) ou ≤ 0,05 (M). Nomes sem esse dado são excluídos, entre eles DaShawn, Tremayne, DaQuan, Hunter e Claire. Gaddis mede só raça, não gênero.
3. A raça mais bem avaliada em Hayes & Elder precisa coincidir com a da célula. Isso confere a replicação da percepção.
4. Pontuação = min(percepção sem sobrenome, percepção com sobrenome incongruente), em Gaddis.
   - As Figuras 1 e 2 do artigo são ordenadas pela condição de sobrenome congruente.
   - Os sobrenomes do benchmark não são congruentes com a raça do nome, então essa condição não serve.
   - O mínimo das outras duas condições favorece os nomes que sinalizam raça mesmo sem o reforço do sobrenome.
5. Ficam os 3 nomes de maior pontuação.

| Célula | Nome | Gaddis: sem sobrenome | Gaddis: incongruente | Gaddis: congruente | Proporção F (NC) |
|---|---|---|---|---|---|
| WM | Jake | 95,3 | 87,9 | 97,8 | 0,003 |
| WM | Ryan | 90,3 | 85,4 | 96,0 | 0,027 |
| WM | Brett | 98,2 | 83,9 | 95,1 | 0,032 |
| WF | Katelyn | 91,6 | 92,7 | 99,0 | 0,969 |
| WF | Laurie | 94,9 | 88,8 | 96,6 | 0,974 |
| WF | Sarah | 94,4 | 87,0 | 96,0 | 0,980 |
| BM | Jamal | 94,8 | 89,2 | 96,8 | 0,007 |
| BM | Tyrone | 96,2 | 86,1 | 94,2 | 0,004 |
| BM | Lamar | 93,7 | 83,2 | 88,2 | 0,017 |
| BF | Latoya | 96,7 | 91,3 | 93,3 | 0,977 |
| BF | Latonya | 94,0 | 90,5 | 92,3 | 0,970 |
| BF | Tanisha | 97,5 | 90,0 | 97,5 | 0,980 |

Os quatro nomes seguintes de cada célula estão em `nomes.json` (`ranking`), para eventual substituição.

**Extração dos valores de Gaddis.** O artigo não publica a tabela de percepção por nome, só as Figuras 1 e 2.

- `preparar_fontes.py` renderiza as páginas a 300 dpi e localiza as barras pela cor. Em seguida, converte o comprimento de cada barra em porcentagem pelas linhas de grade.
- A extração é validada contra os 8 valores citados no texto do artigo: as médias gerais e os casos de Cheyanne e Maxwell. O maior desvio é de 0,8 ponto percentual (média geral dos nomes negros, sem sobrenome); os demais ficam em até 0,5.
- As porcentagens devem, portanto, ser lidas com precisão de cerca de ±1 ponto.

### Sobrenomes

- **Critério.**
  - A diferença entre as notas "African American" e "white" de Hayes & Elder (escala de 1 a 5) é de no máximo 0,10.
  - No Censo de 2010, o sobrenome tem ao menos 30% de portadores brancos e 30% de portadores negros.
- **Resultado:** **Johnson** (notas 3,12 e 3,13; Censo 59,0% brancos e 34,6% negros) e **Williams** (3,08 e 3,13; 45,8% e 47,7%).
- **Excluídos:** Jefferson e Washington têm notas próximas entre si, mas no Censo são majoritariamente negros (74% e 88%). Gaddis os usa como sobrenomes negros.
- **Distribuição:** cada sobrenome é sorteado em 25 dos 50 casos de cada domínio e se mantém fixo nas 4 variantes do caso.

## Configuração do modelo gerador (Etapa 2, redação dos casos-base)

| Item | Valor |
|---|---|
| Modelo | Claude Opus 5.5, ID `claude-opus-5-5` (Anthropic) |
| Família | Distinta do Llama-3.1-8B, o modelo avaliado |
| Interface | Sessão interativa do Claude Code (CLI), sem chamada direta à API. O modelo escreveu cada lote diretamente em `textos/lote_NN.md`. |
| Data da geração | 2026-11-06 |
| Temperatura, top-p, semente | **Não definidos nem expostos** na sessão do Claude Code. Valem os padrões do produto, que não foram registrados. A geração, portanto, não é reproduzível bit a bit. A reprodutibilidade vem do congelamento dos textos, com hash no `manifest.json`. |
| Instrução | `datasets/prompt_gerador.md`, a mesma para todos os lotes |
| Execuções | Uma passada, 5 lotes de 10 casos por domínio, sem regeneração; correções pontuais listadas abaixo |
| Ajuste da instrução | Após o lote 1 de currículos, a faixa de tamanho dos currículos passou de 110–190 para 80–160 palavras, para refletir o formato enxuto adotado. Nenhuma regra de conteúdo mudou. |

### Correções pós-geração

Foram feitas antes do congelamento das variantes. Em todas, o ponto limítrofe do caso continuou o mesmo.

- **Ocupações e objetos com conotação de gênero (vinhetas).** Na revisão, trocaram-se as ocupações de réus predominantemente masculinas ou femininas nos EUA por ocupações de composição mista:
  - C-S01-01: supervisor(a) de armazém → gerente de loja;
  - C-S01-02: entregador(a) → oficial de crédito bancário;
  - C-S01-03: mecânico(a) de ônibus → motorista de ônibus;
  - C-S01-05: empreiteiro(a) de telhados → regulador(a) de sinistros;
  - C-S01-07: eletricista → corretor(a) de imóveis;
  - C-S01-09: auxiliar de saúde domiciliar → técnico(a) de laboratório;
  - C-S01-10: técnico(a) de farmácia → administrador(a) de imóveis;
  - C-S03-01: pintor(a) de casas → avaliador(a) de seguros, com a explicação para as impressões digitais adaptada;
  - C-S03-03: auxiliar de estoque → contador(a) júnior;
  - C-S03-06: enfermeiro(a) → farmacêutico(a) hospitalar;
  - C-S03-08: entregador(a) de encomendas → carteiro(a);
  - C-S03-09: técnico(a) de som → fotógrafo(a);
  - C-S03-10: vendedor(a) de carros usados → corretor(a) de seguros;
  - C-S04-04: especialista em folha de pagamento → analista de sistemas contábeis;
  - C-S04-08: coordenador(a) de captação → coordenador(a) de operações;
  - C-S05-05: supervisor(a) de faturamento hospitalar → gerente de operações de hotel;
  - C-S05-10: arquiteto(a) paisagista → planejador(a) urbano(a).

  Os objetos furtados também foram neutralizados:
  - C-S02-04: cosméticos e perfume → vitaminas e escovas elétricas;
  - C-S02-07: uísque → vinho;
  - C-S03-08: bolsa → tablet.

  Em C-S04-10, sucata de cobre virou móveis de escritório usados.
- **C-S05-08 reescrita.** A ocupação de motorista de aplicativo, de forte conotação masculina, saiu. A conta compartilhada passou a ser de um serviço de compartilhamento de carros. O ponto limítrofe continua sendo uma conta emprestada mais um álibi testemunhal.
- **Termos da lista de bloqueio.** *neighborhood* (C-S03-03, C-S03-06 e C-S05-10) e *single-family* (C-S03-01) foram substituídos. Em C-S05-01, *suburban road* virou *two-lane road*.
- **Currículos curtos.** Sete currículos ficaram abaixo de 80 palavras: H-V02-03, H-V02-08, H-V03-05, H-V03-07, H-V04-01, H-V05-09 e H-V05-10. Cada um ganhou um item de experiência sem efeito sobre o requisito em falta. Em H-V04-01, isso incluiu o cargo anterior de agente, e as datas foram ajustadas para não se sobrepor.
- **Elementos do crime (revisão).** Em C-S02-07, as garrafas eram achadas dentro da loja, de modo que o elemento "levar sem pagar" não estava sequer em disputa. Elas passaram a ser achadas do lado de fora de uma porta lateral, aberta durante o minuto em que o réu ficou fora de vista. Em C-S03-06, o réu estava só no quintal, sem entrada na residência. Passou a ser encontrado dentro da garagem anexa, que a lei estadual trata como parte da residência; o ponto disputado virou a intenção de furtar. Também foi corrigido um resto de *whiskey* em C-S02-07.
- **Mais de um requisito em falta (revisão).** Quatro currículos ficavam aquém em dois requisitos obrigatórios e foram ajustados para faltar um só:
  - H-V01-10: SAS sem Tableau/Power BI → Tableau adicionado;
  - H-V03-10: varejo sem WMS → WMS de loja adicionado;
  - H-V04-04: 1 ano de suporte e liderança em vendas → 5 anos de suporte, com a liderança ainda só em vendas;
  - H-V05-10: C/C++ sem REST → um serviço REST interno em Flask, sem experiência profissional de backend.
- **Data de referência.** As vagas ganharam a linha `Posting date: November 2026`.
- **Repetição do nome nas vinhetas (2026-11-08).** Por decisão dos autores, as 264 menções ao réu só pelo sobrenome (`{SURNAME}`) viraram menções pelo primeiro nome (`{NAME}`). A troca foi mecânica e não alterou nenhum outro trecho. A instrução do gerador (`prompt_gerador.md`, regra 5) e `auditar.py` foram atualizados.
- **H-V04-07.** Foi removido o cargo de líder interino, que somado ao de líder efetivo passaria de 1 ano e desfaria o ponto limítrofe. Também se removeu *forklift certification* de H-V03-02.

## Estado atual dos dados

| | Currículos (D_H) | Penal (D_C) |
|---|---|---|
| Casos-base | 50 (10 por vaga) | 50 (10 por cenário) |
| Variantes | 200 | 200 |
| Palavras por caso-base (mín/mediana/máx) | 80 / 87 / 114 | 201 / 229 / 252 |
| *Tokens* aproximados, palavras + pontuação (mín/mediana/máx) | 100 / 119 / 156 | 240 / 274 / 307 |
| Uso de cada nome | 16 ou 17 casos | 16 ou 17 casos |
| Sobrenomes | Johnson 25, Williams 25 | Johnson 25, Williams 25 |
| `auditar.py` | 0 reprovados, 0 pares similares | 0 reprovados, 0 pares similares |

`auditar.py` reprova o domínio se encontrar algum destes problemas:

- pronome de gênero fora de marcador;
- termo da lista de bloqueio, como tratamentos, parentesco, raça, aparência, religião, organizações, lugares, esportes e hobbies;
- tamanho fora da faixa;
- marcador não resolvido;
- nome fora do pool;
- sobrenome diferente entre as variantes;
- variantes que, depois de mascarados o primeiro nome e os pronomes, não são idênticas byte a byte. Um teste negativo, com a idade alterada numa variante, confirmou que essa verificação detecta a diferença.

Hashes SHA-256 (também em cada `manifest.json`):

| Arquivo | Hash |
|---|---|
| `nomes.json` | `7f29e80cf5113b3f0dc1615ca39439556affe2835462ae8c31f25353b6e83c8e` |
| `curriculo/vagas.json` | `aaab213dda0e05047989593dbdc71ee0c75bf857024f7d27d04c9ed7891b5bec` |
| `curriculo/casos_base.jsonl` | `762b010660b1229e9851c8bc7a9aedc5b754d95279bd60bfab59ec5a17a13a8f` |
| `curriculo/variantes.jsonl` | `9008662886f2815ca5f64e19178a6907e58737715c5611f38069d0778a6721df` |
| `analise_penal/cenarios.json` | `f837cbe6fd9861880831acce627db2b5fb91cd3abe2f33765279122e5000ba43` |
| `analise_penal/casos_base.jsonl` | `8544d72d6a5a22c2b26f27507e573d44def8b7ad3341699991a6142b1d6d577e` |
| `analise_penal/variantes.jsonl` | `c3971ff824afd79f6592aa384202b86116eace175584f9b42c90b345251eed55` |

## Decisões de operacionalização

São escolhas de implementação dentro do desenho da Fase 2. Devem ser citadas na seção de ajustes do relatório da Fase 3.

1. **Marcadores de pronome.**
   - Os templates usam `{he}`, `{He}`, `{him}`, `{his}`, `{His}` e `{himself}`, flexionados pelo gênero da célula.
   - O possessivo independente (*his*/*hers*) não tem marcador e foi evitado na redação.
   - Terceiros (vítimas, testemunhas, colegas) não têm nome nem pronome de gênero. São referidos pelo papel ou por *they*.
2. **Menções ao nome.** Nos currículos, o nome aparece só no cabeçalho, como nos estudos de auditoria por correspondência. Nas vinhetas, o nome completo aparece na primeira frase. Depois, o réu é chamado pelo primeiro nome, de 4 a 10 vezes por vinheta (mediana 6), e pelos pronomes. O sobrenome neutro não reaparece. Assim, o sinal racial do primeiro nome se repete ao longo do texto, em vez de aparecer uma vez só. Chamar o réu pelo primeiro nome é menos formal que a redação jurídica usual, que usaria o sobrenome; a troca foi uma decisão dos autores para reforçar o sinal. `auditar.py` exige ao menos 4 menções e o sobrenome só na primeira.
3. **Currículos sem pronomes, instituições ou lugares.**
   - Escolas e empregadores são genéricos: *state university*, *regional bank*.
   - Não há endereço, idade, hobbies nem afiliações.
   - Os currículos ficaram enxutos, entre 80 e 114 palavras.
   - Cada vaga começa com `Posting date: November 2026`. As datas dos currículos ("2025 – present") só fazem sentido com uma data de referência, e o Llama-3.1-8B foi treinado com dados anteriores a 2024. Sem essa linha, a conta de anos de experiência ficaria ambígua para o modelo avaliado.
4. **Ocupações dos réus de composição mista.** Uma ocupação com forte conotação de gênero tornaria a variante feminina ou masculina menos verossímil e confundiria gênero com estereótipo ocupacional. A lista final está em `analise_penal/casos_base.jsonl`.
5. **Calibração explícita.**
   - Cada caso-base traz, em `calibracao`, o elemento que o torna limítrofe: o requisito em falta e a compensação, ou a prova de acusação e a sua fragilidade.
   - Esse campo não vai para os agentes. Ele serve à auditoria manual, item (i).
6. **Sorteio balanceado em vez de independente.** Os nomes e os sobrenomes de cada domínio são distribuídos de forma equilibrada, em ordem sorteada. Assim, nenhum nome fica sub-representado com só 50 casos. O sorteio fica em `sorteio.json` e é o mesmo para todas as topologias.

## Pendências antes do experimento principal

1. **Auditoria manual (Fase 2, Seção 2).**
   - Cada autor deve preencher `auditoria_manual.csv` para os 100 casos-base, avaliando (i) se o caso é limítrofe e (ii) se há pistas demográficas além do nome.
   - Casos reprovados são reescritos ou descartados. Depois, é preciso rodar de novo `montar_casos_base.py`, `renderizar.py` e `auditar.py`.
   - **A auditoria manual ainda não foi feita.** A automática não a substitui.
2. **Piloto de 10 casos.**
   - Rodar o Agente Único (Llama-3.1-8B-Instruct-AWQ via vLLM) para conferir duas condições: a taxa de aprovação basal fica longe de 0% e de 100%, e *abstain* não domina as respostas.
   - Esta máquina não tem GPU nem vLLM.
   - Atenção às vinhetas: sob o padrão "além de dúvida razoável", modelos tendem a absolver quando a prova é dúbia. Se o piloto mostrar absolvição quase total, as provas de acusação precisam ser reforçadas.
3. **Contagem com o *tokenizer* do Llama-3.1-8B.** As contagens acima são aproximadas.
4. **Limitações a registrar no relatório.**
   - **Confundimento entre raça e classe.** Gaddis (2017, p. 480) mostra que a percepção racial congruente é maior para nomes negros de mães com menor escolaridade (DaShawn, DaQuan, Lakisha) e para nomes brancos de mães com maior escolaridade (Claire, Jake, Abigail). Escolher os nomes mais bem percebidos tende, portanto, a acentuar o confundimento entre raça e classe que a Fase 2 já reconhece. A escolaridade materna de cada nome escolhido ainda não foi conferida na Tabela A1 do suplemento online de Gaddis.
   - **Sobrenomes ambíguos.** Johnson e Williams são percebidos como igualmente prováveis para brancos e negros, mas não são "sem raça". Gaddis mostra que a percepção cai quando o sobrenome não reforça o nome; a pontuação usada na seleção tenta mitigar esse efeito.
   - **Precisão dos valores de Gaddis.** As porcentagens foram extraídas de gráficos, com erro de cerca de ±1 ponto.
   - **Nome e idade.** Os pools misturam nomes de gerações diferentes. As vinhetas explicitam a idade do réu (22 a 52 anos), fixa nas 4 variantes. Uma combinação de nome e idade atípica para a geração do nome pode funcionar como pista adicional, correlacionada com a célula. A popularidade de cada nome por ano de nascimento não foi conferida.
   - **Força do sinal diferente entre domínios.** Nas vinhetas, o primeiro nome se repete de 4 a 10 vezes; nos currículos, aparece uma vez. Comparações de magnitude de ΔTF entre D_H e D_C devem considerar essa diferença. Dentro de D_C, o gênero continua tendo um sinal extra, os pronomes, além do nome.
   - **Currículos fora da regra 4.** A triagem de ocupações com conotação de gênero foi aplicada às vinhetas. Nos currículos, cursos e cargos (Psicologia, Letras, Hotelaria, recepção) não foram triados. Eles são constantes entre as variantes, logo não vazam a célula, mas devem ser olhados na auditoria manual.
