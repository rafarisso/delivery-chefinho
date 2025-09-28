import axios, { AxiosError, AxiosRequestConfig } from "axios";

const baseURL = (import.meta.env.VITE_API_URL || "http://localhost:8000/api").replace(/\/$/, "");

export const api = axios.create({
  baseURL,
});

type AuthHeaders = {
  Authorization: string;
};

function withAuth(token?: string | null): Partial<AuthHeaders> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function extractErrorMessage(error: AxiosError): string {
  const data = error.response?.data as { detail?: unknown } | undefined;
  if (data?.detail) {
    if (typeof data.detail === "string") {
      return data.detail;
    }
    if (Array.isArray(data.detail)) {
      const [first] = data.detail;
      if (first && typeof first === "object" && "msg" in first) {
        const message = (first as { msg?: unknown }).msg;
        if (typeof message === "string") {
          return message;
        }
      }
    }
  }
  return error.message;
}

async function request<T>(config: AxiosRequestConfig): Promise<T> {
  try {
    const response = await api.request<T>(config);
    return response.data;
  } catch (err) {
    if (axios.isAxiosError(err)) {
      throw new Error(extractErrorMessage(err));
    }
    throw err;
  }
}

export interface Expense {
  id: number;
  date: string;
  amount: string;
  partner_name: "Rafael" | "Guilherme";
  platform?: string | null;
  category?: string | null;
  note?: string | null;
  receipt_url?: string | null;
  created_at: string;
}

export interface Settlement {
  id: number;
  payout_id: number;
  created_at: string;
  week_start: string;
  week_end: string;
  reimb_rafael: string;
  reimb_guilherme: string;
  net_for_split: string;
  share_rafael: string;
  share_guilherme: string;
  total_rafael: string;
  total_guilherme: string;
  rent_fee: string;
  income_total: string;
}

export interface CloseWeekPayload {
  week_end: string;
  ifood_amount: number;
  ninety9_amount: number;
  rent_fee?: number;
  rule?: "rent_before_split" | "rent_after_split";
}

export function loginRequest(email: string, password: string) {
  return request<{ access_token: string }>({
    method: "POST",
    url: "/auth/login",
    data: { email, password },
  });
}

export function listExpenses(
  token: string,
  params?: { start?: string; end?: string; partner_name?: string }
) {
  return request<Expense[]>({
    method: "GET",
    url: "/expenses",
    headers: withAuth(token),
    params,
  });
}

export function createExpenseRequest(
  token: string,
  data: {
    amount: number;
    date: string;
    partner_name: "Rafael" | "Guilherme";
    platform?: string;
    category?: string;
    note?: string;
    file: File;
  }
) {
  const formData = new FormData();
  formData.append("file", data.file);
  formData.append("amount", data.amount.toString());
  formData.append("date_value", data.date);
  formData.append("partner_name", data.partner_name);
  if (data.platform) formData.append("platform", data.platform);
  if (data.category) formData.append("category", data.category);
  if (data.note) formData.append("note", data.note);

  return request<Expense>({
    method: "POST",
    url: "/expenses",
    data: formData,
    headers: withAuth(token),
  });
}

export function closeWeek(token: string, payload: CloseWeekPayload) {
  return request<Settlement>({
    method: "POST",
    url: "/payouts/close_week",
    data: payload,
    headers: withAuth(token),
  });
}

export function fetchSettlement(token: string, id: number) {
  return request<Settlement>({
    method: "GET",
    url: `/settlements/${id}`,
    headers: withAuth(token),
  });
}

export function listSettlements(token: string) {
  return request<Settlement[]>({
    method: "GET",
    url: "/reports/settlements",
    headers: withAuth(token),
  });
}

export function downloadWeeklyCsv(token: string, weekEnd: string) {
  return request<Blob>({
    method: "GET",
    url: "/reports/weekly.csv",
    headers: withAuth(token),
    responseType: "blob",
    params: { week_end: weekEnd },
  });
}

export function downloadWeeklyPdf(token: string, weekEnd: string) {
  return request<Blob>({
    method: "GET",
    url: "/reports/weekly.pdf",
    headers: withAuth(token),
    responseType: "blob",
    params: { week_end: weekEnd },
  });
}
