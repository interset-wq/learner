# Learning Log

A collection of Django demo applications showcasing modern web development patterns.

## Tech Stack

- **Django 6.0.5** — Python web framework
- **Tailwind CSS 4.x** — Utility-first CSS
- **SQLite** — Database
- **Python 3.13** (uv package manager)
- **Node.js** (pnpm for Tailwind)

## Apps

### Catalog

A local library management system.

- Browse books, authors, genres, languages, tags
- Borrow and return books (authenticated users)
- Renew borrowed books (staff with `can_mark_returned` permission)
- Staff dashboard with stats and quick actions
- Search books by title or author
- User profiles with borrowing history

**URL**: `/catalog/`

### Learning Logs

A personal learning journal.

- Create topics and record learning entries
- User isolation (each user sees only their own data)
- Edit entries to track progress over time

**URL**: `/learning_logs/`

### Polls (Core)

A polling application.

- Create questions with multiple choices
- Vote on questions (atomic counting with F expressions)
- View results with progress bars

**URL**: `/core/`

### Accounts

Authentication and profile management (Django built-in auth).

- Login, logout, registration
- Profile editing
- Password change and reset

**URL**: `/accounts/`

## Quick Start

### Prerequisites

- **Python 3.13+** — [uv](https://docs.astral.sh/uv/) (recommended) or pip
- **Node.js 22+** — [pnpm](https://pnpm.io/) (recommended) or npm/yarn

### Linux / macOS

```bash
make setup          # Install + migrate + seed + build
make dev            # Start Django + Tailwind watch
# Access: http://localhost:8000  |  Admin: admin/admin123
make help           # Show all commands
```

### Windows (Manual)

```bash
uv sync             # or: pip install -r requirements.txt
pnpm install        # or: npm install

uv run python manage.py migrate
uv run python create_fake_data.py
pnpm build          # or: npm run build

# Run in two terminals:
pnpm dev            # Tailwind watch
uv run python manage.py runserver  # Django server

# Access: http://localhost:8000  |  Admin: admin/admin123
```

### Docker

```bash
docker compose build
docker compose up -d
docker compose exec web uv run python create_fake_data.py
# Access: http://localhost:8000  |  Admin: admin/admin123
docker compose down
```

## Project Structure

```
learning_log/
├── catalog/          # Library management app
├── core/             # Polls app
├── learning_logs/    # Personal learning journal
├── accounts/         # Authentication
├── config/           # Django settings
├── templates/        # Root templates
├── static/           # Static assets (Tailwind CSS output)
├── site_config.toml  # Site configuration
└── create_fake_data.py
```

## Staff Accounts

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Superuser |
| `librarian1` | `staff123` | Staff (borrow/return) |
| `librarian2` | `staff123` | Staff (borrow/return) |
| `librarian3` | `staff123` | Staff (borrow/return) |
| `librarian` | `staff123` | Staff (borrow/return only) |
| `catalog_editor` | `staff123` | Staff (add/edit catalog) |
| `catalog_viewer` | `staff123` | Staff (read-only) |

## License

MIT
