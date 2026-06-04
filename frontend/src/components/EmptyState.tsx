import { Link } from "react-router-dom";

type EmptyStateProps = {
  title: string;
  description?: string;
  actionHref?: string;
  actionLabel?: string;
};

export function EmptyState({ title, description, actionHref, actionLabel }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      {description ? <p>{description}</p> : null}
      {actionHref && actionLabel ? (
        <div className="state-actions">
          <Link className="button-link" to={actionHref}>
            {actionLabel}
          </Link>
        </div>
      ) : null}
    </div>
  );
}

export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="empty-state loading-state" aria-live="polite">
      <span className="loading-dot" aria-hidden="true" />
      <strong>{label}</strong>
    </div>
  );
}

export function ErrorState({
  title = "Something went wrong",
  description = "Refresh the page or try again in a moment.",
}: {
  title?: string;
  description?: string;
}) {
  return <EmptyState title={title} description={description} />;
}
