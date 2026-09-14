# Guia completo — do zero à apresentação

## 1. O racional do case

O case foi desenhado para mostrar cinco competências ao mesmo tempo: visão de produto, engenharia de dados, ciência de dados, automação e comunicação executiva. O erro comum seria começar pelo algoritmo. Aqui começamos pela decisão.

**Decisão:** devemos substituir uma faixa de títulos populares por recomendações personalizadas?

**Hipótese:** o recomendador híbrido aumenta descoberta relevante e horas assistidas.

**Risco:** o algoritmo pode elevar cliques e ainda piorar satisfação, repetir títulos, criar bolhas ou concentrar exposição.

Por isso, a avaliação combina relevância, ordenação, cobertura, diversidade e novidade.

## 2. Ferramentas gratuitas e online

| Necessidade | Ferramenta | Por que foi escolhida |
|---|---|---|
| Notebook e treino | Google Colab | Não exige instalação e oferece recursos gratuitos, sujeitos a disponibilidade. |
| Versionamento | GitHub público | Portfólio auditável e fácil de compartilhar. |
| Automação | GitHub Actions | Executa pipeline, testes e publicação; gratuito em runners padrão para repositórios públicos. |
| Dashboard | HTML, CSS, JavaScript e Plotly.js | Controle visual, responsividade e publicação estática. |
| Hospedagem | GitHub Pages | Publica HTML/CSS/JS diretamente do repositório público no plano Free. |
| API local/demonstração | FastAPI | Documentação automática e baixo acoplamento. |
| Chatbot | Regras/intenções auditáveis | Zero custo, sem segredo e sem alucinação de números. |

