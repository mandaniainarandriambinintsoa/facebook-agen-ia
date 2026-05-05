"use client";

import { useEffect, useState } from "react";
import { DashboardTour } from "./DashboardTour";

/**
 * Wrapper qui gere le mount/unmount du tour :
 * - Auto-mount au 1er arrive sur dashboard (si pas deja fait)
 * - Re-mount sur custom event "valina-tour-start" (declenche par le bouton header)
 */
export function DashboardTourMount() {
  const [mountKey, setMountKey] = useState<number | null>(null);
  const [forceStart, setForceStart] = useState(false);

  useEffect(() => {
    const alreadyDone = localStorage.getItem("valina_tour_done_v1") === "true";
    if (!alreadyDone) {
      // Petit delai pour laisser le DOM se stabiliser (sidebar rendered, data-tour attrs en place)
      const timer = setTimeout(() => {
        setMountKey(Date.now());
        setForceStart(false);
      }, 800);
      return () => clearTimeout(timer);
    }
  }, []);

  useEffect(() => {
    const handler = () => {
      setMountKey(Date.now());
      setForceStart(true);
    };
    window.addEventListener("valina-tour-start", handler);
    return () => window.removeEventListener("valina-tour-start", handler);
  }, []);

  if (mountKey === null) return null;

  return (
    <DashboardTour
      key={mountKey}
      forceStart={forceStart}
      onClose={() => setMountKey(null)}
    />
  );
}
