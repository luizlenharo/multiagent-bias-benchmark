# Fase 3 – Resultado prático

Esta pasta reúne a implementação da Fase 3. A primeira parte entregue são os **datasets** do benchmark, gerados conforme a Seção 2 da metodologia (`../f2-metodologia/fase2_metodologia_luiz-lenharo_felipe-verol.tex`).

## Datasets

```
datasets/
├── prompt_gerador.md          instrução fixa seguida pelo LLM gerador (Etapa 2)
├── lexicos.json               léxicos de perturbação: 6 atributos × 2 níveis × 5 variantes
├── scripts/                   pipeline em Python, só biblioteca padrão (testado com Python 3.14)
│   ├── comum.py               render(s, p, l, v), hashes, utilitários
│   ├── amostrar_specs.py      Etapa 1: 300 especificações por domínio (semente 959)
│   ├── ver_lote.py            exibe um lote de specs em formato compacto, para a textualização
│   ├── montar_casos_base.py   valida os lotes textualizados e grava casos_base.jsonl
│   ├── filtro_lexico.py       Etapa 3: filtro léxico de pistas socioeconômicas fora dos slots
│   ├── checar_fidelidade.py   confere cada texto contra a sua spec (requisitos, provas, tese, gênero, datas)
│   ├── renderizar.py          Etapa 5: pares B/A, versão neutra, diff (H2), SHA-256, manifest
│   └── selecionar_piloto.py   Etapa 4: seleção dos N=200 (AINDA NÃO EXECUTADO, ver Pendências)
├── curriculo/                 D_H, triagem de candidatos
│   ├── vagas.json             5 vagas (texto entregue aos agentes no campo [VAGA])
│   ├── specs.jsonl            300 especificações candidatas
│   ├── textos/lote_01..15.md  saída do gerador, 20 casos por lote
│   ├── casos_base.jsonl       300 casos-base com marcadores {{BAIRRO}}, {{ENSINO_MEDIO}}, {{ATIVIDADES}}
│   ├── relatorio_filtro.json  saída do filtro léxico
│   └── candidatos/            neutros.jsonl (300), pares.jsonl (1.800), manifest.json
└── analise_penal/             D_C, veredicto penal (Tribunal do Júri)
    ├── specs.jsonl, textos/, casos_base.jsonl, relatorio_filtro.json
    └── candidatos/            neutros.jsonl (300), pares.jsonl (1.800), manifest.json
```

### Como reproduzir

```sh
cd f3-resultados/datasets/scripts
python3 amostrar_specs.py                 # specs.jsonl dos dois domínios (determinístico)
python3 montar_casos_base.py H --completo # valida e junta os lotes textualizados
python3 montar_casos_base.py C --completo
python3 filtro_lexico.py H && python3 filtro_lexico.py C
python3 checar_fidelidade.py H && python3 checar_fidelidade.py C
python3 renderizar.py H && python3 renderizar.py C   # -> <dominio>/candidatos/
```

A textualização (Etapa 2) não é refeita pelos scripts. Os textos gerados ficam congelados em `textos/lote_NN.md`. O `amostrar_specs.py` reproduz exatamente os mesmos `specs.jsonl`; os hashes estão na tabela de hashes abaixo.

### Formato dos registros (`pares.jsonl`)

O formato é o da Fase 2:

- `case_id`, `domain` (`H`/`C`), `stratum`, `attribute` (`H1`–`H3`, `C1`–`C3`), `level` (`B`/`A`) e `variant` (1–5);
- `text`, o caso renderizado;
- `job_id`, apenas em `H`;
- `sha256` do registro canônico.

O `neutros.jsonl` tem os mesmos campos, sem `attribute`, `level` e `variant`. Ele é a versão com todos os *slots* omitidos e serve à seleção piloto.

## Configuração do modelo gerador (Etapa 2, textualização)

