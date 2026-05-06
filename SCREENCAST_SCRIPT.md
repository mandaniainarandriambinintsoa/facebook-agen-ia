# Screencast Meta App Review — Script

**Durée cible** : 1:50 - 2:00
**Permissions démontrées** : `pages_show_list`, `pages_messaging`, `pages_manage_metadata`
**Méthode** : enregistrement silencieux → sous-titres ajoutés après via CapCut

## Setup avant record

- [ ] Fermer tous les onglets navigateur sauf Chrome DevTools
- [ ] Backend Render chaud (déjà fait, reste chaud ~15 min)
- [ ] Zoom navigateur à 100%
- [ ] Résolution écran 1920x1080 recommandé
- [ ] Lancer **Win+G** → onglet "Capturer" → bouton rouge Record
- [ ] Dire "GO" quand tu es prêt, je pilote

## Séquence (je pilote, tu n'as rien à faire)

| Temps | Action | Sous-titre |
|-------|--------|------------|
| **0:00-0:08** | Landing page `agent.valina-bot.com` | *Agent IA — Assistant automatique pour Messenger* |
| **0:08-0:12** | Clic "Se connecter avec Facebook" | *L'admin se connecte avec Facebook* |
| **0:12-0:20** | Page OAuth Facebook avec permissions | *Autorisation : pages_show_list, pages_messaging, pages_manage_metadata* |
| **0:20-0:25** | Clic "Continue" | *L'admin choisit sa page Manda-page* |
| **0:25-0:35** | Dashboard s'affiche avec stats | *Tableau de bord : 10 produits, 63% confiance moyenne* |
| **0:35-0:50** | Scroll dashboard → voir "Derniers messages" | *Historique des conversations client ↔ bot* |
| **0:50-1:05** | Clic sidebar "Plateformes" | *Gestion des canaux connectés* |
| **1:05-1:15** | Montrer card "Manda-page — Actif" | *pages_manage_metadata : webhook Messenger actif* |
| **1:15-1:25** | Clic sidebar "Produits" | *Catalogue produits synchronisé* |
| **1:25-1:40** | Montrer la liste des produits | *10 produits avec prix, stock, couleurs* |
| **1:40-1:55** | Clic sidebar "Messages" | *pages_messaging : réponse automatique IA aux clients* |
| **1:55-2:00** | Fin sur la table messages | *L'agent IA répond 24/7 en français et malgache* |

## Sous-titres (format SRT prêt pour CapCut)

Voir `screencast_subtitles.srt` à côté.

## Après l'enregistrement

1. Arrêter Win+G → fichier dans `Videos\Captures\`
2. Ouvrir CapCut (gratuit)
3. Importer vidéo + importer `screencast_subtitles.srt`
4. Ajuster le timing si nécessaire (glisser les sous-titres)
5. Export 1080p
6. Upload dans Meta App Review > Screencast

## Permissions expliquées

| Permission | Où c'est montré | Usage |
|------------|-----------------|-------|
| `pages_show_list` | OAuth + Plateformes | Lister les pages de l'admin pour lui permettre de choisir laquelle connecter |
| `pages_manage_metadata` | Plateformes (badge Actif) | S'abonner aux webhooks Messenger pour recevoir les messages |
| `pages_messaging` | Messages (réponses bot) | Envoyer une réponse automatique générée par IA au client |
