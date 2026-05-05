import { LandingHeader } from "@/components/landing/Header";
import { Hero } from "@/components/landing/Hero";
import { TrustLogos } from "@/components/landing/TrustLogos";
import { Pillars } from "@/components/landing/Pillars";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Features } from "@/components/landing/Features";
import { Pricing } from "@/components/landing/Pricing";
import { FAQ } from "@/components/landing/FAQ";
import { FinalCTA } from "@/components/landing/FinalCTA";
import { LandingFooter } from "@/components/landing/Footer";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white text-slate-900">
      <LandingHeader />
      <Hero />
      <TrustLogos />
      <Pillars />
      <HowItWorks />
      <Features />
      <Pricing />
      <FAQ />
      <FinalCTA />
      <LandingFooter />
    </main>
  );
}
