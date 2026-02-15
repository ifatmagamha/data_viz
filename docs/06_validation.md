# 6. Stratégie de Validation

Les LLM peuvent produire :

- JSON mal formé
- Colonnes inexistantes
- Types incompatibles

Notre stratégie :

1. Extraction robuste du JSON
2. Validation Pydantic
3. Tentative de réparation via second prompt
4. Retry limité

Cela garantit une robustesse face à l’imprévisibilité du modèle.
