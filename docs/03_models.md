# 3. Modèles de Données (Pydantic)

Les propositions générées par le LLM sont validées via Pydantic.

## 3.1 Pourquoi utiliser Pydantic ?

Les LLM peuvent générer du JSON invalide ou incohérent.
Pydantic permet :

- Validation stricte du schéma
- Typage fort
- Détection d’erreurs précoces
- Sécurité d’exécution

## 3.2 Structure d’une Proposition

Chaque visualisation contient :

- chart_type
- x
- y
- color
- aggregation
- filters
- formatting
- reasoning

Cette structure formalise la visualisation comme un objet déclaratif.
