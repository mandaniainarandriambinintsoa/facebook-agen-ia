"use client";

import { useRef, useState } from "react";
import { ArrowRight, ArrowLeft, Upload, FileSpreadsheet, Check, AlertCircle } from "lucide-react";
import { useProducts } from "@/hooks/useProducts";

interface Step4Props {
  onBack: () => void;
  onNext: () => void;
}

export function Step4Catalog({ onBack, onNext }: Step4Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploaded, setUploaded] = useState(false);
  const { products, uploadCatalog } = useProducts();

  const handleFile = async (file: File) => {
    setUploadError(null);
    setUploading(true);
    try {
      await uploadCatalog(file);
      setUploaded(true);
    } catch (e) {
      setUploadError(
        e instanceof Error
          ? e.message
          : "Erreur lors de l'upload. Vérifie le format du fichier (Excel ou CSV)."
      );
    } finally {
      setUploading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const productCount = products?.length || 0;
  const hasProducts = productCount > 0;

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-10">
        <span className="font-mono text-xs text-[#B7481E] uppercase tracking-widest mb-4 block">
          03 — Catalogue
        </span>
        <h2 className="font-display text-3xl md:text-5xl text-[#1A1614] tracking-tight leading-[1.05] mb-4">
          Apprends ton{" "}
          <span className="italic text-[#B7481E]">catalogue</span>
          <br />
          au bot
        </h2>
        <p className="text-[#1A1614]/70 leading-relaxed">
          Excel ou CSV avec colonnes : nom, prix, description, image_url, tailles, couleurs.
        </p>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`rounded-2xl border-2 border-dashed p-10 cursor-pointer transition-all ${
          uploaded
            ? "border-[#2D4A3E] bg-[#2D4A3E]/5"
            : uploadError
            ? "border-[#B7481E] bg-[#B7481E]/5"
            : "border-[#1A1614]/25 bg-[#FBF6EE] hover:border-[#B7481E] hover:bg-[#FBF6EE]/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          className="hidden"
          onChange={handleChange}
        />

        <div className="flex flex-col items-center text-center">
          {uploaded ? (
            <>
              <div className="h-14 w-14 rounded-full bg-[#2D4A3E] text-[#FBF6EE] flex items-center justify-center mb-4">
                <Check className="h-6 w-6" />
              </div>
              <h3 className="font-display text-2xl text-[#2D4A3E] mb-2">
                {productCount} produits chargés
              </h3>
              <p className="text-[#1A1614]/70 text-sm">
                Le bot connaît maintenant ton catalogue. Tu peux re-uploader pour mettre à jour.
              </p>
            </>
          ) : uploading ? (
            <>
              <div className="h-14 w-14 rounded-full bg-[#1A1614]/10 flex items-center justify-center mb-4 animate-pulse">
                <Upload className="h-6 w-6 text-[#1A1614]/60" />
              </div>
              <h3 className="font-display text-2xl text-[#1A1614] mb-2">
                Apprentissage en cours...
              </h3>
              <p className="text-[#1A1614]/70 text-sm">
                On lit ton fichier et on génère les embeddings. ~30 secondes.
              </p>
            </>
          ) : uploadError ? (
            <>
              <div className="h-14 w-14 rounded-full bg-[#B7481E]/10 flex items-center justify-center mb-4">
                <AlertCircle className="h-6 w-6 text-[#B7481E]" />
              </div>
              <h3 className="font-display text-2xl text-[#B7481E] mb-2">
                Erreur d&apos;upload
              </h3>
              <p className="text-[#1A1614]/70 text-sm max-w-md">{uploadError}</p>
              <p className="mt-4 text-xs text-[#1A1614]/50 underline">
                Clique pour réessayer
              </p>
            </>
          ) : (
            <>
              <div className="h-14 w-14 rounded-full bg-[#F5E9D9] flex items-center justify-center mb-4">
                <FileSpreadsheet className="h-6 w-6 text-[#B7481E]" />
              </div>
              <h3 className="font-display text-2xl text-[#1A1614] mb-2">
                Glisse ton fichier ici
              </h3>
              <p className="text-[#1A1614]/70 text-sm mb-2">
                ou clique pour choisir
              </p>
              <p className="font-mono text-xs text-[#1A1614]/40 uppercase tracking-widest">
                .xlsx · .xls · .csv
              </p>
            </>
          )}
        </div>
      </div>

      <details className="mt-6 text-sm text-[#1A1614]/70">
        <summary className="cursor-pointer hover:text-[#1A1614] font-medium">
          Quelles colonnes mettre dans mon Excel ?
        </summary>
        <div className="mt-4 p-5 bg-[#F5E9D9] rounded-xl text-xs leading-relaxed">
          <p className="mb-3 text-[#1A1614]">
            <strong>Obligatoires</strong> : <code>nom</code> et <code>prix</code>
          </p>
          <p className="mb-3 text-[#1A1614]">
            <strong>Recommandées</strong> : <code>description</code>, <code>image_url</code>, <code>category</code>, <code>tailles</code>, <code>couleurs</code>, <code>stock</code>
          </p>
          <p className="text-[#1A1614]/70">
            Plus ton catalogue est précis, mieux le bot répond aux questions clients (taille,
            dispo, photo). Les noms de colonnes sont insensibles à la casse.
          </p>
        </div>
      </details>

      <div className="flex items-center justify-between pt-8 mt-8 border-t border-[#1A1614]/10">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 text-[#1A1614]/70 hover:text-[#1A1614] text-sm"
        >
          <ArrowLeft className="h-4 w-4" />
          Précédent
        </button>

        <div className="flex items-center gap-4">
          {!hasProducts && (
            <button
              onClick={onNext}
              className="text-[#1A1614]/60 hover:text-[#1A1614] underline underline-offset-4 decoration-[#1A1614]/30 text-sm"
            >
              Passer pour l&apos;instant
            </button>
          )}
          <button
            onClick={onNext}
            disabled={uploading}
            className="group inline-flex items-center gap-3 rounded-full bg-[#1A1614] text-[#FBF6EE] pl-6 pr-2 py-2 text-base font-medium hover:bg-[#B7481E] transition-all disabled:opacity-30"
          >
            {hasProducts ? "Tester le bot" : "Suivant"}
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#F4B83A] text-[#1A1614] group-hover:translate-x-0.5 transition-transform">
              <ArrowRight className="h-4 w-4" />
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
