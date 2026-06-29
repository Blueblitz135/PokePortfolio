# 10 - Step-by-Step Build Guide

## Step 0 - Create repo

```bash
mkdir pokemon-portfolio
cd pokemon-portfolio
git init
```

Copy this markdown pack into the repo.

Then commit the docs:

```bash
git add .
git commit -m "Add project docs and Codex tickets"
```

## Step 1 - Start in VS Code

Open the repo in VS Code.

Use the VS Code Codex agent first. Do not use parallel agents yet.

## Step 2 - Run ticket 001

Paste:

```txt
Read AGENTS.md, CODING_RULES.md, docs/00_project_overview.md, docs/01_mvp_scope.md, and docs/tickets/001_project_setup.md.

Implement ticket 001 only.

Do not implement external APIs, pricing, AI, auth, alerts, or scraping.

After coding:
- list changed files
- explain how to run backend and frontend
- run the checks that are available
- tell me what to commit
```

## Step 3 - Review and commit

After Codex finishes:

```bash
git status
git diff
```

Run the commands Codex gives you.

If it works:

```bash
git add .
git commit -m "Set up full stack project"
```

## Step 4 - Continue tickets in order

Suggested commit messages:

```txt
001: Set up full stack project
002: Add core database models
003: Add manual collection CRUD
004: Add purchase lots and calculations
005: Add asset image uploads
006: Add card metadata search
007: Add graded card overlay
008: Add sealed product support
009: Add collection dashboard
010: Add asset detail page
011: Add manual pricing snapshots
012: Add currency layer
013: Add tests and quality checks
014: Add external pricing adapters
```

## Step 5 - Only then use multiagent

After ticket 005, the project should be stable enough for limited multiagent work.

Start with:

- backend card search in one branch
- frontend search UI in another branch
- reviewer after both are done

## Step 6 - Keep a learning log

Create:

```txt
docs/dev_log.md
```

After each ticket, write:

- what changed
- what you understood
- what was confusing
- what broke
- how you fixed it

This is useful for interviews and co-op applications.
