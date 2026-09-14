# Roteiro de apresentação — 8 a 10 minutos

## 1. Abertura — 40 segundos

“Eu construí este case para responder uma pergunta de produto, não apenas uma pergunta de algoritmo: como aumentar descoberta relevante sem recomendar sempre os mesmos títulos? Usei dados sintéticos para tornar o projeto público e reproduzível.”

## 2. Problema e hipótese — 50 segundos

“Popularidade é um baseline forte, mas oferece pouca personalização e concentra catálogo. Minha hipótese é que um motor híbrido, com diversidade e explicação, melhora consumo relevante. Ainda é hipótese até o teste A/B.”

## 3. Dados — 50 segundos

Mostre as três tabelas e explique feedback implícito. Destaque que skip não vale o mesmo que play e que o split é temporal para evitar vazamento.

## 4. Solução — 2 minutos

“O candidato colaborativo encontra padrões entre pessoas; conteúdo captura afinidade explícita; popularidade e frescor protegem descoberta e cold start. Depois, MMR reduz repetição. Os pesos são ponto de partida, não verdade absoluta.”

## 5. Resultado offline — 1 minuto

Abra o benchmark no dashboard. Compare híbrido e popularidade. Explique Recall, NDCG, cobertura e diversidade em linguagem de produto. Não chame diferença offline de receita ou retenção.

## 6. Produto — 1 minuto

Mostre cards, filtros e explicações. Abra a Vivi e pergunte: “Como validar no negócio?”. Explique que o chat lê artefatos controlados e não inventa SQL nem números.

## 7. Automação e governança — 1 minuto

“Toda segunda o pipeline pode retreinar, executar testes e bloquear publicação se guardrails falharem. Em produção eu adicionaria shadow deployment, champion–challenger e rollback.”

## 8. Experimento — 1 minuto

Controle: popularidade. Tratamento: híbrido. Primária: horas assistidas. Secundárias: CTR, conclusão, diversidade e D30. Guardrails: skips, latência e concentração.

## 9. Fechamento — 30 segundos

“O valor do case não está apenas em recomendar. Está em transformar dados em uma decisão mensurável, com custo controlado, explicação e rota segura para produção.”

## Perguntas difíceis e respostas honestas

**Por que SVD e não deep learning?**

“Para este porte, SVD entrega um baseline forte, barato e explicável. Eu só aumentaria complexidade se um challenger mostrasse ganho incremental relevante em avaliação temporal e teste online.”

**Os pesos foram otimizados?**

“Não. São uma configuração informada por produto. Em seguida eu faria busca controlada, respeitando múltiplas métricas, e validaria o candidato online.”

**Você pode afirmar aumento de retenção?**

“Não. Posso afirmar desempenho offline contra o baseline nesta base. Retenção exige experimento com randomização, amostra e janela adequadas.”

**Como evitar bolha?**

“Re-ranking de diversidade, limites de repetição, exploração controlada, cobertura por segmento e feedback negativo. Também monitoraria concentração de exposição.”

**Como lidar com fraude ou eventos artificiais?**

“Validação de eventos, deduplicação, limites por sessão, detecção de anomalias e redução de peso para sinais suspeitos.”

**Qual limitação mais importante?**

“Os dados são sintéticos e não reproduzem todas as dinâmicas de catálogo, contexto e causalidade. O objetivo é provar arquitetura e raciocínio, não estimar impacto real.”