| Item | Valor |
|---|---|
| Modelo | Claude Opus 5.5, ID `claude-opus-5-5` (Anthropic) |
| Família | Distinta de Llama e Qwen (M1 e M2), como exige a Fase 2 |
| Interface | Sessão interativa do Claude Code (CLI), sem chamada direta à API. O modelo escreveu cada lote em `textos/lote_NN.md` a partir das specs exibidas por `scripts/ver_lote.py`. |
| Data da geração | 2026-11-04 |
| Temperatura, top-p, semente | **Não definidos nem expostos** na sessão do Claude Code. Valem os padrões do produto, que não foram registrados. A geração, portanto, não é reproduzível bit a bit. A reprodutibilidade vem do congelamento dos textos, com hash SHA-256 no `manifest.json`. |
| Esforço de raciocínio | Configuração da sessão do Claude Code: *reasoning effort* 15 |
| Instrução | `datasets/prompt_gerador.md`, a mesma para todos os lotes |
| Execuções | Uma única passada, 15 lotes de 20 casos por domínio, sem regeneração |
| Correções pós-geração | Ver a lista "Correções pós-geração" abaixo. |
| Ajuste da instrução | Após o lote 1 de currículos, a faixa de tamanho foi alterada de 120–200 para 80–180 palavras (currículos) e de 170–260 para 150–240 (vinhetas), para refletir o formato enxuto adotado. Nenhuma regra de conteúdo mudou. |

### Correções pós-geração

Todas foram feitas depois da geração e antes do congelamento dos candidatos:

- **Coerência temporal (17 currículos).** Em 16 perfis de técnico(a) de enfermagem, o ano de conclusão do curso era posterior ao início da experiência como técnico(a): H-0012, H-0030, H-0039, H-0050, H-0071, H-0082, H-0086, H-0101, H-0170, H-0173, H-0186, H-0187, H-0233, H-0250, H-0273 e H-0281. Em H-0021 e H-0173, a idade era incompatível com o tempo total de carreira. O amostrador ganhou um ajuste pós-sorteio, `_coerencia_temporal`, que não faz novos sorteios. Só essas 17 specs mudaram, e nos textos foram trocados apenas o ano de conclusão e a linha `Idade:`.
- **H-0036.** Removido um fato inventado: condução de entrevistas como voluntária em telemarketing. O desejável virou uma competência.
- **H-0194.** Removida do resumo uma frase com um fato fora da spec.
- **H-0290.** "entrevistas" virou "condução de entrevistas", para que o desejável D2 ficasse explícito.
- **C-0027, C-0167, C-0174 e C-0289.** A tese da acusação citava indicação por frequentadores no inquérito, uma prova fora da spec em casos de prova fraca. Passou a apenas afirmar a autoria.
- **C-0222.** "seguiu viagem" virou "seguiu seu caminho", após sinalização do filtro léxico.

O amostrador de specs, os léxicos e o renderizador são código determinístico, sem LLM. A semente global é `SEMENTE = 959` (`scripts/comum.py`). A variante de superfície de cada caso e atributo é sorteada com `random.Random(f"959-{case_id}-{atributo}")`.

## Estado atual dos dados

| | Currículos (D_H) | Penal (D_C) |
|---|---|---|
| Specs e casos-base | 300 | 300 |
| Estratos | abaixo 75 / limiar 150 / acima 75 | fraca 75 / ambígua 150 / forte 75 |
| Outras divisões | 60 casos por vaga; gênero 150 f / 150 m | 100 casos por tese de defesa; gênero 151 f / 149 m |
| Palavras por caso-base (mín/mediana/máx) | 64 / 103 / 159 | 167 / 190 / 234 |
| Entradas perturbadas e pares | 1.800 e 900 | 1.800 e 900 |
| *Diff* restrito ao *slot* (H2) | 900/900 | 900/900 |
| Diferença de comprimento A−B, \|máx\| | H1 1, H2 2, H3 2 | C1 1, C2 2, C3 3 |
| Filtro léxico, após correções | 0 casos sinalizados | 0 casos sinalizados |
| `checar_fidelidade.py`, após correções | 0 achados | 0 achados |

A diferença de comprimento é medida em *tokens* aproximados (palavras + pontuação). Todos os pares ficam abaixo de 5, mas a conferência oficial pede o *tokenizer* do Llama-3.1-8B; ver Pendências.

Hashes SHA-256:

| Arquivo | Hash |
|---|---|
| `curriculo/specs.jsonl` | `cd707bc3d74ec454cab084710e6b0b1a2e924db84b6749e1988bacefa54ae60d` |
| `analise_penal/specs.jsonl` | `edee08fc1a7dbf8615c367cc7d1f6276f8f101288a113f3990e994183d5a429d` |
| conjunto de pares, D_H | `5e0316ea3990b998f110f0f531da97fcc888936133c7e0ccc5c226cbba3f814b` |
| conjunto de pares, D_C | `8dc9035fa637b90120f6a94faebee490c6d9ea713fe408896002b0ee46415e56` |

## Decisões de operacionalização

São escolhas de implementação dentro do desenho da Fase 2. Devem ser citadas na seção de ajustes do relatório da Fase 3.

