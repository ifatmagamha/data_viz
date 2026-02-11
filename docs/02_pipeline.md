# 2. Pipeline de Traitement des Données

Le pipeline suit les étapes suivantes :

1. Upload du dataset CSV
2. Nettoyage léger et standardisation des colonnes
3. Profiling statistique rapide
4. Construction d’un résumé du schéma
5. Appel au modèle Gemini
6. Validation stricte du JSON généré
7. Sélection par l’utilisateur
8. Génération du graphique final
9. Export au format PNG

Ce pipeline reproduit le raisonnement d’un analyste humain :
Question → Compréhension données → Choix visualisation → Rendu.
