# AGENTS.md

## Project Overview

Django 6.0.5 learning log application with Tailwind CSS 4.x styling.

## Versioning

Each iteration must update `pyproject.toml` version and `site_config.toml` version.

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

# Run tests
uv run python manage.py test
```

## App Structure

| App | URL Namespace | Purpose |
|-----|---------------|---------|
| `core` | `core/` | Polls/voting |
| `catalog` | `catalog` | Books, authors, genres, instances |
| `learning_logs` | `learning_logs` | Personal learning topics/entries |
| `accounts` | `accounts` | Authentication & Profile |

## Critical Constraints

- **`core/` and `learning_logs/`** - minimal changes only
- **`catalog/`** - can be significantly modified
- **`accounts/`** - authentication, registration, and profile management
- **Apps are independent**: `core`, `learning_logs`, `catalog` each have their own homepage and navigation
- Each app's header only links to its own routes, never to other apps
- **No Chinese in code** - use English only
- All app templates must inherit from `templates/base.html`
- Template structure per app: `app/templates/app/base.html`
- Static structure per app: `app/static/app/{js,css,images}/`

### Accounts App Exception

The `accounts` app follows Django's built-in auth conventions, not the project's template structure rules:

- Templates live in `accounts/templates/registration/` (Django default)
- Templates extend `base.html` directly (no app-level `base.html`)
- No own header/footer components (uses root header/footer)
- Uses `django.contrib.auth.urls` for login/logout/password flows

## Configuration

- Django settings: `config/settings.py`
- Environment variables: `.env` (see `.env.example`)
- Site config: `site_config.toml` (loaded via context processor)
- Database: SQLite (`db.sqlite3`)

## Template Inheritance

```html
{% extends "base.html" %}
```

All app `base.html` files should extend the root `templates/base.html`.

## Code Style

- **Python**: format with `black`, 4-space indentation
- **Templates (HTML)**: 2-space indentation
- **JavaScript**: 2-space indentation
- **CSS**: 2-space indentation

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

## Pagination

Configurable via `site_config.toml` under `[pagination]`:

- `style = "traditional"` — page numbers with prev/next
- `style = "load_more"` — AJAX-based infinite scroll button
