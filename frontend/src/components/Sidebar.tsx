import type { RefObject } from "react";
import { Link, useLocation } from "react-router-dom";

type SidebarIconName = "collection" | "search" | "settings";

interface SidebarProps {
  isCollapsed: boolean;
  isMobile: boolean;
  isMobileOpen: boolean;
  sidebarRef: RefObject<HTMLElement | null>;
  closeButtonRef: RefObject<HTMLButtonElement | null>;
  onToggleCollapse: () => void;
  onCloseMobile: () => void;
}

const NAV_ITEMS: ReadonlyArray<{
  to: string;
  label: string;
  icon: SidebarIconName;
}> = [
  { to: "/collection", label: "Collection", icon: "collection" },
  { to: "/search", label: "Search", icon: "search" },
  { to: "/settings", label: "Settings", icon: "settings" },
];

function SidebarIcon({ name }: { name: SidebarIconName }) {
  if (name === "collection") {
    return (
      <svg
        className="sidebar-nav-icon"
        viewBox="0 0 24 24"
        aria-hidden="true"
        focusable="false"
      >
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </svg>
    );
  }

  if (name === "search") {
    return (
      <svg
        className="sidebar-nav-icon"
        viewBox="0 0 24 24"
        aria-hidden="true"
        focusable="false"
      >
        <circle cx="10.5" cy="10.5" r="6.5" />
        <path d="m15.5 15.5 5 5" />
      </svg>
    );
  }

  return (
    <svg
      className="sidebar-nav-icon"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <circle cx="12" cy="12" r="3.25" />
      <path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M18.7 5.3l-2.1 2.1M7.4 16.6l-2.1 2.1" />
    </svg>
  );
}

export function Sidebar({
  isCollapsed,
  isMobile,
  isMobileOpen,
  sidebarRef,
  closeButtonRef,
  onToggleCollapse,
  onCloseMobile,
}: SidebarProps) {
  const location = useLocation();
  const showFullSidebar = isMobile || !isCollapsed;

  function isCurrentNavigationItem(path: string) {
    if (path === "/collection") {
      return (
        location.pathname === path ||
        location.pathname === "/sealed-products" ||
        location.pathname.startsWith("/assets/")
      );
    }

    return location.pathname === path;
  }

  return (
    <aside
      className={`application-sidebar ${
        isCollapsed ? "application-sidebar--collapsed" : ""
      } ${isMobileOpen ? "application-sidebar--mobile-open" : ""}`}
      id="primary-sidebar"
      ref={sidebarRef}
      role={isMobile ? "dialog" : undefined}
      aria-modal={isMobile && isMobileOpen ? "true" : undefined}
      aria-label={isMobile ? "Application navigation" : undefined}
      tabIndex={isMobile ? -1 : undefined}
    >
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <span className="sidebar-brand-mark" aria-hidden="true">
            PP
          </span>
          <span className="sidebar-brand-copy">
            <strong>PokePortfolio</strong>
            <span>Investment tracker</span>
          </span>
        </div>

        {isMobile && (
          <button
            className="sidebar-close-button"
            type="button"
            ref={closeButtonRef}
            onClick={onCloseMobile}
            aria-label="Close navigation"
          >
            <svg
              className="sidebar-control-icon"
              viewBox="0 0 24 24"
              aria-hidden="true"
              focusable="false"
            >
              <path d="m6 6 12 12M18 6 6 18" />
            </svg>
          </button>
        )}
      </div>

      <nav
        className="sidebar-navigation"
        id="primary-navigation"
        aria-label="Primary navigation"
      >
        {NAV_ITEMS.map((item) => {
          const isCurrent = isCurrentNavigationItem(item.to);

          return (
            <Link
              className={`sidebar-nav-link ${
                isCurrent ? "sidebar-nav-link--active" : ""
              }`}
              key={item.to}
              to={item.to}
              title={!showFullSidebar ? item.label : undefined}
              aria-current={isCurrent ? "page" : undefined}
              aria-label={!showFullSidebar ? item.label : undefined}
              onClick={isMobile ? onCloseMobile : undefined}
            >
              <SidebarIcon name={item.icon} />
              <span className="sidebar-nav-label">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {!isMobile && (
        <button
          className="sidebar-collapse-button"
          type="button"
          onClick={onToggleCollapse}
          aria-expanded={!isCollapsed}
          aria-controls="primary-navigation"
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <svg
            className="sidebar-control-icon"
            viewBox="0 0 24 24"
            aria-hidden="true"
            focusable="false"
          >
            <path d={isCollapsed ? "m9 6 6 6-6 6" : "m15 6-6 6 6 6"} />
          </svg>
          <span className="sidebar-nav-label">
            {isCollapsed ? "Expand" : "Collapse"}
          </span>
        </button>
      )}
    </aside>
  );
}
