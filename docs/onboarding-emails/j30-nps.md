# Email J30 - NPS et demande de temoignage (30 jours apres signup)

**Trigger** : 30 jours apres creation du tenant
**Delai** : J0 + 30 jours
**Conditions** :
- compte toujours actif
- client a paye au moins 1 mois

---

## Subject

`Une question rapide apres 30 jours`

## Preheader

`Sur 0 a 10, tu recommanderais Valina-Bot a un autre commercant ?`

## Corps

```
Salut {{prenom}},

Ca fait 30 jours que tu utilises Valina-Bot.

Sur une echelle de 0 a 10, quelle est la probabilite que tu recommandes
Valina-Bot a un autre commercant ?

Reponds juste par un chiffre.

Selon ta reponse :

- Si tu reponds 9 ou 10 : je te demanderai un temoignage court (2-3
  phrases) qui m aide a convaincre d autres commercants. En contrepartie,
  je t offre 1 mois gratuit.

- Si tu reponds 7 ou 8 : dis-moi ce qui manque pour que tu mettes 10.

- Si tu reponds 6 ou moins : appelons-nous, je regle le probleme. Mon
  WhatsApp : +261 XX XX XXX.

Merci pour ton temps.

Manda

---
contact@manda-ia.com
```

## Notes

- C est un classique du customer success : NPS (Net Promoter Score)
- 9-10 = promoter, 7-8 = passive, 0-6 = detractor
- Reponse en 1 chiffre = friction zero, taux de reponse 30-50%
- Si tu accumules 20 reponses, tu as un NPS officiel pour pitcher futurs
  clients ("nos clients nous mettent 8.5/10 en moyenne")

## Reponse type selon score

### Si client repond 9 ou 10
```
Excellent ! Voici ce que je te demande : peux-tu m envoyer 2-3 phrases
sur ce que Valina-Bot a change pour toi ? Idealement avec ton prenom +
nom de ta page (ex: "Manda Shop, Tana"). Je le mettrai sur le site.

En remerciement, le mois prochain est offert. Tu n as rien a faire,
j applique le credit sur ton compte.

Manda
```

### Si client repond 7 ou 8
```
Merci pour la note. Pour passer a 10, qu est-ce qui te manque ?

Reponds en 1-2 phrases, je vais voir ce qu on peut faire.

Manda
```

### Si client repond 6 ou moins
```
Aie. Desole que ca ne marche pas. Tu peux m appeler maintenant ? Voici
mon WhatsApp : +261 XX XX XXX.

On regle ca ensemble en 15 min, et si on n y arrive pas, je rembourse
ton dernier mois sans question.

Manda
```

## Une fois la reponse recue

- Sauvegarder dans un Google Sheet ou Notion : score, date, nom_page
- Recalculer le NPS chaque trimestre : (% promoters - % detractors)
- Promoters > 60% = excellent, 30-60% = bon, <30% = a ameliorer
