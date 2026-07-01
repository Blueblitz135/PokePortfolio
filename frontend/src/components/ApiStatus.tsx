interface ApiStatusProps {
  status: "loading" | "online" | "offline";
}

const labels = {
  loading: "Checking API...",
  online: "API online",
  offline: "API unavailable",
};

export function ApiStatus({ status }: ApiStatusProps) {
  return <p className={`api-status api-status--${status}`}>{labels[status]}</p>;
}
