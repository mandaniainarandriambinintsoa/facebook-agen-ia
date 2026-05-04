# Scripts

## coolify_deploy.py — Force-deploy via API Coolify

Permet de declencher un Force deploy (without cache) sur Coolify via API,
sans avoir a cliquer dans l'UI a chaque fois.

### Setup (une seule fois)

1. Coolify -> Profile (icone bas-gauche) -> **Keys & Tokens** -> **API Tokens**
2. **Create new token** :
   - Name : `claude-deploy`
   - Permissions : minimum `deploy:write` si granular dispo, sinon `all`
3. Copier le token (commence par `ckp_...` ou similaire)
4. Ajouter le token dans le fichier `.env` a la racine du projet :

   ```
   COOLIFY_API_TOKEN=ckp_xxxxxxxxxxxxxxxx
   ```

   `.env` est deja dans `.gitignore`, donc le secret ne sera jamais commit.

   Alternative : exporter via shell (vie courte, par session) :
   ```powershell
   $env:COOLIFY_API_TOKEN="ckp_..."
   ```

### Usage

```bash
# Force deploy backend prod (le cas le plus frequent)
python scripts/coolify_deploy.py --env prod --app backend

# Deploy backend ET frontend prod en meme temps
python scripts/coolify_deploy.py --env prod --app both

# Deploy uniquement le frontend stagging
python scripts/coolify_deploy.py --env stagging --app frontend

# Redeploy normal (avec cache, pour les cas ou on veut juste relancer
# l'image existante sans rebuild). Equivalent du bouton "Redeploy".
python scripts/coolify_deploy.py --env prod --app backend --no-force
```

### UUIDs des apps

Hardcoded dans `coolify_deploy.py` (variable `APPS`). Si on renomme/recreate
des apps, mettre a jour ce dict. Les UUIDs sont visibles dans l'URL Coolify
quand on clique sur une app : `/application/<UUID>/...`.

### Comportement

Le script fait un `GET /api/v1/applications/{uuid}/deploy?force=true` avec
Bearer token. Coolify retourne immediatement (200) avec le deployment_uuid,
et le build/deploy continue en arriere-plan cote serveur.

Pour suivre la progression, ouvrir Coolify -> app -> onglet **Deployments**.
