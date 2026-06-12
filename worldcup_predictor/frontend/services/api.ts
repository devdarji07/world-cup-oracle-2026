const API = process.env.NEXT_PUBLIC_API_URL || "https://world-cup-oracle-2026-1.onrender.com";
export async function api<T>(path:string, options?:RequestInit):Promise<T> {
  const response = await fetch(`${API}${path}`, { cache:"no-store", ...options });
  if (!response.ok) throw new Error(`Oracle API returned ${response.status}`);
  return response.json();
}
