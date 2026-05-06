# Setup Brevo (10 min, 1 fois)

Brevo = moteur d'envoi emails onboarding J0 → J30 + transactionnels futurs.
Free tier : **9 000 emails/mois** (300/jour). Largement suffisant pour bootstrap.

## 1. Creer le compte Brevo (2 min)

1. Aller sur https://www.brevo.com/
2. **Sign up free** avec `studio.dev1@arpon.agency` (ou autre)
3. Confirmer l'email recu
4. Dans le formulaire onboarding Brevo :
   - Use case : `Send transactional emails`
   - Industry : `SaaS`
   - Skip les autres etapes

## 2. Verifier le domaine `valina-bot.com` (5 min + propagation DNS ~30 min)

C'est l'etape critique pour la deliverability. Sans verification, Gmail/Outlook
mettront tes emails en spam.

### 2a. Cote Brevo

1. Menu gauche → **Senders, Domains & Dedicated IPs** → onglet **Domains**
2. Bouton **Add a domain** → entrer `valina-bot.com`
3. Brevo te genere 3 records DNS a copier :
   - 1 record `TXT` pour SPF (commence par `v=spf1`)
   - 1 record `TXT` pour DKIM (commence par `k=rsa; p=...`)
   - 1 record `TXT` pour DMARC (commence par `v=DMARC1`)
4. **Garde cette page ouverte**, on revient apres etape 2b

### 2b. Cote Porkbun (DNS du domaine)

1. https://porkbun.com/ → login
2. **Account** → **Domain Management** → cliquer sur `valina-bot.com`
3. Onglet **DNS**
4. Ajouter les 3 records que Brevo a generes :

   | Type | Host | Value |
   |------|------|-------|
   | TXT  | (vide ou `@`) | `v=spf1 include:spf.brevo.com -all` |
   | TXT  | `mail._domainkey` (ou ce que Brevo dit) | `k=rsa; p=ABC...` |
   | TXT  | `_dmarc` | `v=DMARC1; p=none; rua=mailto:dmarc@valina-bot.com` |

5. Sauvegarder
6. **Attendre 15-30 min** (propagation DNS, parfois jusqu'a 24h mais rare avec Porkbun)

### 2c. Retour sur Brevo

1. Sur la page Domains, cliquer **Verify** sur `valina-bot.com`
2. Si tout est vert : domaine pret a envoyer
3. Si rouge : attendre 30 min de plus, re-verifier
4. Astuce : tester avec `dig TXT valina-bot.com @8.8.8.8` ou
   https://mxtoolbox.com/spf.aspx pour voir si SPF est propage

## 3. Creer le sender `hello@valina-bot.com` (1 min)

1. Menu → **Senders** → onglet **Senders**
2. **Add a sender** :
   - Sender name : `Valina-Bot`
   - Sender email : `hello@valina-bot.com`
3. Brevo envoie un email de confirmation a `hello@valina-bot.com`
4. **Probleme** : tu n'as pas encore de boite mail sur ce domaine

   **Solution rapide** : creer un alias gratuit chez Porkbun
   - Porkbun → DNS → onglet **Email Forwarding**
   - Forward `hello@valina-bot.com` → `studio.dev1@arpon.agency`
   - Sauvegarder
   - Attendre 5 min, le mail de confirmation Brevo va arriver dans ta boite Arpon
   - Cliquer le lien → sender verifie

## 4. Recuperer la cle API (1 min)

1. Menu → **SMTP & API** → onglet **API Keys**
2. **Generate a new API key** :
   - Name : `valina-bot-prod`
   - Permission : `Full Access`
3. Copier la cle (commence par `xkeysib-...`)

## 5. Ajouter les variables Coolify (1 min)

Dans Coolify, app `backend` (api.valina-bot.com), env vars :

```
BREVO_API_KEY=xkeysib-xxxxxxxxx
MAIL_FROM=hello@valina-bot.com
MAIL_FROM_NAME=Valina-Bot
```

Idem env `stagging` (api-staging.valina-bot.com) si tu veux tester avant prod.

Redeploy l'app pour que les variables soient prises en compte.

## 6. Verifier (1 min)

Une fois les variables ajoutees et le code Brevo deploye :

```bash
# depuis ton poste, test l'API :
curl -X POST https://api.valina-bot.com/api/admin/test-brevo \
  -H "Authorization: Bearer $JWT" \
  -d '{"to":"studio.dev1@arpon.agency"}'
```

Si tu recois l'email "Test Brevo Valina-Bot" → tout marche.

## Checklist finale

- [ ] Compte Brevo cree
- [ ] Domaine `valina-bot.com` verifie (3 records DNS Porkbun)
- [ ] Sender `hello@valina-bot.com` cree et confirme
- [ ] Email forwarding Porkbun configure (`hello@` → ton inbox)
- [ ] Cle API Brevo generee
- [ ] `BREVO_API_KEY`, `MAIL_FROM`, `MAIL_FROM_NAME` ajoutes dans Coolify (prod + stagging)
- [ ] Test endpoint `/api/admin/test-brevo` reussi

## Cout

- Free tier : 0 € / mois jusqu'a 9 000 emails (300/jour)
- Au dela : 19 €/mois pour 20 000 emails (Starter, branding retire)
- Compare au scenario "1 client = 7 emails sur 30j" : 9000/7 = ~1280 nouveaux clients/mois avant de payer

## Liens utiles

- Doc API Brevo : https://developers.brevo.com/
- SDK Python : https://github.com/sendinblue/APIv3-python-library
- Mailtester : https://www.mail-tester.com/ (envoyer un email a leur adresse pour scorer ta deliverability)
