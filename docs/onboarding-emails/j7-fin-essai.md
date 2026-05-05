# Email J7 - Fin essai (24h avant fin de la periode gratuite)

**Trigger** : 7 jours apres creation du tenant (~24h avant fin essai)
**Delai** : J0 + 6 jours et 12h
**Conditions** :
- compte toujours actif
- abonnement encore en essai gratuit (pas deja paye)

---

## Subject

`Ton essai Valina-Bot se termine demain`

## Preheader

`Tes stats : {{nb_messages_total}} messages, {{nb_commandes}} commandes auto. Continue ?`

## Corps

```
Salut {{prenom}},

Ton essai gratuit de 7 jours se termine demain.

Voici ce que ton bot a fait pour toi cette semaine :

- {{nb_messages_total}} messages traites automatiquement
- {{nb_prospects_chauds}} prospects chauds detectes
- {{nb_commandes}} commandes auto-prises
- ~{{heures_economisees}} heures gagnees (estimation)

Si tu veux continuer, choisis ton plan :

Plan Starter : 30 000 MGA / mois
- 1 page Facebook Messenger
- 1 000 messages / mois
- Catalogue jusqu a 100 produits

Plan Pro : 80 000 MGA / mois (recommande si plus de 1000 messages / mois)
- 3 pages Messenger
- 10 000 messages / mois
- Catalogue illimite, custom prompt, notifs Telegram

S abonner en 30 secondes : {{lien_subscribe}}

Si tu ne souhaites pas continuer, pas de probleme. Ton compte sera
automatiquement mis en pause apres-demain. Tes donnees restent 30 jours
au cas ou tu changerais d avis.

Une derniere chose : si tu hesites, reponds a ce mail. Je peux te faire
une demo perso pour voir ce qui te bloque.

Merci d avoir teste Valina-Bot.

Manda

---
contact@manda-ia.com
```

## Notes

- Email LE PLUS IMPORTANT de la sequence (taux conversion essai → payant)
- Mettre les stats en HAUT (rappelle la valeur creee)
- Pricing transparent (pas besoin de faire un appel pour connaitre le prix)
- "Si tu ne souhaites pas continuer..." rassure (pas de high pressure)
- "Reponds a ce mail" laisse une porte ouverte pour les indecis

## Variantes selon usage

### Si client a >0 commandes auto-prises
Garder le message tel quel.

### Si 0 commande auto mais >0 prospects chauds
Adapter intro :
"Ton bot a detecte {{nb_prospects_chauds}} prospects chauds cette semaine,
clients prets a acheter. C est exactement la valeur que Valina-Bot doit
te ramener. Pour transformer ces prospects en commandes payees, il faut
souvent rappeler manuellement..."

### Si 0 message traite (essai mort)
Email different :
"Salut {{prenom}}, je vois que ton bot n a pas eu de message cette
semaine. C est probablement parce que ta page n a pas eu beaucoup de
trafic, ou que le bot n est pas encore bien configure. On regle ca
ensemble en 15 min ? Reponds avec un creneau."

## Calcul `heures_economisees`

Estimation simple : `nb_messages_total × 2 minutes` arrondi a la demi-heure.
Exemple : 60 messages × 2 min = 120 min = 2 heures.

Si <30 min (donc <15 messages), ne pas inclure cette ligne dans l email.
