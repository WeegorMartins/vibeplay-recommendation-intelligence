# Dicionário de dados

## users.csv

| Campo | Tipo | Regra |
|---|---|---|
| user_id | string | Identificador sintético único. |
| region | categoria | Região brasileira. |
| age_group | categoria | Faixa etária, sem data de nascimento. |
| plan | categoria | Basic, Standard ou Premium. |
| main_device | categoria | Dispositivo mais usado. |
| favorite_genres | string | Três gêneros separados por `|`. |
| tenure_months | inteiro | Tempo de relacionamento. |

## catalog.csv

| Campo | Tipo | Regra |
|---|---|---|
| item_id | string | Identificador sintético do título. |
| title | string | Nome fictício. |
| type | categoria | Filme ou Série. |
| genres | string | Um a três gêneros separados por `|`. |
| release_year | inteiro | Ano entre 2000 e 2026. |
| duration_min | inteiro | Duração de filme ou episódio. |
| quality_score | decimal | Sinal sintético entre 3,8 e 9,7. |
| maturity_rating | categoria | Classificação indicativa. |

## interactions.csv

| Campo | Tipo | Regra |
|---|---|---|
| interaction_id | string | Identificador único do evento. |
| user_id | string | Chave para usuários. |
| item_id | string | Chave para catálogo. |
| event_type | categoria | skip, play, complete ou like. |
| event_weight | decimal | -1, 1, 3 ou 4. |
| watch_pct | decimal | Percentual assistido entre 0 e 1. |
| event_ts | timestamp | Data/hora do evento. |
| session_id | string | Sessão sintética. |
| source | categoria | Home, Busca, Minha lista ou Top 10. |

## Contratos mínimos de qualidade

- `user_id`, `item_id` e `event_ts` não podem ser nulos.
- Todo item de interação deve existir no catálogo.
- Todo usuário de interação deve existir na base de usuários.
- `watch_pct` deve estar entre 0 e 1.
- `event_type` deve pertencer ao domínio definido.
- Datas futuras devem bloquear o pipeline.

