# Model Card — VibePlay Hybrid Recommender v1.0

## Uso pretendido

Ordenar títulos para uma faixa de descoberta em um produto fictício de streaming. O artefato é educacional e usa dados sintéticos.

## Fora de escopo

- Decidir acesso a crédito, emprego, saúde ou qualquer direito.
- Inferir atributos sensíveis.
- Substituir moderação, classificação indicativa ou regras territoriais.
- Declarar efeito causal sobre retenção ou receita.

## Componentes

- Truncated SVD sobre feedback implícito.
- TF-IDF de gênero e tipo.
- Popularidade e frescor.
- Re-ranking MMR.
- Explicação baseada em sinais observáveis.

## Avaliação

Split temporal por usuário, amostra de 160 usuários elegíveis e comparação com popularidade. Métricas são regeneradas em `artifacts/metrics.json`; não devem ser copiadas manualmente para relatórios.

## Riscos

| Risco | Consequência | Controle proposto |
|---|---|---|
| Popularity bias | catálogo concentrado | coverage, novelty e caps |
| Filter bubble | pouca exploração | MMR e exploração controlada |
| Cold start | baixa personalização | onboarding + fallback |
| Feedback loop | reforço do próprio ranking | logs de exposição e propensity |
| Segmento subatendido | experiência desigual | métricas por região/segmento |
| Drift | perda silenciosa | monitoramento e rollback |

## Limitações

Dados sintéticos simplificam sequência, contexto, múltiplos perfis por residência, disponibilidade territorial e efeito da interface. Métricas offline não incorporam causalidade nem impacto de longo prazo.

## Critério de promoção

1. Contrato de dados válido.
2. Ganho contra baseline em Recall@10 e NDCG@10.
3. Cobertura e diversidade acima dos limites.
4. Shadow test sem degradação de latência.
5. A/B test com efeito positivo e guardrails preservados.

