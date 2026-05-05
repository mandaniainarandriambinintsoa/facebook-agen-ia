"use client";

import { useRef, useState } from "react";
import { ArrowRight, ArrowLeft, Upload, FileSpreadsheet, Check, AlertCircle } from "lucide-react";
import { useProducts } from "@/hooks/useProducts";

interface Step4Props {
  onBack: () => void;
  onNext: () => void;
  previewMode?: boolean;
}

export function Step4Catalog({ onBack, onNext, previewMode = false }: Step4Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploaded, setUploaded] = useState(false);
  const { products, uploadCatalog } = useProducts();

  const handleFile = async (file: File) => {
    setUploadError(null);
    setUploading(true);
    try {
      if (previewMode) {
        await new Promise((r) => setTimeout(r, 1200));
        setUploaded(true);
        return;
      }
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

  const productCount = previewMode ? (uploaded ? 12 : 0) : products?.length || 0;
  const hasProducts = productCount > 0;

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-10">
        <span className="font-mono text-xs text-[#1877F2] uppercase tracking-widest mb-4 block">
          03 — Catalogue
        </span>
        <h2 className="text-3xl md:text-5xl text-[#1C1E21] tracking-tight leading-[1.05] mb-4">
          Apprends ton{" "}
          <span className="italic text-[#1877F2]">catalogue</span>
          <br />
          au bot
        </h2>
        <p className="text-[#1C1E21]/70 leading-relaxed">
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
            ? "border-[#16A34A] bg-[#16A34A]/5"
            : uploadError
            ? "border-[#1877F2] bg-[#1877F2]/5"
            : "border-[#1C1E21]/25 bg-[#F7F8FA] hover:border-[#1877F2] hover:bg-[#F7F8FA]/50"
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
              <div className="h-14 w-14 rounded-full bg-[#16A34A] text-[#F7F8FA] flex items-center justify-center mb-4">
                <Check className="h-6 w-6" />
              </div>
              <h3 className="text-2xl text-[#16A34A] mb-2">
                {productCount} produits chargés
              </h3>
              <p className="text-[#1C1E21]/70 text-sm">
                Le bot connaît maintenant ton catalogue. Tu peux re-uploader pour mettre à jour.
              </p>
            </>
          ) : uploading ? (
            <>
              <div className="h-14 w-14 rounded-full bg-[#1C1E21]/10 flex items-center justify-center mb-4 animate-pulse">
                <Upload className="h-6 w-6 text-[#1C1E21]/60" />
              </div>
              <h3 className="text-2xl text-[#1C1E21] mb-2">
                Apprentissage en cours...
              </h3>
              <p className="text-[#1C1E21]/70 text-sm">
                On lit ton fichier et on génère les embeddings. ~30 secondes.
              </p>
            </>
          ) : uploadError ? (
            <>
              <div className="h-14 w-14 rounded-full bg-[#1877F2]/10 flex items-center justify-center mb-4">
                <AlertCircle className="h-6 w-6 text-[#1877F2]" />
              </div>
              <h3 className="text-2xl text-[#1877F2] mb-2">
                Erreur d&apos;upload
              </h3>
              <p className="text-[#1C1E21]/70 text-sm max-w-md">{uploadError}</p>
              <p className="mt-4 text-xs text-[#1C1E21]/50 underline">
                Clique pour réessayer
              </p>
            </>
          ) : (
            <>
              <div className="h-14 w-14 rounded-full bg-[#F0F2F5] flex items-center justify-center mb-4">
                <FileSpreadsheet className="h-6 w-6 text-[#1877F2]" />
              </div>
              <h3 className="text-2xl text-[#1C1E21] mb-2">
                Glisse ton fichier ici
              </h3>
              <p className="text-[#1C1E21]/70 text-sm mb-2">
                ou clique pour choisir
              </p>
              <p className="font-mono text-xs text-[#1C1E21]/40 uppercase tracking-widest">
                .xlsx · .xls · .csv
              </p>
            </>
          )}
        </div>
      </div>

      <details className="mt-6 text-sm text-[#1C1E21]/70">
        <summary className="cursor-pointer hover:text-[#1C1E21] font-medium">
          Quelles colonnes mettre dans mon Excel ?
        </summary>
        <div className="mt-4 p-5 bg-[#F0F2F5] rounded-xl text-xs leading-relaxed">
          <p className="mb-3 text-[#1C1E21]">
            <strong>Obligatoires</strong> : <code>nom</code> et <code>prix</code>
          </p>
          <p className="mb-3 text-[#1C1E21]">
            <strong>Recommandées</strong> : <code>description</code>, <code>image_url</code>, <code>category</code>, <code>tailles</code>, <code>couleurs</code>, <code>stock</code>
          </p>
          <p className="text-[#1C1E21]/70">
            Plus ton catalogue est précis, mieux le bot répond aux questions clients (taille,
            dispo, photo). Les noms de colonnes sont insensibles à la casse.
          </p>
        </div>
      </details>

      <div className="flex items-center justify-between pt-8 mt-8 border-t border-[#1C1E21]/10">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 text-[#1C1E21]/70 hover:text-[#1C1E21] text-sm"
        >
          <ArrowLeft className="h-4 w-4" />
          Précédent
        </button>

        <div className="flex items-center gap-4">
          {!hasProducts && (
            <button
              onClick={onNext}
              className="text-[#1C1E21]/60 hover:text-[#1C1E21] underline underline-offset-4 decoration-[#1C1E21]/30 text-sm"
            >
              Passer pour l&apos;instant
            </button>
          )}
          <button
            onClick={onNext}
            disabled={uploading}
            className="group inline-flex items-center gap-3 rounded-full bg-[#1C1E21] text-[#F7F8FA] pl-6 pr-2 py-2 text-base font-medium hover:bg-[#1877F2] transition-all disabled:opacity-30"
          >
            {hasProducts ? "Tester le bot" : "Suivant"}
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#F4B83A] text-[#1C1E21] group-hover:translate-x-0.5 transition-transform">
              <ArrowRight className="h-4 w-4" />
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
