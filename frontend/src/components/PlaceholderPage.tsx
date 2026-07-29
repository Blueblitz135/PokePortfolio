interface PlaceholderPageProps {
  eyebrow: string;
  title: string;
  description: string;
  message: string;
}

export function PlaceholderPage({
  eyebrow,
  title,
  description,
  message,
}: PlaceholderPageProps) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          <p className="intro">{description}</p>
        </div>
      </header>

      <section className="panel placeholder-panel">
        <h2>Coming in a later ticket</h2>
        <p>{message}</p>
      </section>
    </div>
  );
}