Fontes oficiais consultadas em 14/09/2026: [Google Colab FAQ](https://research.google.com/colaboratory/faq.html), [GitHub Plans](https://docs.github.com/get-started/learning-about-github/githubs-products), [GitHub Actions billing](https://docs.github.com/billing/managing-billing-for-github-actions/about-billing-for-github-actions) e [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages). Planos e limites podem mudar.

## 3. Clique a clique: criar o repositório

1. Acesse `github.com` e entre na sua conta.
2. Clique no sinal **+** no canto superior direito e em **New repository**.
3. Use o nome `vibeplay-recommendation-intelligence`.
4. Em **Description**, use: `Sistema híbrido de recomendação, automação, chatbot analítico e dashboard HTML.`
5. Marque **Public**. Isso deixa o portfólio visível e mantém Pages/Actions no cenário gratuito documentado.
6. Não inicialize com README, pois o pacote já contém um.
7. Clique em **Create repository**.
8. Faça upload do conteúdo deste projeto, preservando as pastas.

## 4. Clique a clique: executar no Google Colab

1. Acesse `colab.research.google.com`.
2. Clique em **File → Upload notebook**.
3. Escolha `notebooks/VibePlay_Case_Colab.ipynb`.
4. Na primeira célula, substitua `SEU_USUARIO` pelo seu usuário do GitHub.
5. Clique em **Runtime → Run all**.
6. Se o Colab mostrar o aviso de notebook não criado pelo Google, revise o código e confirme a execução.
7. Aguarde a instalação das bibliotecas, geração dos dados, treino e testes.
8. Confira a tabela final de métricas. O pipeline usa semente 42 para ser reproduzível.

### Por que não começamos com deep learning?

Porque o objetivo é demonstrar uma solução adequada ao volume e ao problema. SVD + conteúdo é rápido, explicável, barato e suficiente como challenger sério. Uma rede neural sem ganho comparável seria complexidade sem valor comprovado.

## 5. Como a base sintética foi criada

Há três entidades:

- `users.csv`: segmento, região, plano, dispositivo e preferências.
- `catalog.csv`: tipo, gêneros, ano, duração, classificação e qualidade.
- `interactions.csv`: play, complete, like ou skip, percentual assistido, origem e data.

Cada pessoa recebe uma distribuição latente de preferências por gênero. A chance de interação positiva cresce quando o catálogo é compatível com essa distribuição, mas inclui ruído e popularidade global. Isso evita uma base perfeita e irreal.

## 6. Preparação e prevenção de vazamento

O split é temporal dentro de cada usuário: aproximadamente 80% das interações mais antigas treinam; as 20% mais recentes testam. Um split aleatório deixaria o futuro ajudar a prever o passado e superestimaria o resultado.

Eventos recebem pesos implícitos:

| Evento | Peso | Interpretação |
|---|---:|---|
| skip | -1 | rejeição explícita por comportamento |
| play | 1 | interesse inicial |
| complete | 3 | consumo forte |
| like | 4 | preferência explícita |

No treinamento matricial, sinais negativos não viram “consumo negativo”; eles são usados para reduzir interesse e não para criar fatoração com confiança invertida.

## 7. Motor de recomendação

### 7.1 Colaborativo

Uma matriz usuário × título agrega feedback implícito. O Truncated SVD projeta pessoas e itens em fatores latentes. A similaridade capta padrões como “quem gostou destes títulos também tende a consumir aqueles”, mesmo sem gênero igual.

### 7.2 Conteúdo

Gêneros e tipo viram vetores TF-IDF. O perfil de conteúdo do usuário é a média ponderada do que ele consumiu positivamente.

### 7.3 Score híbrido

`score = 0,52 colaborativo + 0,28 conteúdo + 0,12 popularidade + 0,08 frescor`

Os pesos são uma configuração inicial informada por produto. Não são apresentados como ótimos; devem ser ajustados por validação e experimento.

### 7.4 Diversidade

O top N bruto pode conter dez títulos quase iguais. O re-ranking MMR escolhe o próximo item equilibrando relevância e semelhança com o que já entrou na lista. `diversity_lambda=0.78` mantém a relevância como prioridade, mas penaliza repetição.

### 7.5 Cold start

Para usuário novo, o onboarding pede três gêneros ou títulos. O score inicial usa 68% conteúdo, 22% popularidade e 10% frescor. Conforme surgem eventos, o componente colaborativo passa a dominar.

## 8. Métricas: como explicar sem decorar

- **Precision@10:** das dez recomendações, quantas eram relevantes.
- **Recall@10:** dos títulos relevantes disponíveis no teste, quantos apareceram no top 10.
- **NDCG@10:** valoriza acertos nas primeiras posições.
- **Coverage:** fração do catálogo recomendada para a amostra.
- **Diversidade:** variedade média de gêneros nas listas.
- **Novidade:** favorece itens menos óbvios, sem confundir novidade com qualidade.

Não existe “métrica boa” universal. Compare contra baseline, histórico, custo e objetivo.

## 9. Chatbot: por que não usar uma API paga

O chatbot deste case responde somente a intenções conhecidas e lê números do artefato gerado. Isso oferece três vantagens: custo zero, consistência e auditabilidade. Em produção, um LLM poderia traduzir linguagem natural para uma camada semântica controlada, mas nunca deveria inventar métrica ou consultar tabela sem permissão.

Perguntas aceitas:

- “O Recall@10 está bom?”
- “Como tratar usuário novo?”
- “Qual a cobertura do catálogo?”
- “Como evitar bolha?”
- “Como validar o resultado no negócio?”
- “Por que este título foi recomendado?”

## 10. Automação

O workflow `.github/workflows/retrain.yml` roda:

1. manualmente;
2. a cada push relevante na branch `main`;
3. às segundas-feiras, 09:17 UTC.

Passos: instalar dependências → gerar dados → treinar → avaliar → testar → verificar guardrails → publicar dashboard.

Se cobertura, diversidade ou taxa positiva caírem abaixo do limite, `check_guardrails.py` encerra a execução. O modelo anterior permanece como referência. Em produção, o artefato só seria promovido após aprovação e shadow test.

## 11. Clique a clique: ativar o dashboard

1. No repositório GitHub, clique em **Settings**.
2. No menu lateral, clique em **Pages**.
3. Em **Build and deployment**, selecione **GitHub Actions**.
4. Volte para a aba **Actions**.
5. Abra **Retrain, validate and publish dashboard**.
6. Clique em **Run workflow** e confirme a branch `main`.
7. Abra a execução e confirme que todos os passos ficaram verdes.
8. Volte a **Settings → Pages** e clique em **Visit site**.

## 12. Teste A/B proposto

**Unidade de randomização:** usuário, para impedir que a mesma pessoa alterne de experiência.

**Controle:** trilho de popularidade atual.

**Tratamento:** top N híbrido com diversidade e explicações.

**Primária:** horas assistidas por usuário elegível.

**Secundárias:** CTR do trilho, taxa de conclusão, títulos distintos e retenção D30.

**Guardrails:** skip precoce, latência p95, concentração de exposição, reclamações e opt-out.

Antes do teste, calcular amostra mínima usando baseline, efeito mínimo detectável, poder de 80% e significância de 5%. Não encerrar quando o p-valor “ficar bonito”; respeitar janela e plano pré-registrado.

## 13. O que melhoraria em produção

- Feature store e identificação consistente entre dispositivos.
- Eventos idempotentes e schema versionado.
- Modelo incremental ou retreino por mudança de distribuição.
- Candidate generation e ranking em duas etapas.
- Latência, cache e fallback por contexto.
- Avaliação por segmentos, não só média global.
- Regras de conteúdo, idade e disponibilidade regional.
- Privacidade, retenção mínima e direito de opt-out.
- Champion–challenger e rollback automatizado.

## 14. Checklist antes de apresentar

- Rode o notebook do início ao fim.
- Abra o dashboard e teste filtros e chat.
- Conheça a diferença entre métrica offline e causal.
- Não diga “IA aumentou retenção”; diga “é a hipótese a testar”.
- Explique por que popularidade é baseline e não vilã.
- Mostre uma limitação real antes que perguntem.
- Termine com decisão e próximo experimento.

