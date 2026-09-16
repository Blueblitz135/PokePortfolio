/** Compact, accessible indicator for backend loading/online/offline state. */
interface ApiStatusProps {
  status: "loading" | "online" | "offline";
}

const labels = {
  loading: "Checking API...",
  online: "API online",
  offline: "API unavailable",
};

/** Render a textual status that does not rely on color alone. */
export function ApiStatus({ status }: ApiStatusProps) {
  return <p className={`api-status api-status--${status}`}>{labels[status]}</p>;
}
