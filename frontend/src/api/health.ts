import type { HealthResponse } from "../types/health";

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch("/api/health");

  if (!response.ok) {
    throw new Error("The API health check failed.");
  }

  return response.json() as Promise<HealthResponse>;
}
