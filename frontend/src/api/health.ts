/** Backend availability check used by page-level connection states. */
import type { HealthResponse } from "../types/health";

/** Fetch the lightweight health payload or report an offline backend. */
export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch("/api/health");

  if (!response.ok) {
    throw new Error("The API health check failed.");
  }

  return response.json() as Promise<HealthResponse>;
}
