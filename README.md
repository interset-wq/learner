# Learning Log

A collection of Django demo applications showcasing modern web development patterns.

**Version**: 2.0.3

## Tech Stack

- **Django 6.0.5** — Python web framework
- **HTMX 2.x** — Lightweight interactivity without JavaScript
- **Tailwind CSS 4.x** — Utility-first CSS
- **SQLite** — Database
- **Python 3.13** with [uv](https://docs.astral.sh/uv/)
- **Node.js 22+** with [pnpm](https://pnpm.io/)

## Apps

### Catalog

A local library management system.

- Browse books, authors, genres, languages, tags
- Borrow and return books (authenticated users)
- Renew borrowed books (staff with `can_mark_returned` permission)
- Staff dashboard with stats and quick actions
- Search books by title or author
- User profiles with borrowing history

**URL**: `/catalog/` | [README](catalog/README.md)

### Learning Logs

A personal learning journal with social features.

- Create topics and record learning entries in Markdown
- EasyMDE editor with live preview and toolbar
- Public/private visibility for topics and entries
- Like, comment, and share on public entries
- Nested comment threads (max 2 levels) with @mentions
- Infinite scroll pagination for comments
- Click-to-reply with auto @mention
- Collapsible reply threads

**URL**: `/learning_logs/` | [README](learning_logs/README.md)

### Polls (Core)

A polling application.

- Create questions with multiple choices
- Vote on questions (atomic counting with F expressions)
- View results with progress bars

**URL**: `/core/` | [README](core/README.md)

### Accounts

Authentication and profile management (Django built-in auth).

- Login, logout, registration
- Profile editing with role badges
- Public user profiles with topic listings
- Password change and reset

**URL**: `/accounts/` | [README](accounts/README.md)

## Quick Start

### Prerequisites

- **Python 3.13+** with [uv](https://docs.astral.sh/uv/)
- **Node.js 22+** with [pnpm](https://pnpm.io/)

### Linux / macOS

```bash
make setup
make dev
```

### Windows

```bash
uv sync
pnpm install
uv run python manage.py migrate
uv run python create_fake_data.py
pnpm build
pnpm dev
uv run python manage.py runserver
```

### Docker

```bash
docker compose build
docker compose up -d
docker compose exec web uv run python create_fake_data.py
docker compose down
```

Access: http://localhost:8000 | Admin: `admin` / `admin123`

Run `make help` to see all available commands.

## Configuration

| File | Purpose |
|------|---------|
| `.env` | Environment variables (SECRET_KEY, DEBUG, etc.) |
| `.env.example` | Template with all available variables |
| `site_config.toml` | Site name, pagination style |
| `pyproject.toml` | Python dependencies and project metadata |

## Project Structure

```
learning_log/
├── catalog/          # Library management app
├── core/             # Polls app
├── learning_logs/    # Personal learning journal
├── accounts/         # Authentication
├── config/           # Django settings, mixins, TOML loader
├── templates/        # Root templates and components
├── static/           # Static assets (HTMX, Tailwind CSS output)
├── .env              # Environment variables
├── site_config.toml  # Site configuration
├── Makefile          # Linux/macOS shortcuts
├── Dockerfile        # Docker build
└── create_fake_data.py
```

## Staff Accounts

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Superuser |
| `librarian1` | `staff123` | Staff (all catalog permissions) |
| `librarian2` | `staff123` | Staff (all catalog permissions) |
| `librarian3` | `staff123` | Staff (all catalog permissions) |
| `librarian` | `staff123` | Staff (borrow/return only) |
| `catalog_editor` | `staff123` | Staff (add/edit catalog) |
| `catalog_viewer` | `staff123` | Staff (read-only) |

## Testing

```bash
uv run python manage.py test
```

CI runs automatically on push/PR to main via GitHub Actions.

## Pre-commit

```bash
uv run pre-commit install
```

Runs automatically on commit: trailing whitespace, end-of-file, YAML check, black, isort.

## License

MIT
