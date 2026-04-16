export interface Tenant {
  id: number;
  page_id: string;
  page_name: string;
  created_at: string;
}

export interface Stats {
  messages_today: number;
  messages_total: number;
  avg_confidence: number;
  products_count: number;
  prospects_today: number;
  prospects_total: number;
  prospects_new: number;
  orders_today: number;
  orders_total: number;
  orders_pending: number;
  conversion_rate: number;
}

export interface ChartPoint {
  date: string;
  count: number;
}

export interface Message {
  id: string;
  sender_id: string;
  message_text: string;
  response_text: string;
  confidence_level: string;
  confidence_score: number;
  channel: string;
  created_at: string;
}

export interface PaginatedMessages {
  messages: Message[];
  total: number;
  limit: number;
  offset: number;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  price: string;
  category: string;
  sizes?: string;
  colors?: string;
  stock_status?: string;
  image_url?: string | null;
}

export interface KnowledgeStats {
  embeddings_count: number;
  products_count: number;
  uploads: Upload[];
}

export interface Upload {
  id: number;
  filename: string;
  products_count: number;
  created_at: string;
}

export interface BotConfig {
  welcome_message: string;
  bot_type: string;
  delivery_enabled: boolean;
  phone_numbers: string;
  custom_system_prompt: string;
}

export interface PublicConfig {
  facebook_app_id: string;
  oauth_login_url: string;
}

export interface TenantPlatform {
  id: string;
  platform: "messenger" | "instagram" | "whatsapp";
  platform_id: string;
  platform_name: string;
  is_active: boolean;
  created_at: string | null;
}
