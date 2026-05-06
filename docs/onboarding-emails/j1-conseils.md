# Email J1 - Premiers conseils (24h apres signup)

**Trigger** : 24h apres creation du tenant
**Delai** : J0 + 24h
**Conditions** : compte toujours actif, pas encore desabonne

---

## Subject

`3 conseils pour tes premieres conversations bot`

## Preheader

`Hier soir, ton bot a repondu a {{nb_messages_hier}} messages. Voici comment l ameliorer.`

## Corps

```
Salut {{prenom}},

Hier soir, ton bot a repondu a {{nb_messages_hier}} messages. Voici 3
conseils bases sur les premiers echanges :

1. Plus ton catalogue est precis, mieux le bot repond

   Ajoute les variantes (tailles, couleurs, photos) dans ton Excel. C est ce
   qui fait la difference entre "Desole je ne sais pas" et "Oui, on a la
   robe rouge en M et L, livraison Tana en 24h".

2. Active la detection prospects

   Le bot peut reperer automatiquement les clients prets a acheter (ceux
   qui parlent paiement, livraison, adresse). Tu recois une notif sur
   Telegram pour les rappeler personnellement.

   Activer : {{lien_dashboard}}/config

3. Teste-toi sur ton bot

   Va dans le dashboard, onglet Configuration > Test bot. Envoie une
   question comme un client. Tu vois la reponse en direct, et tu peux
   ajuster le ton si besoin.

Reponds a ce mail si tu as une question, je lis tout.

Manda

---
contact@valina-bot.com
```

## Variantes selon nb_messages_hier

- Si `nb_messages_hier == 0` : remplacer la 1ere ligne par "Ton bot tourne
  mais n a pas encore eu de message. C est normal le 1er jour. Voici 3
  conseils pour optimiser..."
- Si `nb_messages_hier > 50` : ajouter "Tu es deja tres actif. Voici
  comment scaler proprement..."

## Notes

- Toujours une stat concrete en intro (cree de la valeur immediate)
- 3 conseils actionnables (pas vague)
- "Reponds a ce mail" : ouvre le dialogue 1-1
