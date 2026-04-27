import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata = {
  title: "Politique de confidentialite - Facebook Agent IA",
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-muted/40 p-4 md:p-8">
      <Card className="max-w-3xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl">Politique de confidentialite</CardTitle>
          <p className="text-sm text-muted-foreground">Derniere mise a jour : 4 mars 2026</p>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none space-y-6">
          <section>
            <h2 className="text-lg font-semibold">1. Introduction</h2>
            <p>
              Facebook Agent IA (&quot;le Service&quot;) est une plateforme SaaS operee par{" "}
              <strong>RANDRIAMBININTSOA MANDANIAINA</strong>, entrepreneur individuel base a
              LOT VT 85 HE BIS DB ANDOHANIMANDROSEZA, Antananarivo, Analamanga, 101, Madagascar.
              Le Service permet aux proprietaires de pages Facebook de configurer un assistant
              IA pour repondre automatiquement aux messages et commentaires de leurs clients.
            </p>
            <p>
              Cette politique de confidentialite explique comment nous collectons, utilisons
              et protegeons vos donnees personnelles.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">2. Donnees collectees</h2>
            <p>Nous collectons les donnees suivantes :</p>
            <ul className="list-disc pl-6 space-y-1">
              <li><strong>Donnees Facebook</strong> : identifiant utilisateur, nom, email, pages gerees, tokens d&apos;acces aux pages</li>
              <li><strong>Messages</strong> : messages recus sur vos pages Facebook et reponses generees par le bot</li>
              <li><strong>Catalogue produits</strong> : informations sur les produits que vous uploadez (nom, description, prix, images)</li>
              <li><strong>Donnees d&apos;utilisation</strong> : statistiques de messages, scores de confiance, historique des interactions</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold">3. Utilisation des donnees</h2>
            <p>Vos donnees sont utilisees exclusivement pour :</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>Generer des reponses automatiques pertinentes aux messages de vos clients</li>
              <li>Afficher les statistiques et l&apos;historique dans votre tableau de bord</li>
              <li>Ameliorer la qualite des reponses via le systeme RAG (Retrieval-Augmented Generation)</li>
              <li>Vous permettre de gerer votre catalogue produits</li>
            </ul>
            <p>Nous ne vendons jamais vos donnees a des tiers.</p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">4. Stockage et securite</h2>
            <ul className="list-disc pl-6 space-y-1">
              <li>Les donnees sont stockees sur des serveurs securises (Neon PostgreSQL, Render)</li>
              <li>Les tokens d&apos;acces Facebook sont chiffres en base de donnees</li>
              <li>Les communications sont protegees par HTTPS/TLS</li>
              <li>L&apos;acces au tableau de bord est protege par authentification JWT</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold">5. Partage des donnees</h2>
            <p>Vos donnees peuvent etre partagees avec :</p>
            <ul className="list-disc pl-6 space-y-1">
              <li><strong>Facebook/Meta</strong> : pour envoyer et recevoir des messages via l&apos;API Graph</li>
              <li><strong>Groq</strong> : le contenu des messages est envoye a l&apos;API Groq pour generer des reponses (sans donnees personnelles identifiables)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold">6. Suppression des donnees</h2>
            <p>
              Vous pouvez a tout moment supprimer vos donnees depuis le tableau de bord
              (produits, embeddings, historique). Pour demander la suppression complete de
              votre compte et de toutes vos donnees, contactez-nous a l&apos;adresse ci-dessous.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">7. Vos droits</h2>
            <p>Conformement aux reglementations applicables, vous disposez des droits suivants :</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>Droit d&apos;acces a vos donnees personnelles</li>
              <li>Droit de rectification</li>
              <li>Droit de suppression</li>
              <li>Droit a la portabilite des donnees</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold">8. Contact</h2>
            <p>
              Pour toute question concernant cette politique de confidentialite :<br />
              <strong>RANDRIAMBININTSOA MANDANIAINA</strong><br />
              LOT VT 85 HE BIS DB ANDOHANIMANDROSEZA, Antananarivo, Analamanga, 101, Madagascar<br />
              Email : contact@manda-ia.com
            </p>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
