# 1. Architecture Générale du Système

## 1.1 Objectif du Projet

Ce projet vise à concevoir un système intelligent capable de transformer :
- une problématique métier (texte libre)
- un dataset tabulaire (CSV)

en propositions de visualisations pertinentes, générées automatiquement via un Large Language Model (Gemini).

## 1.2 Architecture en Couches

Le système est structuré en plusieurs couches :

1. Interface utilisateur (Streamlit)
2. Couche d’orchestration (controller)
3. Services spécialisés (LLM, profiling, visualisation, export)
4. Modèles de données (Pydantic)
5. Utilitaires techniques

Cette séparation respecte le principe de séparation des responsabilités (Separation of Concerns).

## 1.3 Avantages de cette Architecture

- Modularité
- Maintenabilité
- Testabilité
- Robustesse face aux erreurs du LLM
