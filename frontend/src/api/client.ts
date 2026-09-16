/** Shared JSON request helpers and normalized API error handling. */

/** Extract FastAPI string/list validation details with a status fallback. */
async function getErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };

    if (typeof body.detail === "string") {
      return body.detail;
    }

    if (Array.isArray(body.detail)) {
      const messages = body.detail
        .map((item) => {
          if (
            typeof item === "object" &&
            item !== null &&
            "msg" in item &&
            typeof item.msg === "string"
          ) {
            return item.msg;
          }
          return null;
        })
        .filter((message): message is string => message !== null);

      if (messages.length > 0) {
        return messages.join(" ");
      }
    }
  } catch {
    // Use the status-based fallback when the response does not contain JSON.
  }

  return `The request failed with status ${response.status}.`;
}

export class ApiError extends Error {
  /** HTTP failure that preserves status for workflow-specific recovery. */
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** Execute a request, throw a normalized error, and decode its JSON body. */
export async function requestJson<T>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(url, options);

  if (!response.ok) {
    throw new ApiError(await getErrorMessage(response), response.status);
  }

  return response.json() as Promise<T>;
}

/** Execute a request whose successful response intentionally has no body. */
export async function requestNoContent(
  url: string,
  options?: RequestInit,
): Promise<void> {
  const response = await fetch(url, options);

  if (!response.ok) {
    throw new ApiError(await getErrorMessage(response), response.status);
  }
}
