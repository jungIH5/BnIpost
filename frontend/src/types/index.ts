export interface User {
  id: number;
  email: string;
  nickname: string;
  profileImage?: string;
  provider: "NAVER" | "INSTAGRAM";
  hasNaverToken: boolean;
  hasInstagramToken: boolean;
}

export interface PostResult {
  success: boolean;
  post_history_id?: number;
  published_url?: string;
  generated_title?: string;
  generated_content?: string;
  generated_hashtags?: string[];
  error?: string;
}

export interface HistoryItem {
  id: number;
  platform: "naver" | "instagram";
  input_type: "keyword" | "image";
  input_keyword?: string;
  generated_title?: string;
  generated_content?: string;
  generated_hashtags?: string[];
  published_url?: string;
  status: "pending" | "processing" | "published" | "failed";
  retry_count: number;
  error_message?: string;
  created_at?: string;
}

export type Platform = "naver" | "instagram";
