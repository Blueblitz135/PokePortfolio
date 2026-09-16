/** Provide shared navigation, responsive sidebar behavior, and routed page content. */
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import { Outlet, useLocation } from "react-router-dom";

import { useMediaQuery } from "../hooks/useMediaQuery";
import { Sidebar } from "./Sidebar";

const MOBILE_SIDEBAR_QUERY = "(max-width: 48rem)";
const FOCUSABLE_SELECTOR = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(",");

/** Find keyboard-focusable visible descendants for the mobile focus trap. */
function getVisibleFocusableElements(container: HTMLElement): HTMLElement[] {
  return Array.from(
    container.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR),
  ).filter(
    (element) =>
      element.getClientRects().length > 0 && !element.hasAttribute("inert"),
  );
}

/** Coordinate desktop/mobile navigation, focus restoration, and nested routes. */
export function AppShell() {
  const location = useLocation();
  const isMobile = useMediaQuery(MOBILE_SIDEBAR_QUERY);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const sidebarRef = useRef<HTMLElement>(null);
  const applicationFrameRef = useRef<HTMLDivElement>(null);
  const skipLinkRef = useRef<HTMLAnchorElement>(null);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const restoreMenuFocusRef = useRef(false);
  const focusWasInSidebarRef = useRef(false);
  const previousIsMobileRef = useRef(isMobile);
  const previousLocationRef = useRef(
    `${location.pathname}${location.search}${location.hash}`,
  );

  const closeMobileSidebar = useCallback((restoreFocus = true) => {
    restoreMenuFocusRef.current = restoreFocus;
    setIsMobileOpen(false);
  }, []);

  /** Open mobile navigation while remembering where keyboard focus began. */
  function openMobileSidebar() {
    restoreMenuFocusRef.current = false;
    setIsMobileOpen(true);
  }

  useLayoutEffect(() => {
    const breakpointChanged = previousIsMobileRef.current !== isMobile;
    previousIsMobileRef.current = isMobile;

    if (breakpointChanged && focusWasInSidebarRef.current) {
      if (isMobile) {
        menuButtonRef.current?.focus();
      } else {
        const activeNavigationLink =
          sidebarRef.current?.querySelector<HTMLElement>(
            '[aria-current="page"]',
          );
        (
          activeNavigationLink ??
          document.getElementById("main-content")
        )?.focus();
      }
    }

    if (isMobile && isMobileOpen) {
      if (sidebarRef.current) {
        sidebarRef.current.inert = false;
      }
      if (applicationFrameRef.current) {
        applicationFrameRef.current.inert = true;
      }
      if (skipLinkRef.current) {
        skipLinkRef.current.inert = true;
      }
      closeButtonRef.current?.focus();
      return;
    }

    if (applicationFrameRef.current) {
      applicationFrameRef.current.inert = false;
    }
    if (skipLinkRef.current) {
      skipLinkRef.current.inert = false;
    }

    if (!isMobileOpen && restoreMenuFocusRef.current) {
      restoreMenuFocusRef.current = false;
      menuButtonRef.current?.focus();
    }
  }, [isMobile, isMobileOpen]);

  useEffect(() => {
    /** Remember whether focus last belonged to navigation or main content. */
    function trackFocusedRegion(event: FocusEvent) {
      if (!(event.target instanceof Node)) {
        return;
      }

      if (sidebarRef.current?.contains(event.target)) {
        focusWasInSidebarRef.current = true;
      } else if (
        event.target !== document.body &&
        event.target !== document.documentElement
      ) {
        focusWasInSidebarRef.current = false;
      }
    }

    document.addEventListener("focusin", trackFocusedRegion);
    return () => document.removeEventListener("focusin", trackFocusedRegion);
  }, []);

  useEffect(() => {
    if (!isMobile && isMobileOpen) {
      closeMobileSidebar(false);
    }
  }, [closeMobileSidebar, isMobile, isMobileOpen]);

  useEffect(() => {
    const sidebar = sidebarRef.current;
    const applicationFrame = applicationFrameRef.current;
    const skipLink = skipLinkRef.current;

    if (!sidebar || !applicationFrame || !skipLink) {
      return;
    }

    const drawerIsOpen = isMobile && isMobileOpen;
    const previousBodyOverflow = document.body.style.overflow;

    applicationFrame.inert = drawerIsOpen;
    skipLink.inert = drawerIsOpen;
    sidebar.inert = isMobile && !isMobileOpen;
    document.body.style.overflow = drawerIsOpen
      ? "hidden"
      : previousBodyOverflow;

    return () => {
      applicationFrame.inert = false;
      skipLink.inert = false;
      sidebar.inert = false;
      document.body.style.overflow = previousBodyOverflow;
    };
  }, [isMobile, isMobileOpen]);

  useEffect(() => {
    if (!isMobile || !isMobileOpen) {
      return;
    }

    /** Close on Escape and cycle Tab focus within the open mobile drawer. */
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        closeMobileSidebar();
        return;
      }

      if (event.key !== "Tab" || !sidebarRef.current) {
        return;
      }

      const focusableElements = getVisibleFocusableElements(
        sidebarRef.current,
      );
      if (focusableElements.length === 0) {
        event.preventDefault();
        sidebarRef.current.focus();
        return;
      }

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];
      const activeElement = document.activeElement;

      if (!sidebarRef.current.contains(activeElement)) {
        event.preventDefault();
        (event.shiftKey ? lastElement : firstElement).focus();
      } else if (event.shiftKey && activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      } else if (!event.shiftKey && activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [closeMobileSidebar, isMobile, isMobileOpen]);

  useEffect(() => {
    const currentLocation =
      `${location.pathname}${location.search}${location.hash}`;

    if (previousLocationRef.current !== currentLocation) {
      previousLocationRef.current = currentLocation;
      if (isMobileOpen) {
        closeMobileSidebar();
      }
    }
  }, [
    closeMobileSidebar,
    isMobileOpen,
    location.hash,
    location.pathname,
    location.search,
  ]);

  useEffect(() => {
    if (!location.hash) {
      return;
    }

    let targetId: string;
    try {
      targetId = decodeURIComponent(location.hash.slice(1));
    } catch {
      return;
    }

    const animationFrame = window.requestAnimationFrame(() => {
      document.getElementById(targetId)?.scrollIntoView({ block: "start" });
    });

    return () => window.cancelAnimationFrame(animationFrame);
  }, [location.hash, location.pathname]);

  return (
    <div
      className={`application-layout ${
        isCollapsed ? "application-layout--collapsed" : ""
      }`}
    >
      <a className="skip-link" href="#main-content" ref={skipLinkRef}>
        Skip to main content
      </a>

      {isMobile && isMobileOpen && (
        <button
          className="sidebar-backdrop"
          type="button"
          tabIndex={-1}
          onClick={() => closeMobileSidebar()}
          aria-label="Close navigation"
        />
      )}

      <Sidebar
        isCollapsed={isCollapsed}
        isMobile={isMobile}
        isMobileOpen={isMobileOpen}
        sidebarRef={sidebarRef}
        closeButtonRef={closeButtonRef}
        onToggleCollapse={() => setIsCollapsed((current) => !current)}
        onCloseMobile={() => closeMobileSidebar()}
      />

      <div className="application-frame" ref={applicationFrameRef}>
        <header className="mobile-application-header">
          <button
            className="mobile-menu-button"
            type="button"
            ref={menuButtonRef}
            onClick={openMobileSidebar}
            aria-expanded={isMobileOpen}
            aria-controls="primary-sidebar"
            aria-label="Open navigation"
          >
            <svg
              className="sidebar-control-icon"
              viewBox="0 0 24 24"
              aria-hidden="true"
              focusable="false"
            >
              <path d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          </button>
          <span className="mobile-application-title">PokePortfolio</span>
        </header>

        <main className="application-main" id="main-content" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
