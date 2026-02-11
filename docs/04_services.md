# 4. Services du Système

## 4.1 Dataset Service

Responsable de :
- Chargement du CSV
- Nettoyage léger
- Construction du résumé de schéma

## 4.2 Profiling Service

Produit des statistiques rapides :
- Type de variable
- Taux de valeurs manquantes
- Nombre de valeurs uniques
- Statistiques numériques

Ces informations améliorent la qualité des propositions du LLM.

## 4.3 LLM Service

Encapsule :
- Lecture du prompt depuis un fichier externe
- Appel à Gemini
- Extraction robuste du JSON
- Tentative de réparation si nécessaire

## 4.4 Viz Service

Transforme une spécification déclarative en figure Plotly.

## 4.5 Export Service

Permet l’export PNG via Kaleido.
