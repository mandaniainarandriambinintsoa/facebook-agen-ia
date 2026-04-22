"""
Upload catalogue Excel/CSV + gestion des produits
"""

import uuid
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.db import crud
from app.db.models import Tenant
from app.auth.dependencies import get_current_tenant
from app.rag.pg_retriever import PgVectorRetriever

router = APIRouter(prefix="/api/tenants", tags=["Catalog"])


# ─── Schemas ───────────────────────────────────────────────

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None
    sizes: Optional[str] = None
    colors: Optional[str] = None
    stock_status: Optional[str] = None


# ─── Column detection ─────────────────────────────────────

COLUMN_MAPPING = {
    "name": ["nom", "name", "produit", "product", "titre", "title", "designation", "article"],
    "description": ["description", "desc", "details", "detail"],
    "price": ["prix", "price", "tarif", "cout", "cost", "montant"],
    "category": ["categorie", "category", "cat", "type", "famille"],
    "sizes": ["taille", "tailles", "size", "sizes", "pointure"],
    "colors": ["couleur", "couleurs", "color", "colors"],
    "stock_status": ["stock", "disponibilite", "dispo", "status", "statut", "availability"],
    "image_url": ["image", "image_url", "photo", "photo_url", "img", "url_image", "lien_image"],
}


def _detect_columns(headers: list[str]) -> dict[str, int]:
    """Detecte automatiquement le mapping colonnes → champs"""
    mapping = {}
    headers_lower = [h.strip().lower() for h in headers]

    for field, aliases in COLUMN_MAPPING.items():
        for i, header in enumerate(headers_lower):
            if header in aliases:
                mapping[field] = i
                break

    return mapping


def _product_to_text(product_data: dict) -> str:
    """Convertit un produit en texte pour l'embedding"""
    parts = []
    if product_data.get("name"):
        parts.append(f"Produit: {product_data['name']}")
    if product_data.get("category"):
        parts.append(f"Categorie: {product_data['category']}")
    if product_data.get("description"):
        parts.append(f"Description: {product_data['description']}")
    if product_data.get("price"):
        parts.append(f"Prix: {product_data['price']}")
    if product_data.get("sizes"):
        parts.append(f"Tailles: {product_data['sizes']}")
    if product_data.get("colors"):
        parts.append(f"Couleurs: {product_data['colors']}")
    if product_data.get("stock_status"):
        parts.append(f"Disponibilite: {product_data['stock_status']}")
    return "\n".join(parts)


# ─── Endpoints ─────────────────────────────────────────────

