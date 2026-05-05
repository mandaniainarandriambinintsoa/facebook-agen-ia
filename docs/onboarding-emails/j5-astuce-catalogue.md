# Email J5 - Astuce catalogue avec photos (5 jours apres signup)

**Trigger** : 5 jours apres creation du tenant
**Delai** : J0 + 5 jours
**Conditions** :
- compte toujours actif
- `nb_produits > 0`
- `nb_avec_photo < nb_produits` (sinon l email ne sert a rien, le client a
  deja toutes les photos)

---

## Subject

`L astuce qui double les ventes via Valina-Bot`

## Preheader

`Tes clients qui demandent "elle existe en quelle couleur" recoivent la photo en 2 sec.`

## Corps

```
Salut {{prenom}},

Statistique observee chez nos clients beta : ceux qui ajoutent des photos
produits dans leur catalogue Excel ont un taux de conversion 2x plus eleve
que ceux qui n en ont pas.

Pourquoi ?

Parce que le bot envoie automatiquement la photo du produit en reponse aux
questions style "elle existe en quelle couleur ?" ou "vous l avez en
quelle taille ?".

Le client a la photo en 2 secondes au lieu d attendre que tu sois libre.

Comment ajouter les photos a ton catalogue :

1. Dans ton Excel ou Google Sheets, ajoute une colonne "image_url"
2. Mets l URL de la photo de chaque produit (Drive public, Imgur, ton
   site web, ou meme un screenshot d Instagram)
3. Re-upload le catalogue dans le dashboard

Tutoriel video de 2 min : {{lien_tuto_photos}}

Etat actuel de ton catalogue :
- {{nb_produits}} produits charges
- {{nb_avec_photo}} avec photo
- Tu peux faire mieux !

Manda

---
contact@manda-ia.com
```

## Notes

- Argument data ("2x plus eleve") concret et credible
- Step-by-step technique mais simple
- Le rappel `{{nb_avec_photo}} / {{nb_produits}}` met une legere pression
  positive
- Tutoriel video : si pas pret, remplacer par une page dashboard avec
  3 captures d ecran annotees
