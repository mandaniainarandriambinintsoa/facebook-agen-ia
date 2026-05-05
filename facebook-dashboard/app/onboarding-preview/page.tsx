import { OnboardingFlow } from "@/components/onboarding/OnboardingFlow";

export const metadata = {
  title: "Onboarding · Preview · Valina-Bot",
  robots: "noindex, nofollow",
};

export default function OnboardingPreviewPage() {
  return <OnboardingFlow previewMode />;
}
