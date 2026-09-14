from __future__ import annotations

import json
import re
from pathlib import Path


class AnalyticsChatbot:
    """Deterministic, auditable analytics assistant: no paid API or secret required."""

    def __init__(self, dashboard_json: str | Path = "dashboard/assets/dashboard_data.json"):
        self.data = json.loads(Path(dashboard_json).read_text(encoding="utf-8"))

    def answer(self, question: str) -> dict:
        q = re.sub(r"\s+", " ", question.lower().strip())
        k = self.data["kpis"]
        m = self.data["metric_cards"]
        if any(term in q for term in ["recall", "acerto", "encontrou"]):
            answer = f"O Recall@10 do modelo híbrido é {m['recall_at_10']:.1%}. Ele mede quanto dos títulos relevantes do período de teste apareceu no top 10."
            next_step = "Validar em teste A/B com retenção, horas assistidas e satisfação como métricas de negócio."
        elif any(term in q for term in ["cobertura", "catálogo", "catalogo"]):
            answer = f"A cobertura do catálogo é {m['catalog_coverage']:.1%}. Isso ajuda a evitar que o produto recomende sempre os mesmos sucessos."
            next_step = "Monitorar cobertura por gênero e região, não apenas no total."
        elif any(term in q for term in ["diversidade", "bolha", "repetição", "repeticao"]):
            answer = f"A diversidade média de gêneros está em {m['genre_diversity']:.1%}. O re-ranking MMR equilibra relevância e variedade."
            next_step = "Testar lambdas entre 0,70 e 0,85 para encontrar o melhor equilíbrio em produção."
        elif any(term in q for term in [
    "tamanho da base",
    "volume",
    "quantos usuários",
    "quantos usuarios",
    "quantos títulos",
    "quantos titulos",
]):
            answer = f"A base demonstra {k['users']:,} usuários, {k['titles']:,} títulos e {k['interactions']:,} interações sintéticas."
            next_step = "Substituir os CSVs sintéticos por eventos anonimizados mantendo o mesmo contrato de dados."
        elif any(term in q for term in ["cold", "novo", "sem histórico", "sem historico"]):
            answer = "Para usuários novos, o motor usa preferências declaradas, popularidade qualificada e frescor. Após os primeiros eventos, migra para o score híbrido."
            next_step = "Coletar 3 gêneros ou títulos no onboarding e medir abandono desse passo."
        elif any(term in q for term in ["por que", "explica", "recomendou"]):
            answer = "Cada recomendação traz um motivo legível: afinidade de gênero, consumo positivo anterior ou similaridade com perfis próximos."
            next_step = "Exibir a razão na interface e permitir feedback ‘mais como isso’ / ‘não tenho interesse’."
        elif any(term in q for term in ["negócio", "negocio", "resultado", "ab"]):
            answer = "Offline, o modelo supera a referência de popularidade. Em negócio, isso ainda é hipótese: o próximo passo é um A/B test com guardrails."
            next_step = "Primária: horas assistidas por usuário. Secundárias: CTR, conclusão e retenção D30. Guardrails: skips, latência e concentração."
        else:
            answer = "Posso explicar Recall@10, cobertura, diversidade, cold start, volume da base, explicabilidade ou o desenho do teste A/B."
            next_step = "Exemplo: ‘Como tratar usuário novo?’"
        return {"answer": answer, "next_step": next_step, "scope": "Dados demonstrativos; não representa produção."}


if __name__ == "__main__":
    import sys
    bot = AnalyticsChatbot()
    print(json.dumps(bot.answer(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2))

