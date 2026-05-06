# Email automation onboarding Valina-Bot

Sequence de 7 emails a envoyer aux clients qui demarrent l essai gratuit.

## Comment l implementer (gratuit ou cheap)

| Outil | Free tier | Avantage |
|---|---|---|
| **Resend** | 100 emails / jour gratuits | Simple, dev-friendly, API |
| **Brevo** | 300 emails / jour gratuits | Templates visuels, automation builder |
| **Loops** | 1000 contacts gratuits | Excellent pour onboarding sequences |
| **Mailchimp** | 500 contacts gratuits | Reference mais lourd |

Recommandation : **Brevo** si tu veux configurer les automation depuis une UI
visuelle (sans coder), **Resend** si tu preferes envoyer les emails depuis
le backend FastAPI (`app/api/emails.py`, ~50 lignes a ajouter).

## Variables a remplacer

Chaque email utilise des placeholders :

- `{{prenom}}` : prenom du client
- `{{nom_page}}` : nom de la page Facebook connectee
- `{{lien_dashboard}}` : URL dashboard du tenant (https://agent.valina-bot.com/dashboard)
- `{{lien_upload_catalog}}` : URL upload catalogue
- `{{lien_message_setup}}` : URL config message bienvenue
- `{{nb_messages_hier}}` : stat des messages traites la veille
- `{{nb_messages_total}}` : stat cumulative essai
- `{{nb_prospects_chauds}}` : nb prospects detectes
- `{{nb_commandes}}` : nb commandes auto-prises
- `{{nb_produits}}` : nb produits dans catalogue
- `{{nb_avec_photo}}` : nb produits avec image
- `{{lien_subscribe}}` : URL paiement
- `{{lien_tuto_photos}}` : URL tutoriel ajout photos

## Sequence (calendrier)

| Email | Quand | Objectif |
|---|---|---|
| J0 | Immediat apres signup | Bienvenue + 3 actions concretes |
| J1 | 24h apres | Premiers conseils + stats J0 |
| J3 | 72h apres | Check-in (1/2/3 reponse rapide) |
| J5 | 5 jours apres | Astuce catalogue avec photos |
| J7 | 7 jours apres | Fin essai + CTA paiement |
| J14 | 14 jours apres | Features avancees (post-paiement) |
| J30 | 30 jours apres | NPS + demande temoignage |

## Conditions d envoi

Tous les emails dependent du statut compte. Logique a implementer :

- J7, J14, J30 : envoyer SEULEMENT si compte actif (pas annule)
- J14 : envoyer SEULEMENT si client a paye apres essai
- J5 : envoyer SEULEMENT si nb_avec_photo < nb_produits (sinon le conseil
  ne sert a rien)

## Subject lines testees / a tester

Pour J0 :
- "Bienvenue sur Valina-Bot, {{prenom}}" (test A actuel)
- "{{prenom}}, ton bot est en ligne — voici la suite"
- "Setup Valina-Bot en 3 etapes ({{prenom}})"

Pour J7 (le plus critique) :
- "Ton essai Valina-Bot se termine demain" (test A actuel)
- "{{prenom}}, derniere chance de garder Valina-Bot"
- "Valina-Bot expire dans 24h — voici tes stats"
