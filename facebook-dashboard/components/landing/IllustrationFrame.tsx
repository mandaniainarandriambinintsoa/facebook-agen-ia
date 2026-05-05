"use client";

import Image from "next/image";
import { useState } from "react";

/**
 * Frame pour les illustrations line-art editoriales.
 * Affiche l'image si disponible, sinon un placeholder visuel guidé
 * pour que Manda sache où poser le fichier.
 */
interface IllustrationFrameProps {
  src: string;
  alt: string;
  caption?: string;
  width?: number;
  height?: number;
  className?: string;
}

export function IllustrationFrame({
  src,
  alt,
  caption,
  width = 600,
  height = 480,
  className,
}: IllustrationFrameProps) {
  const [error, setError] = useState(false);

  return (
    <figure className={`relative ${className || ""}`}>
      <div
        className="relative rounded-3xl overflow-hidden bg-[#F0F2F5]"
        style={{ aspectRatio: `${width}/${height}` }}
      >
        {!error ? (
          <Image
            src={src}
            alt={alt}
            fill
            className="object-cover"
            onError={() => setError(true)}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center p-8">
            <div className="text-center">
              <div className="font-mono text-[10px] uppercase tracking-widest text-[#1C1E21]/40 mb-3">
                Illustration manquante
              </div>
              <div className="text-lg text-[#1C1E21]/60 mb-2 italic">
                {alt}
              </div>
              <div className="font-mono text-xs text-[#1C1E21]/40 break-all">
                {src}
              </div>
            </div>
          </div>
        )}
      </div>
      {caption && (
        <figcaption className="mt-3 text-center italic text-sm text-[#1C1E21]/60">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}
