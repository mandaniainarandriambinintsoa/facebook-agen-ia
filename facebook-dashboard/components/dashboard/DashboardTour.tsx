"use client";

import { useEffect, useRef } from "react";
import type { Driver } from "driver.js";

const TOUR_STORAGE_KEY = "valina_tour_done_v1";

interface DashboardTourProps {
  /**
   * Si true, force le tour a se lancer meme si localStorage marque "done".
   * Utilise par le bouton "Tour guide" dans le header.
   */
  forceStart?: boolean;
  onClose?: () => void;
}

export function DashboardTour({ forceStart = false, onClose }: DashboardTourProps) {
  const driverRef = useRef<Driver | null>(null);

  useEffect(() => {
    let cancelled = false;

    const start = async () => {
      // Dynamic import : driver.js ne supporte pas SSR.
      // CSS importe statiquement dans globals.css.
      const { driver } = await import("driver.js");

      if (cancelled) return;

      const alreadyDone = localStorage.getItem(TOUR_STORAGE_KEY) === "true";
      if (alreadyDone && !forceStart) return;

      const d = driver({
        showProgress: true,
        progressText: "{{current}} / {{total}}",
        nextBtnText: "Suivant →",
        prevBtnText: "← Précédent",
        doneBtnText: "Compris !",
        smoothScroll: true,
        allowClose: true,
        animate: true,
        overlayColor: "rgba(15, 14, 12, 0.65)",
        onDestroyStarted: () => {
          localStorage.setItem(TOUR_STORAGE_KEY, "true");
          d.destroy();
          onClose?.();
        },
        steps: [
          {
            popover: {
              title: "Bienvenue dans ton dashboard",
              description:
                "On va faire un tour rapide en 8 étapes (~1 min). Tu apprendras où trouver tes prospects, tes commandes, ton catalogue et comment configurer le bot.",
            },
          },
          {
            element: '[data-tour="dashboard-home"]',
            popover: {
              title: "Vue d'ensemble",
              description:
                "Tes stats du jour : messages traités, prospects détectés, commandes prises. Tu vois tout en temps réel.",
              side: "bottom",
              align: "start",
            },
          },
          {
            element: '[data-tour="nav-prospects"]',
            popover: {
              title: "Prospects chauds",
              description:
                "Les clients qui ont parlé paiement, livraison ou Mvola. Le bot les détecte automatiquement et tu les rappelles toi-même pour conclure.",
              side: "right",
            },
          },
          {
            element: '[data-tour="nav-orders"]',
            popover: {
              title: "Commandes auto",
              description:
                "Les commandes que le bot a prises tout seul (produit + adresse + paiement). Tu les confirmes et tu prépares les colis.",
              side: "right",
            },
          },
          {
            element: '[data-tour="nav-messages"]',
            popover: {
              title: "Toutes les conversations",
              description:
                "L'historique complet entre tes clients et le bot. Tu peux relire ce qu'il a répondu, ajuster si besoin.",
              side: "right",
            },
          },
          {
            element: '[data-tour="nav-products"]',
            popover: {
              title: "Ton catalogue",
              description:
                "Les produits chargés depuis ton Excel. Tu peux ajouter, modifier, supprimer. Plus c'est précis, mieux le bot répond.",
              side: "right",
            },
          },
          {
            element: '[data-tour="nav-knowledge"]',
            popover: {
              title: "Base de connaissances",
              description:
                "Les embeddings RAG du bot : ce qu'il sait sur ton commerce. Tu peux ré-uploader ton catalogue ici à tout moment.",
              side: "right",
            },
          },
          {
            element: '[data-tour="nav-platforms"]',
            popover: {
              title: "Plateformes connectées",
              description:
                "Ta page Facebook Messenger connectée. Si tu veux brancher une nouvelle page, c'est ici.",
              side: "right",
            },
          },
          {
            element: '[data-tour="nav-config"]',
            popover: {
              title: "Configuration du bot",
              description:
                "Custom prompt, ton, message d'accueil, auto-reply commentaires. Tout ce qui personnalise le bot à ta marque.",
              side: "right",
            },
          },
          {
            element: '[data-tour="nav-onboarding"]',
            popover: {
              title: "Refaire la configuration",
              description:
                "Tu peux relancer l'assistant de configuration en 5 étapes à tout moment depuis ici.",
              side: "right",
            },
          },
          {
            element: '[data-tour="header-help"]',
            popover: {
              title: "Besoin de revoir le tour ?",
              description:
                "Clique sur ce bouton à tout moment pour relancer ce tour guidé. À toi de jouer 👋",
              side: "bottom",
              align: "end",
            },
          },
        ],
      });

      driverRef.current = d;
      d.drive();
    };

    start();

    return () => {
      cancelled = true;
      if (driverRef.current) {
        try {
          driverRef.current.destroy();
        } catch {
          // ignore
        }
      }
    };
  }, [forceStart, onClose]);

  return null;
}

/**
 * Trigger le tour manuellement depuis n'importe où.
 * Utilise un custom event window.
 */
export function triggerDashboardTour() {
  window.dispatchEvent(new CustomEvent("valina-tour-start"));
}
