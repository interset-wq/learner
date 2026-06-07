# AGENTS.md

## Project Overview

Django 6.0.5 learning log application with Tailwind CSS 4.x styling.

## Package Managers

- **Python**: uv (Python 3.13)
- **Node.js**: pnpm (Tailwind CSS only)

## Commands

```bash
# Django
uv run python manage.py runserver
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py shell

# Tailwind CSS (development)
pnpm dev

# Tailwind CSS (production build)
pnpm build

# Generate fake data
uv run python create_fake_data.py
```

## App Structure

| App | URL Namespace | Purpose |
|-----|---------------|---------|
| `core` | `core/` | Polls/voting (under development) |
| `catalog` | `catalog` | Books, authors, genres, instances |
| `learning_logs` | `learning_logs` | Personal learning topics/entries |
| `accounts` | `accounts` | Authentication (READ-ONLY) |

## Critical Constraints

- **`accounts/` is read-only** - never modify files in this directory
- **`core/` and `learning_logs/`** - minimal changes only
- **`catalog/`** - can be significantly modified
- **Apps are independent**: `core`, `learning_logs`, `catalog` each have their own homepage and navigation
- Each app's header only links to its own routes, never to other apps
- **No Chinese in code** - use English only
- All app templates must inherit from `templates/base.html`
- Template structure per app: `app/templates/app/base.html`
- Static structure per app: `app/static/app/{js,css,images}/`

## Configuration

- Django settings: `config/settings.py`
- Site config: `site_config.toml` (loaded via context processor)
- Database: SQLite (`db.sqlite3`)

## Template Inheritance

```html
{% extends "base.html" %}
```

All app `base.html` files should extend the root `templates/base.html`.

## Styling

Uses Tailwind CSS 4.x. Input file: `static/css/input.css`, Output: `static/css/output.css`.

Run `pnpm dev` during development to watch for changes.

- Minimize raw CSS - prefer Tailwind utilities
- Keep global styles consistent - reuse rulesets in `input.css`
- Implement dark mode (can copy/paste sun/moon icons from Django admin source)

## Git Workflow

- Commit code regularly
- Each task in the task list should have at least one commit
- Do not commit directly to `main`

## Footer

Footer must provide links to other apps' root routes for cross-app navigation.