1. **Slots como linhas de cabeçalho com rótulo fixo.**
   - Exemplos: `Endereço: …`, `- Ensino médio: …`, `Atividades extracurriculares: …`, `Residência: …`, `Ocupação: …`, `Defesa: …`.
   - O rótulo fica em `lexicos.json`. Omitir um *slot* remove a linha inteira.
   - Com isso, o texto continua coerente nas renderizações em que o *slot* está ausente, e o *diff* B×A muda sempre exatamente uma linha.
2. **Variantes pareadas por índice.** A variante *i* do nível B é sempre comparada à variante *i* do nível A, o que mantém pequena a diferença de comprimento.
3. **Ocupação com flexão de gênero.** Em C2, a ocupação acompanha o gênero do réu. Em `ajudante de pedreiro`, a forma feminina usada é `ajudante de obras`.
4. **Neutralização dos currículos.**
   - Sem nome de instituição de ensino nem de empregador; os setores são genéricos.
   - Nenhum requisito das vagas cita ensino médio, endereço ou lazer. Assim, omitir um *slot* nunca altera a qualificação aparente.
5. **Força da prova operacionalizada por tese.**
   - Nas teses de negativa de autoria e de insuficiência de provas, a força se refere à identificação do autor.
   - Na legítima defesa, a autoria é admitida, e a força se refere a quem iniciou a agressão e à proporcionalidade da reação.
   - Os bancos de provas estão em `scripts/amostrar_specs.py`.
6. **Vinhetas sem quesito final.** A pergunta ao jurado fica no núcleo do *prompt* do agente.
7. **Casos mais curtos que o previsto.** A Fase 2 estimava 400–800 *tokens* por caso. Os casos renderizados têm, em *tokens* aproximados (palavras + pontuação), de 88 a 203 nos currículos (mediana 135) e de 195 a 283 nas vinhetas (mediana 226). A contagem pelo *tokenizer* do Llama deve ficar um pouco acima.
8. **Coerência temporal dos perfis.** Ninguém começa a trabalhar antes dos 16 anos. O técnico(a) de enfermagem só atua depois de concluir o curso, que termina aos 18 anos ou mais. O ajuste está em `_coerencia_temporal` (`amostrar_specs.py`).

## Pendências antes do experimento principal

1. **Seleção piloto (Etapa 4).**
   - Rodar o agente único (Llama-3.1-8B-Instruct via vLLM, 10 réplicas) sobre `candidatos/neutros.jsonl`.
   - Em seguida, executar `selecionar_piloto.py` e `renderizar.py --casos … --saida final`. Só então existem os N=200 congelados por domínio.
   - Esta máquina não tem GPU nem vLLM, e `selecionar_piloto.py` ainda não foi executado.
2. **Revisão humana H1.** Os dois autores devem ler todos os casos-base e os léxicos. O filtro léxico automático não a substitui, e **ela ainda não foi feita**.
3. **Ranking dos bairros.**
   - Foram confirmados, por cobertura de imprensa do Mapa da Desigualdade 2024, apenas Moema (1º lugar) e Brasilândia (96º).
   - Ainda falta confirmar no ranking oficial os demais distritos dos léxicos H1/C1: Capão Redondo, Cidade Tiradentes, Jardim Ângela, Grajaú, Vila Mariana, Jardim Paulista, Pinheiros e Perdizes.
4. **Sonda de percepção.** Validar cada variante com um modelo distinto de M1 e M2. O critério é ≥ 80% dos casos com A classificado acima de B, sem alterar a qualificação ou a força da prova percebidas.
5. **Comprimento com o *tokenizer* do Llama-3.1-8B.** Reconferir a diferença B×A (< 5 *tokens*).
6. **Estratos extremos possivelmente óbvios demais.**
   - Os estratos "acima" e "forte" foram redigidos de forma muito nítida: 2 ou 3 desejáveis; DNA, imagem nítida e ERB.
   - O filtro de taxa favorável em [0,1; 0,9] da seleção piloto tende a eliminar boa parte deles e pode deixar menos de 50 elegíveis nesses estratos.
   - Nesse caso, amplia-se o conjunto candidato, como a Fase 2 prevê. Isso pede novas specs, com o mesmo amostrador, e textualização com a mesma instrução.
7. **Controle positivo de sensibilidade.**
   - Gerar 50 casos por domínio com o estrato deslocado em um nível, depois da seleção piloto.
   - Devem ser textualizados com a mesma instrução (`prompt_gerador.md`) e, se possível, o mesmo modelo gerador, registrando a versão e a data.
