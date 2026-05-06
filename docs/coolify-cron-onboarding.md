# Cron Coolify : envoi onboarding emails J0 → J30

Le job `app/jobs/onboarding_emails.py` doit etre lance **une fois par jour** pour
scanner les tenants et envoyer J0/J1/J3/J5/J7/J14/J30 selon l'age.

## Option 1 (recommandee) : Cron via Coolify natif

Coolify supporte les "Scheduled Tasks" attachees a une application.

### Configuration

1. Coolify -> Project -> App `valina-bot-api-prod` -> onglet **Scheduled Tasks**
2. **Add new** :
   - Name : `onboarding-emails-daily`
   - Command : `python -m app.jobs.onboarding_emails`
   - Frequency : `0 9 * * *`   *(tous les jours a 9h UTC = 12h Madagascar)*
   - Container : leave default (= meme container que l'app)
3. Save.

Repeter sur l'env `stagging` si tu veux tester avec des tenants test.

### Verifier que ca tourne

- Coolify -> App -> **Logs** : grep "onboarding"
- Ou attache un test : Coolify -> App -> **Terminal** ->
  ```bash
  python -m app.jobs.onboarding_emails
  ```
  -> tu dois voir les logs `[onboarding] X tenants actifs a evaluer` etc.

## Option 2 (alternative) : Cron via systeme du VPS

Si tu preferes ne pas dependre de Coolify pour la planification :

```bash
# Sur le VPS (ssh ubuntu@161.97.149.233)
crontab -e

# Ajouter :
0 9 * * * docker exec <container_name> python -m app.jobs.onboarding_emails >> /var/log/valina-onboarding.log 2>&1
```

Trouver le `<container_name>` avec `docker ps | grep valina-bot-api`.

## Variables d'env requises (dans Coolify, env `production`)

```
BREVO_API_KEY=xkeysib-xxxxxxxxxxxxx
MAIL_FROM=hello@valina-bot.com
MAIL_FROM_NAME=Valina-Bot
DASHBOARD_BASE_URL=https://agent.valina-bot.com
```

(Les 3 dernieres ont des defaults dans `app/config.py`, donc seule
`BREVO_API_KEY` est strictement obligatoire pour activer l'envoi.)

## Premier lancement / smoke test

1. Verifier que les variables sont definies :
   ```bash
   docker exec <container> env | grep -i brevo
   ```
2. Lancer manuellement :
   ```bash
   docker exec <container> python -m app.jobs.onboarding_emails
   ```
3. Logs attendus :
   ```
   [onboarding] N tenants actifs a evaluer
   [onboarding] j0 -> client@example.com (tenant ...)
   [onboarding] DONE. envoyes=X skipped=Y failed=Z
   ```
4. Verifier dans Brevo -> **Statistics** -> **Email** que les emails partent
   (taux d'ouverture, clics, etc.)

## Sync templates (avant le 1er run)

**Important** : tant que `scripts/sync_brevo_templates.py` n'a pas ete lance
au moins une fois, le mapping `TEMPLATE_IDS` dans `app/services/brevo_templates.py`
est vide -> le job va lever `BrevoError` sur chaque tenant.

Premier lancement :

```bash
# En local, avec BREVO_API_KEY dans .env
python scripts/sync_brevo_templates.py
```

Output :
```
[sync] create template 'valina_onboarding_j0'
[sync]   -> j0 = 12
[sync] create template 'valina_onboarding_j1'
[sync]   -> j1 = 13
...
[OK] 7/7 templates sync.
```

Puis :
```bash
git add app/services/brevo_templates.py
git commit -m "chore(brevo): sync onboarding template ids"
git push origin master
```

-> staging redeploye auto, ensuite force deploy prod via le script Coolify.

## Modification des templates apres deploy

1. Editer `docs/onboarding-emails/templates/<email>.html`
2. Re-run en local : `python scripts/sync_brevo_templates.py` (update les IDs existants)
3. Commit & push (les IDs ne changent pas si update, donc pas de re-deploy strict
   necessaire, mais bon par hygiene).
