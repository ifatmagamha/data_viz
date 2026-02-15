# 5. Conception du Prompt LLM

Le prompt est externalisé dans `prompts/propose_viz.txt`.

## 5.1 Pourquoi externaliser le prompt ?

- Séparation logique
- Facilité d’expérimentation
- Lisibilité académique

## 5.2 Contraintes imposées au LLM

- 3 propositions exactement
- JSON strict
- Colonnes existantes uniquement
- Visualisations différentes
- Justification orientée métier

Cette contrainte structure la génération et réduit l’ambiguïté.