@router.post("/{tenant_id}/upload-catalog")
async def upload_catalog(
    tenant_id: str,
    file: UploadFile = File(...),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Upload un fichier Excel/CSV, parse les produits, genere les embeddings"""
    # Verifier que le tenant_id correspond
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    filename = file.filename.lower()
    if not (filename.endswith(".xlsx") or filename.endswith(".csv")):
        raise HTTPException(status_code=400, detail="Format supporte: .xlsx ou .csv")

    content = await file.read()
    products_data = []

    try:
        if filename.endswith(".xlsx"):
            products_data = _parse_xlsx(content)
        else:
            products_data = _parse_csv(content)
    except Exception as e:
        logger.error(f"Erreur parsing fichier: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur lecture fichier: {str(e)}")

    if not products_data:
        raise HTTPException(status_code=400, detail="Aucun produit trouve dans le fichier")

    # Supprimer les anciens produits et embeddings
    await crud.delete_tenant_products(db, tenant.id)
    await crud.delete_tenant_embeddings(db, tenant.id)

    # Inserer les nouveaux produits
    await crud.create_products(db, tenant.id, products_data)

    # Generer les embeddings
    texts = [_product_to_text(p) for p in products_data]
    metadatas = [
        {
            "source": "catalog",
            "product_name": p.get("name", ""),
            "image_url": p.get("image_url", "") or "",
        }
        for p in products_data
    ]

    retriever = PgVectorRetriever(tenant_id=tenant.id, db=db)
    await retriever.add_documents(texts, metadatas)

    # Log l'upload
    await crud.create_upload(db, tenant.id, file.filename, len(products_data))

    logger.info(f"Catalogue uploade pour {tenant.page_name}: {len(products_data)} produits")

    return {
        "status": "success",
        "products_count": len(products_data),
        "embeddings_count": len(texts),
        "filename": file.filename,
    }


@router.get("/{tenant_id}/products")
async def list_products(
    tenant_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Liste les produits du tenant"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    products = await crud.get_products(db, tenant.id)
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "category": p.category,
            "sizes": p.sizes,
            "colors": p.colors,
            "stock_status": p.stock_status,
            "image_url": p.image_url,
        }
        for p in products
    ]


@router.put("/{tenant_id}/products/{product_id}")
async def update_product(
    tenant_id: str,
    product_id: str,
    data: ProductUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Modifie un produit"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    product = await crud.get_product_by_id(db, uuid.UUID(product_id))
    if not product or product.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Produit non trouve")

    updates = data.model_dump(exclude_unset=True)
    updated = await crud.update_product(db, product, **updates)

    return {
        "id": str(updated.id),
        "name": updated.name,
        "description": updated.description,
        "price": updated.price,
        "category": updated.category,
    }


@router.delete("/{tenant_id}/products/{product_id}")
async def delete_product(
    tenant_id: str,
    product_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Supprime un produit"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    product = await crud.get_product_by_id(db, uuid.UUID(product_id))
    if not product or product.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Produit non trouve")

    await crud.delete_product(db, product)
    return {"status": "deleted"}


@router.post("/{tenant_id}/reindex")
async def reindex_products(
    tenant_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Re-genere tous les embeddings a partir des produits"""
    if str(tenant.id) != tenant_id:
        raise HTTPException(status_code=403, detail="Acces refuse")

    # Supprimer les anciens embeddings
    await crud.delete_tenant_embeddings(db, tenant.id)

    # Recharger les produits
    products = await crud.get_products(db, tenant.id)
    if not products:
        return {"status": "no_products", "embeddings_count": 0}

    texts = [_product_to_text({
        "name": p.name, "description": p.description, "price": p.price,
        "category": p.category, "sizes": p.sizes, "colors": p.colors,
        "stock_status": p.stock_status,
    }) for p in products]
    metadatas = [
        {
            "source": "catalog",
            "product_name": p.name,
            "image_url": p.image_url or "",
        }
        for p in products
    ]

    retriever = PgVectorRetriever(tenant_id=tenant.id, db=db)
    await retriever.add_documents(texts, metadatas)

    return {"status": "reindexed", "embeddings_count": len(texts)}


# ─── Parsing helpers ──────────────────────────────────────

def _parse_xlsx(content: bytes) -> list[dict]:
    """Parse un fichier Excel"""
    from openpyxl import load_workbook

    wb = load_workbook(io.BytesIO(content), read_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        return []

    headers = [str(h) if h else "" for h in rows[0]]
    col_map = _detect_columns(headers)

    if "name" not in col_map:
        # Fallback: premiere colonne = nom
        col_map["name"] = 0

    products = []
    for row in rows[1:]:
        if not row or not any(row):
            continue

        product = {}
        for field, col_idx in col_map.items():
            if col_idx < len(row) and row[col_idx] is not None:
                product[field] = str(row[col_idx]).strip()
            else:
                product[field] = ""

        if product.get("name"):
            products.append(product)

    wb.close()
    return products


def _parse_csv(content: bytes) -> list[dict]:
    """Parse un fichier CSV"""
    import csv

    text = content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    if len(rows) < 2:
        return []

    headers = rows[0]
    col_map = _detect_columns(headers)

    if "name" not in col_map:
        col_map["name"] = 0

    products = []
    for row in rows[1:]:
        if not row or not any(row):
            continue

        product = {}
        for field, col_idx in col_map.items():
            if col_idx < len(row):
                product[field] = row[col_idx].strip()
            else:
                product[field] = ""

        if product.get("name"):
            products.append(product)

    return products
