import useSWR from "swr";
import { tenantFetcher, tenantApi } from "@/lib/api";

interface Order {
  id: string;
  sender_id: string;
  customer_name: string;
  customer_phone: string;
  customer_address: string;
  channel: string;
  items: { product_name: string; quantity: number; price: string }[];
  total_amount: string;
  payment_method: string;
  status: string;
  notes: string;
  created_at: string;
}

interface OrdersResponse {
  total: number;
  orders: Order[];
}

interface OrdersStats {
  today: number;
  total: number;
  by_status: {
    pending: number;
    confirmed: number;
    delivered: number;
    cancelled: number;
  };
  conversion_rate: number;
  per_day: { date: string; count: number }[];
}

export function useOrders(status?: string) {
  const params = status ? `?status=${status}` : "";
  const { data, error, isLoading, mutate } = useSWR<OrdersResponse>(
    `/orders${params}`,
    tenantFetcher
  );
  return { orders: data, error, isLoading, mutate };
}

export function useOrdersStats() {
  const { data, error, isLoading } = useSWR<OrdersStats>(
    "/orders/stats",
    tenantFetcher
  );
  return { stats: data, error, isLoading };
}

export async function updateOrderStatus(
  orderId: string,
  status: string,
  notes?: string
) {
  return tenantApi(`/orders/${orderId}`, {
    method: "PUT",
    body: JSON.stringify({ status, notes }),
  });
}
