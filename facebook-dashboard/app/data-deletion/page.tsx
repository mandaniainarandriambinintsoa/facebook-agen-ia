import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata = {
  title: "Suppression des donnees - Facebook Agent IA",
};

export default function DataDeletionPage() {
  return (
    <div className="min-h-screen bg-muted/40 p-4 md:p-8">
      <Card className="max-w-3xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl">Demande de suppression des donnees</CardTitle>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none space-y-6">
          <section>
            <h2 className="text-lg font-semibold">Comment supprimer vos donnees</h2>
            <p>
              Conformement au RGPD et aux politiques de Meta, vous pouvez demander la
              suppression de toutes vos donnees associees a Facebook Agent IA, service
              opere par <strong>RANDRIAMBININTSOA MANDANIAINA</strong>, LOT VT 85 HE BIS DB
              ANDOHANIMANDROSEZA, Antananarivo, Analamanga, 101, Madagascar.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">Option 1 : Depuis le tableau de bord</h2>
            <p>
              Connectez-vous au <a href="/" className="underline">tableau de bord</a> et
              utilisez les options de suppression dans chaque section (Produits, Connaissances).
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">Option 2 : Revoquer l&apos;acces</h2>
            <ol className="list-decimal pl-6 space-y-1">
              <li>Allez dans vos <strong>Parametres Facebook</strong></li>
              <li>Cliquez sur <strong>Applications et sites web</strong></li>
              <li>Trouvez <strong>Facebook Agent IA</strong></li>
              <li>Cliquez sur <strong>Supprimer</strong></li>
            </ol>
            <p>Cela revoquera l&apos;acces et nous supprimerons vos donnees sous 30 jours.</p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">Option 3 : Par email</h2>
            <p>
              Envoyez un email a <strong>contact@manda-ia.com</strong> avec
              l&apos;objet &quot;Demande de suppression de donnees&quot; et votre identifiant Facebook.
              Nous traiterons votre demande sous 30 jours.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold">Donnees supprimees</h2>
            <p>La suppression inclut :</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>Votre compte tenant et configuration du bot</li>
              <li>Votre catalogue produits</li>
              <li>Tous les embeddings (base de connaissances)</li>
              <li>L&apos;historique des messages et reponses</li>
              <li>Les tokens d&apos;acces Facebook</li>
            </ul>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
