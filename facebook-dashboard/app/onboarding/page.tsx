import { OnboardingFlow } from "@/components/onboarding/OnboardingFlow";

export const metadata = {
  title: "Configuration · Valina-Bot",
  description: "Active Valina-Bot sur ta page Messenger en cinq étapes.",
};

export default function OnboardingPage() {
  return <OnboardingFlow />;
}
