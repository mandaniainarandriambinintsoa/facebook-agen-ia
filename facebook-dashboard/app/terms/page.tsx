import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata = {
  title: "Conditions d'utilisation - Facebook Agent IA",
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-muted/40 p-4 md:p-8">
      <Card className="max-w-3xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl">Conditions d&apos;utilisation</CardTitle>
          <p className="text-sm text-muted-foreground">Derniere mise a jour : 4 mars 2026</p>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none space-y-6">
          <section>
            <h2 className="text-lg font-semibold">1. Acceptation des conditions</h2>
            <p>
              Facebook Agent IA (&quot;le Service&quot;) est opere par{" "}
              <strong>RANDRIAMBININTSOA MANDANIAINA</strong>, entrepreneur individuel domicilie
              a LOT VT 85 HE BIS DB ANDOHANIMANDROSEZA, Antananarivo, Analamanga, 101, Madagascar.
              En utilisant le Service, vous acceptez les presentes conditions d&apos;utilisation.
              Si vous n&apos;acceptez pas ces conditions, veuillez ne pas utiliser le Service.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">2. Description du Service</h2>
            <p>
              Facebook Agent IA est une plateforme SaaS qui permet aux proprietaires de pages
              Facebook de deployer un assistant IA capable de :
            </p>
            <ul className="list-disc pl-6 space-y-1">
              <li>Repondre automatiquement aux messages Messenger</li>
              <li>Repondre aux commentaires sur les publications</li>
              <li>Presenter un catalogue de produits interactif</li>
              <li>Fournir des statistiques sur les interactions</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold">3. Compte et acces</h2>
            <ul className="list-disc pl-6 space-y-1">
              <li>L&apos;acces au Service se fait via l&apos;authentification Facebook OAuth</li>
              <li>Vous devez etre administrateur de la page Facebook que vous souhaitez connecter</li>
              <li>Vous etes responsable de la securite de votre compte Facebook</li>
              <li>Vous ne devez pas partager vos tokens d&apos;acces avec des tiers</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold">4. Utilisation acceptable</h2>
            <p>Vous vous engagez a :</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>Respecter les <a href="https://developers.facebook.com/terms/" className="underline" target="_blank" rel="noopener noreferrer">conditions d&apos;utilisation de la plateforme Meta</a></li>
              <li>Ne pas utiliser le Service pour envoyer du spam ou du contenu illegal</li>
              <li>Ne pas tenter de contourner les mesures de securite du Service</li>
              <li>Ne pas utiliser le Service pour collecter des donnees personnelles sans consentement</li>
              <li>Fournir des informations produits exactes et a jour</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold">5. Contenu et responsabilite</h2>
            <ul className="list-disc pl-6 space-y-1">
              <li>Vous etes responsable du contenu de votre catalogue produits</li>
              <li>Les reponses generees par l&apos;IA sont basees sur votre catalogue et peuvent contenir des inexactitudes</li>
              <li>Nous ne garantissons pas l&apos;exactitude des reponses generees automatiquement</li>
              <li>Vous etes responsable de verifier que les reponses du bot sont appropriees pour vos clients</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold">6. Disponibilite du Service</h2>
            <p>
              Nous nous efforcons de maintenir le Service disponible 24h/24, mais ne garantissons
              pas une disponibilite ininterrompue. Des interruptions peuvent survenir pour
              maintenance, mises a jour ou problemes techniques.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">7. Propriete intellectuelle</h2>
            <p>
              Le Service, son code source et son design sont la propriete de Facebook Agent IA.
              Vous conservez la propriete de vos donnees (catalogue, messages, etc.).
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">8. Resiliation</h2>
            <p>
              Vous pouvez cesser d&apos;utiliser le Service a tout moment en revoquant l&apos;acces
              de l&apos;application dans vos parametres Facebook. Nous nous reservons le droit de
              suspendre ou supprimer votre acces en cas de violation de ces conditions.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">9. Limitation de responsabilite</h2>
            <p>
              Le Service est fourni &quot;tel quel&quot;. Nous ne sommes pas responsables des dommages
              directs ou indirects resultant de l&apos;utilisation du Service, y compris les
              pertes de ventes dues a des reponses incorrectes du bot.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">10. Contact</h2>
            <p>
              Pour toute question concernant ces conditions :<br />
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
