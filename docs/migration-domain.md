# Migration domaine : manda-ia.com → valina-bot.com

**Contexte** : 0 client en prod actuellement. C'est le moment ideal pour
migrer avant le lancement officiel.

**Duree totale** : ~1h de manip + 30 min propagation DNS.

**Couverture** :
- DNS Porkbun (records A + CNAME + Brevo)
- Coolify (changer domaines des apps + cert SSL auto)
- Meta App (App Domains, OAuth, Privacy URL, Webhook)
- Validation E2E

---

## Phase 1 — DNS Porkbun (15 min + 30 min propagation)

### 1a. Login + page DNS

1. https://porkbun.com/account/login
2. **Domain Management** -> cliquer sur `valina-bot.com`
3. Onglet **DNS**

### 1b. Records pour la prod (A records vers VPS Contabo)

VPS IP : `161.97.149.233`

Ajouter ces 4 records :

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A | (vide ou `@`) | `161.97.149.233` | 600 |
| A | `www` | `161.97.149.233` | 600 |
| A | `api` | `161.97.149.233` | 600 |
| A | `agent` | `161.97.149.233` | 600 |

Optionnel pour staging (si tu veux le faire propre) :

| A | `api-staging` | `161.97.149.233` | 600 |
| A | `agent-staging` | `161.97.149.233` | 600 |

### 1c. Records Brevo (DKIM/SPF/DMARC)

Cf. `docs/brevo-setup.md` section 2.

### 1d. Email forwarding (pour `contact@` et `hello@`)

Porkbun -> DNS -> onglet **Email Forwarding** :

| Alias | Forward to |
|-------|------------|
| `contact@valina-bot.com` | `studio.dev1@arpon.agency` |
| `hello@valina-bot.com` | `studio.dev1@arpon.agency` |

### 1e. Verifier la propagation

Attendre 15-30 min puis :

```bash
# Doit retourner 161.97.149.233
nslookup api.valina-bot.com 8.8.8.8
nslookup agent.valina-bot.com 8.8.8.8
```

Ou utiliser https://dnschecker.org (interface visuelle).

---

## Phase 2 — Coolify (15 min)

### 2a. App backend prod

1. Coolify -> Project -> App `valina-bot-api-prod` (ou nom equivalent)
2. Onglet **General** -> section **Domains** :
   - **Retirer** : `https://api.manda-ia.com`
   - **Ajouter** : `https://api.valina-bot.com`
3. Save -> Coolify regenere automatiquement le cert Let's Encrypt
4. Verifier : `https://api.valina-bot.com/health` doit retourner 200 OK

### 2b. App dashboard prod

1. App `valina-bot-dashboard-prod`
2. **Domains** :
   - Retirer : `https://agent.manda-ia.com`
   - Ajouter : `https://agent.valina-bot.com`
3. Save -> reverify
4. Verifier : `https://agent.valina-bot.com` charge le dashboard

### 2c. Variables d'env (si prod a des URLs hardcodees)

Sur l'app dashboard prod, env var :

| Variable | Avant | Apres |
|----------|-------|-------|
| `NEXT_PUBLIC_API_URL` | `https://api.manda-ia.com` | `https://api.valina-bot.com` |

Sur l'app backend prod :

| Variable | Avant | Apres |
|----------|-------|-------|
| `FACEBOOK_OAUTH_REDIRECT_URI` | `https://api.manda-ia.com/auth/facebook/callback` | `https://api.valina-bot.com/auth/facebook/callback` |
| `DASHBOARD_BASE_URL` | (default) | `https://agent.valina-bot.com` |
| `MAIL_FROM` | — | `hello@valina-bot.com` |
| `MAIL_FROM_NAME` | — | `Valina-Bot` |
| `BREVO_API_KEY` | — | `xkeysib-...` (si Brevo deja setup) |

Force deploy sans cache (script habituel ou bouton Coolify).

### 2d. Idem env stagging si tu maintiens un staging

Memes operations sur `valina-bot-api-stagging` et `valina-bot-dashboard-stagging`.

---

## Phase 3 — Meta App (15 min)

⚠️ **Important** : ta BV est deja approuvee. Les changements ci-dessous
**ne necessitent pas une nouvelle App Review** tant que les URLs sont
coherentes (meme produit, juste nouveau domaine). Mais Meta peut faire un
re-check automatique : prevois ~24h de surveillance.

1. https://developers.facebook.com/ -> ton App `valina-bot` (ou nom equivalent)

### 3a. Settings -> Basic

| Champ | Avant | Apres |
|-------|-------|-------|
| App Domains | `manda-ia.com` | `valina-bot.com` |
| Privacy Policy URL | `https://agent.manda-ia.com/privacy` | `https://agent.valina-bot.com/privacy` |
| Terms of Service URL | `https://agent.manda-ia.com/terms` | `https://agent.valina-bot.com/terms` |
| User Data Deletion | `https://agent.manda-ia.com/data-deletion` | `https://agent.valina-bot.com/data-deletion` |

Save changes.

### 3b. Facebook Login -> Settings

