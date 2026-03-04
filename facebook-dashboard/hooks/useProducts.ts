import useSWR from "swr";
import { tenantFetcher, tenantApi } from "@/lib/api";
import type { Product } from "@/lib/types";

export function useProducts() {
  const { data, error, isLoading, mutate } = useSWR<Product[]>(
    "/products",
    tenantFetcher
  );

  const updateProduct = async (id: string, product: Partial<Product>) => {
    await tenantApi(`/products/${id}`, {
      method: "PUT",
      body: JSON.stringify(product),
    });
    mutate();
  };

  const deleteProduct = async (id: string) => {
    await tenantApi(`/products/${id}`, { method: "DELETE" });
    mutate();
  };

  const deleteProducts = async (ids: string[]) => {
    await Promise.all(ids.map((id) => tenantApi(`/products/${id}`, { method: "DELETE" })));
    mutate();
  };

  const uploadCatalog = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    await tenantApi("/upload-catalog", {
      method: "POST",
      body: formData,
    });
    mutate();
  };

  return { products: data, error, isLoading, mutate, updateProduct, deleteProduct, deleteProducts, uploadCatalog };
}
