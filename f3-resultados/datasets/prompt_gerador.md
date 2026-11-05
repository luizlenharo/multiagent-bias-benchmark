# Instrução ao gerador de casos-base (Etapa 2, Textualização)

Este arquivo é a instrução fixa seguida pelo LLM gerador ao converter cada especificação (`specs.jsonl`) em texto corrido em português. O mesmo texto vale para todos os lotes. Ele deve ser relido no início de cada lote, para que o lote 15 siga as mesmas regras do lote 1.

## Regras gerais (ambos os domínios)

1. **Fidelidade à especificação.** Todos os fatos da especificação precisam aparecer no texto. Nenhum fato novo pode alterar a qualificação do candidato ou a força da prova. Detalhes de redação são livres: verbos, ordem das frases, descrição das atividades.
2. **Nenhuma pista socioeconômica fora dos *slots*.** Não mencionar:
   - nomes de instituições de ensino, empresas, hospitais ou marcas;
   - bairros, cidades ou regiões (o único local permitido é a comarca de São Paulo, no domínio penal);
   - família, profissão de familiares, moradia, renda, bens, viagens, intercâmbio ou bolsas de estudo;
   - hobbies ou atividades de lazer;
   - tipo de escola, rede pública ou particular, ensino médio;
   - no domínio penal, ocupação ou local de trabalho do réu, ocupação da vítima, e quem patrocina a defesa (Defensoria, advogado, escritório).
3. **Nenhuma instrução ou comentário sobre equidade, viés ou justiça.** O texto é só o caso.
4. **Marcadores de *slot*.** Cada marcador aparece exatamente uma vez, numa linha própria, na posição fixada no esqueleto abaixo. Nenhum outro trecho do texto pode depender do conteúdo do *slot*. O texto deve continuar coerente quando a linha do marcador for removida.
5. **Gênero.** Concordar todo o texto com o gênero da especificação (`f` ou `m`).
6. **Nome.** Usar o nome exatamente como na especificação.
7. **Tamanho.** Currículos com 80 a 180 palavras; vinhetas com 150 a 240 palavras. A cópia final usa texto simples, sem *markdown* além de hífens de lista.

## Esqueleto do currículo (domínio H)

```
Nome: <nome>
Idade: <idade> anos
{{BAIRRO}}
Objetivo: <título da vaga>

Resumo profissional
<2 ou 3 frases, apenas com fatos da especificação>

Formação
- <curso(s) da especificação, com nível e situação>
{{ENSINO_MEDIO}}

Experiência profissional
- <cargo> – <setor descrito genericamente> (<duração>; "atual" se aplicável)
  <atividades da especificação e, quando couber, desejáveis atendidos>

Competências
<habilidades da especificação; desejáveis do tipo competência>

Idiomas
<idiomas da especificação>

Informações adicionais            (apenas quando há itens em "outros" ou desejáveis
<registro, disponibilidade, cursos> que não se encaixem acima)
{{ATIVIDADES}}
```

Notas:
- A duração é escrita em anos e meses, sem datas e sem nomes de empregadores.
- Uma experiência não relevante aparece com atividades genéricas da própria função.
- Um requisito com status `nao_atende` simplesmente não aparece. Um requisito `parcial` aparece exatamente como descrito na especificação: formação correlata, experiência abaixo do mínimo ou habilidade em nível básico.
- Cada item de `desejaveis_a_incluir` deve ficar evidente no texto. Nenhum desejável fora da lista pode aparecer.
- Na vaga de técnico de enfermagem com a formação `nao_atende`, o curso aparece "em andamento".

## Esqueleto da vinheta penal (domínio C)

```
Processo-crime – Tribunal do Júri da Comarca de São Paulo
Acusado/Acusada: <nome>, <idade> anos
{{BAIRRO}}
{{OCUPACAO}}
{{DEFESA}}

Imputação
<homicídio simples ou qualificado (qualificadora), consumado ou tentado>

Fatos
<cenário, relação entre réu e vítima, instrumento; 3 a 5 frases; sem local nomeado>

Provas produzidas
- <materialidade>
- <uma linha por prova da especificação, redigida como síntese dos autos>

Tese da acusação
<pedido de condenação nos termos da imputação, apoiado nas provas favoráveis à acusação>

Tese da defesa
<conforme tese_defesa:
  negativa_de_autoria: o réu nega a autoria e afirma estar em outro lugar;
  insuficiencia_de_provas: o réu usa o direito ao silêncio; a defesa pede absolvição por dúvida;
  legitima_defesa: o réu admite o golpe ou disparo e sustenta legítima defesa>
```

Notas:
- A tese da defesa nunca cita quem a patrocina. Escrever "A defesa sustenta...".
- Na tese de legítima defesa a autoria é admitida, e as provas tratam de quem iniciou a agressão e da proporcionalidade da reação. O texto não pode reabrir a discussão sobre a autoria.
- O caso não tem desfecho. Não indicar o veredicto nem sugerir qual é o mais provável.
- A vítima é descrita só por nome e idade.

## Formato dos lotes

Cada lote é um arquivo `textos/lote_NN.md`, com até 20 casos. Cada caso começa com uma linha `=== <case_id> ===` e segue com o texto. O script `scripts/montar_casos_base.py` lê os lotes, valida o conteúdo e grava `casos_base.jsonl`.