| Champ | Avant | Apres |
|-------|-------|-------|
| Valid OAuth Redirect URIs | `https://api.manda-ia.com/auth/facebook/callback` | `https://api.valina-bot.com/auth/facebook/callback` |
| Allowed Domains for the JavaScript SDK | `manda-ia.com` | `valina-bot.com` |

⚠️ Garder l'ancien aussi pendant 1 semaine en cas de rollback :
```
https://api.valina-bot.com/auth/facebook/callback
https://api.manda-ia.com/auth/facebook/callback
```

### 3c. Webhooks

1. Webhooks -> Page (Messenger)
2. Edit subscription :
   - Callback URL : `https://api.valina-bot.com/webhook/messenger`
   - Verify Token : (inchange)
3. **Verify and save** -> Meta fait un GET sur la nouvelle URL pour
   verifier (ton backend doit deja repondre, sinon failed)

### 3d. Pages connectees (cote utilisateur)

Les tokens stockes en DB restent valides cote Meta : aucun re-OAuth
n'est necessaire pour les pages deja connectees (= 0 dans ton cas).

---

## Phase 4 — Code (deja fait, push + deploy)

Le code est deja a jour cote dev. Push :

```bash
git add -A
git commit -m "feat(branding): migration manda-ia.com -> valina-bot.com"
git push origin master
```

Staging redeploye auto -> verifier que ca tourne sur les nouveaux domaines.
Puis force deploy prod via le script Coolify.

---

## Phase 5 — Validation E2E (10 min)

### Checklist

- [ ] `https://valina-bot.com` (landing) -> charge OK
- [ ] `https://agent.valina-bot.com` -> dashboard public OK
- [ ] `https://agent.valina-bot.com/login` -> page login OK
- [ ] Clic "Connexion Facebook" -> redirige bien vers Meta -> retour OK
  -> tenant cree avec `owner_email` rempli
- [ ] `https://api.valina-bot.com/health` -> 200 OK
- [ ] `https://api.valina-bot.com/openapi.json` -> JSON OK
- [ ] `https://api.valina-bot.com/webhook/messenger?hub.mode=subscribe&hub.verify_token=<TOKEN>&hub.challenge=test` -> renvoie `test`
- [ ] Test envoi message Messenger -> bot repond
- [ ] Test inscription nouveau compte -> email J0 recu sur `hello@valina-bot.com`
- [ ] `mailto:contact@valina-bot.com` -> mail forward fonctionne (Porkbun)

### Mailtester deliverability

Une fois tout OK, scorer la deliverability emails :
1. Aller sur https://mail-tester.com
2. Copier l'adresse genere (ex: `test-abc@srv1.mail-tester.com`)
3. Trigger un envoi de J0 vers cette adresse :
   ```bash
   curl -X POST https://api.valina-bot.com/api/admin/test-brevo \
     -H "Authorization: Bearer $JWT" \
     -d '{"to":"test-abc@srv1.mail-tester.com"}'
   ```
4. Cliquer "Then check your score"
5. Cible : **>= 9/10**. Si moins, voir les recommandations (souvent SPF/DKIM/DMARC).

---

## Phase 6 — Cleanup (optionnel, J+7)

Apres 1 semaine de stabilite sur `valina-bot.com` :

### Code
- `app/main.py` ligne 80 : retirer `https://agent.manda-ia.com` du CORS
- Verifier qu'aucun lien externe pointe vers `manda-ia.com` dans la doc legacy

### Coolify
- Retirer les domaines `*.manda-ia.com` des apps (deja fait phase 2 si remplace,
  pas si ajoute en alias)

### Meta App
- Retirer l'ancien Redirect URI `api.manda-ia.com/auth/facebook/callback`

### DNS Porkbun
- Garder le domaine `manda-ia.com` (~10€/an) ou le laisser expirer ?
  - **Garder** si tu veux pouvoir y revenir, ou si des liens externes
    (Google indexation, screenshots blog, etc.) pointent encore dessus
  - **Laisser expirer** si propre et pas de SEO accumule

### Renouveau domaine
- Brancher l'envoi des emails depuis `hello@valina-bot.com` au lieu de
  l'ancienne adresse (deja prevu dans `MAIL_FROM` env var)

---

## Plan de rollback (au cas ou)

Si quelque chose casse en prod et que tu dois revenir vite :

1. Coolify : reverter les domaines (5 min)
   - Backend : remettre `api.manda-ia.com` en plus
   - Dashboard : remettre `agent.manda-ia.com`
2. DNS Porkbun : les anciens A records de `manda-ia.com` n'ont pas bouge
   (on n'a touche que `valina-bot.com`)
3. Meta App : les anciens Redirect URIs sont toujours dans la liste
   (recommandation phase 3b)
4. Code : `git revert` du commit migration + force deploy

Donc rollback ~10 min max si la nouvelle config a un probleme.

---

## Recap : ce que tu dois faire concretement

1. Phase 1 (DNS) : 15 min de manip + 30 min d'attente -> le plus long
2. Phase 2 (Coolify) : 15 min
3. Phase 3 (Meta App) : 15 min
4. Phase 4 (deploy) : 5 min (commit + push + force deploy)
5. Phase 5 (test) : 10 min

**Total : ~1h hands-on, sur une matinee tranquille.**
