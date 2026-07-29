# Ticket 009A - Application Shell and Sidebar Navigation

## Goal

Create a reusable application shell with a responsive, collapsible left
sidebar before adding more frontend pages.

## Dependencies

- Ticket 009 must be committed.

## Routes

```txt
/collection
/search
/settings
```

`/` should redirect to `/collection`.

Preserve the existing `/sealed-products` route inside the shell.

Until ticket 010 is implemented, `/assets/:assetId` may render a clearly
labelled placeholder with a link back to Collection. Unknown paths must render
a Not Found page instead of silently rendering Collection.

## Requirements

- Replace manual `window.location.pathname` checks with a small client-side
  routing setup appropriate for React.
- Ensure direct loading and refreshing of client routes works in Vite
  development and preview. Document the SPA history fallback required by a
  future static host, or choose a routing mode that does not require one.
- Keep page-level content inside a reusable `AppShell`.
- Keep sidebar behavior in a readable `Sidebar` component.
- Include navigation items for:
  - Collection
  - Search
  - Settings
- Clearly show the active route.
- On desktop, toggle between:
  - expanded sidebar with icons and labels;
  - compact icon rail.
- On small screens:
  - show a menu button;
  - open the sidebar as an off-canvas drawer;
  - include an always-visible close control;
  - close it from the backdrop, after navigation, or when Escape is pressed;
  - move focus into the drawer when it opens;
  - contain focus and prevent background interaction while it is open;
  - restore focus to the menu button when it closes.
- Preserve the current collection dashboard behavior.
- Preserve the current sealed-product workflow.
- Search and Settings may use clear placeholder page components in this
  structural ticket. Their functionality belongs to later tickets.
- Sidebar collapsed state may be kept in component state or `localStorage`.
  Do not add backend persistence.

## Accessibility

- Use semantic navigation markup.
- Give the sidebar toggle an accessible name.
- Use `aria-expanded` and `aria-controls` where appropriate.
- Use `aria-current="page"` on the active navigation link.
- Keep keyboard focus visible.
- Keep navigation usable without a mouse.
- Prevent the mobile drawer from obscuring the page after it closes.
- Use text labels or tooltips when the desktop sidebar is collapsed.
- Respect reduced-motion preferences if transitions are added.

## Suggested components

```txt
AppShell
Sidebar
SidebarNavItem
MobileMenuButton
SearchPage
SettingsPage
```

`SearchPage` and `SettingsPage` are route placeholders only in this ticket.

## Acceptance criteria

- Collection, Search, and Settings routes render inside one shared shell.
- `/` redirects to `/collection`.
- Browser Back and Forward navigation works.
- Directly loading and refreshing `/search`, `/settings`, and
  `/sealed-products` renders the same route.
- Desktop expand/collapse works without losing the active page.
- Mobile drawer open, close, Escape, and navigation behavior work.
- Mobile focus containment and focus restoration work.
- The active sidebar item is visually and programmatically identifiable.
- Unknown routes show a Not Found page.
- Existing collection and sealed-product behavior still works.
- Frontend lint and production build pass.

If no frontend component-test harness exists, record a manual smoke check for:

- keyboard-only navigation;
- `aria-current` on each route;
- browser Back and Forward;
- direct route refresh;
- drawer close button, backdrop, and Escape behavior;
- focus restoration;
- desktop and mobile breakpoints.

## Not included

- card search requests or results;
- adding assets from search;
- settings forms or currency conversion;
- backend changes;
- authentication or real user profiles;
- pricing;
- AI;
- alerts;
- scraping.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/04_frontend_pages.md,
docs/12_frontend_navigation_and_search_plan.md, and
docs/tickets/009a_application_shell_sidebar.md.

Implement ticket 009A only.

Create a reusable React application shell with a responsive, collapsible left
sidebar and routes for Collection, Search, and Settings. Preserve the current
collection dashboard and sealed-product workflow.

Search and Settings should be route placeholders only. Do not implement search
requests, asset creation, settings persistence, pricing, authentication, AI,
alerts, or scraping.
```
