from __future__ import annotations

import logging
import google.generativeai as genai

from src.config import settings
from src.models.viz_spec import ProposalsResponse
from src.utils.json_tools import extract_json_loose

log = logging.getLogger(__name__)


SYSTEM_INSTRUCTION = """
Tu es un expert en data visualization.

Tu dois proposer EXACTEMENT 3 visualisations différentes et pertinentes.
Réponds UNIQUEMENT en JSON valide (pas de markdown, pas de texte autour).
Utilise UNIQUEMENT des colonnes existantes.

Bonnes pratiques:
- Lisibilité > complexité
- Titres & labels clairs
- Si la variable demandée n'existe pas (ex: ventes), choisis un proxy plausible et explique-le dans "reasoning".
""".strip()


PROMPT_TEMPLATE = """
Problématique:
{question}

Schéma du dataset (nom:type:exemple):
{schema}

Profil rapide (optionnel):
{profile}

Réponds STRICTEMENT avec un JSON dans ce format:
{{
  "proposals": [
    {{
      "id": 1,
      "title": "...",
      "chart_type": "bar|line|scatter|box|hist|heatmap",
      "x": "col_name",
      "y": "col_name_or_null",
      "color": "col_name_or_null",
      "aggregation": "mean|sum|count|median|none",
      "filters": [{{"col":"...","op":"==|!=|>|<|in","value":"..."}}],
      "reasoning": "Justification courte orientée métier (1-3 phrases)",
      "formatting": {{
        "x_label": "...",
        "y_label": "...",
        "sort": "asc|desc|null",
        "top_k": 20
      }}
    }},
    {{ "id": 2, "title": "...", "chart_type": "...", "x": "...", "y": null, "color": null, "aggregation": "none", "filters": [], "reasoning": "...", "formatting": {{"x_label":"...","y_label":"...","sort": null, "top_k": 20}} }},
    {{ "id": 3, "title": "...", "chart_type": "...", "x": "...", "y": null, "color": null, "aggregation": "none", "filters": [], "reasoning": "...", "formatting": {{"x_label":"...","y_label":"...","sort": null, "top_k": 20}} }}
  ]
}}

Contraintes:
- 3 propositions VRAIMENT différentes (comparaison / relation / distribution par ex.)
- Pour scatter: x et y numériques si possible
- Pour bar/line avec y: propose une aggregation adaptée
""".strip()


def _ensure_key() -> None:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY manquant. Mets-le dans .env.")


def generate_three_proposals(question: str, schema: str, profile_text: str = "") -> ProposalsResponse:
    _ensure_key()
    genai.configure(api_key=settings.gemini_api_key)

    model = genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=SYSTEM_INSTRUCTION,
    )

    prompt = PROMPT_TEMPLATE.format(question=question, schema=schema, profile=profile_text or "(vide)")

    last_err = None
    for attempt in range(settings.llm_max_retries + 1):
        try:
            resp = model.generate_content(prompt)
            data = extract_json_loose(resp.text or "")
            return ProposalsResponse.model_validate(data)
        except Exception as e:
            last_err = e
            log.warning("LLM attempt %s failed: %s", attempt + 1, e)

    raise RuntimeError(f"LLM a échoué après retries: {last_err}")
