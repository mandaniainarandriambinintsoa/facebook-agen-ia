# Illustrations Valina-Bot landing

3 illustrations à générer (Bing Image Creator gratuit, ChatGPT, Midjourney, Stitch).

Style commun : **line-art éditorial noir sur fond crème, hand-drawn feel, no shading, no realism**.

## merchant-tired.png

Scène : commerçante mada épuisée à son comptoir, phone qui déborde de notifications.

```
Minimalist editorial line-art illustration, single thin black stroke 
on warm cream background #FAF9F5, no shading, hand-drawn feel similar 
to Stripe and Notion illustrations. A young Malagasy female merchant 
at her shop counter, looking exhausted at her smartphone which shows 
many notification bubbles overflowing the screen. She wears a 
patterned shirt suggesting traditional Malagasy lamba textile. 
Behind her, scattered hand-drawn doodle elements at 30% opacity: 
question marks, hourglass, small notification icons, stars. Composed 
asymmetrically with empty space on the right. 16:9 aspect ratio, 
flat illustration style, no gradients, no realism.
```

## customer-night.png

Scène : cliente serveie 24/7 qui chatte avec le bot la nuit.

```
Minimalist editorial line-art illustration, single thin black stroke 
on warm cream background #FAF9F5, no shading, hand-drawn feel. A 
relaxed Malagasy customer sitting on her couch at night, wearing 
casual clothes, holding her phone with a smile. A small lamp glows 
beside her on a side table. Speech bubbles emerge from the phone 
showing a quick response. Surrounding doodle elements at 30% opacity: 
crescent moon, stars, small plant. The scene feels calm, peaceful, 
late-evening. 16:9 aspect ratio, flat illustration style, no 
gradients.
```

## delivery-mvola.png

Scène : livreur Tana qui livre une commande validée Mvola.

```
Minimalist editorial line-art illustration, single thin black stroke 
on warm cream background #FAF9F5. A delivery person in Antananarivo 
wearing a casual t-shirt and cap, holding a package, ringing at a 
front door. A speech bubble shows "Mvola validé ✓" with a checkmark. 
Around them, doodle background at 30% opacity: motorcycle silhouette, 
small palm tree, woven baskets, address pin. 16:9 aspect ratio, flat 
illustration style, no realism, editorial magazine aesthetic.
```

## Outils suggérés

| Outil | Coût | Avantage |
|---|---|---|
| **Bing Image Creator** | Gratuit | DALL-E 3, illimité avec compte Microsoft, pas de queue |
| **ChatGPT free** | Gratuit (3-5/jour) | Intégré dans ChatGPT |
| **Stitch (Google)** | Gratuit | Génère aussi UI + image |
| **Midjourney** | $10/mois | Qualité plus stylée |

## Une fois générés

Mets les fichiers ici sous les noms exacts :
- `public/illustrations/merchant-tired.png`
- `public/illustrations/customer-night.png`
- `public/illustrations/delivery-mvola.png`

La landing les chargera automatiquement via next/image.

Le composant `IllustrationFrame` affiche un placeholder visuel guidé tant
que le fichier est absent, donc tu peux push la landing avant d'avoir les
images, et les ajouter ensuite.
