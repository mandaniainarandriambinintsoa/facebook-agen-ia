import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function FinalCTA() {
  return (
    <section className="py-20 md:py-28">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900 px-6 py-16 md:px-16 md:py-20 text-center">
          <div
            aria-hidden
            className="absolute -top-32 -right-32 h-96 w-96 rounded-full bg-amber-500/20 blur-3xl"
          />
          <div
            aria-hidden
            className="absolute -bottom-32 -left-32 h-96 w-96 rounded-full bg-emerald-500/20 blur-3xl"
          />

          <h2 className="relative text-3xl md:text-4xl lg:text-5xl font-bold text-white tracking-tight">
            Lance Valina-Bot sur ta page en 10 minutes
          </h2>
          <p className="relative mt-4 text-lg text-slate-200 max-w-xl mx-auto">
            Pas de carte bancaire, pas d&apos;engagement. Tu testes pendant 7
            jours, tu décides après.
          </p>

          <Button
            asChild
            size="lg"
            className="relative mt-8 bg-amber-500 hover:bg-amber-600 text-white text-base px-8 shadow-xl shadow-amber-500/30"
          >
            <Link href="/login">
              Démarrer l&apos;essai gratuit
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </Button>

          <p className="relative mt-4 text-sm text-slate-300">
            Setup guidé · Support par email · Hébergé en UE
          </p>
        </div>
      </div>
    </section>
  );
}
