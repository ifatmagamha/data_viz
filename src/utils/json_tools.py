from __future__ import annotations

import json
import re
from typing import Any, Dict


def extract_json_loose(text: str) -> Dict[str, Any]:
    """
    If the model returns extra text, try to extract the first {...} JSON object.
    """
    text = (text or "").strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("Impossible d'extraire du JSON depuis la réponse du modèle.")

    return json.loads(match.group(0).strip())
