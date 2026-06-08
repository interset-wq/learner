# Accounts

Authentication and profile management using Django's built-in auth system.

## Features

- Login and logout
- User registration
- Profile editing (username, email, first name, last name)
- Password change and reset
- Role badges (Superuser, Staff)

## URL

`/accounts/`

## Key URLs

| URL | Description |
|-----|-------------|
| `/accounts/login/` | Login page |
| `/accounts/logout/` | Logout |
| `/accounts/register/` | Registration |
| `/accounts/profile/` | Edit profile |
| `/accounts/password_change/` | Change password |
| `/accounts/password_reset/` | Reset password |

## Template Structure

Templates follow Django's auth conventions:

```
accounts/
├── templates/
│   └── registration/
│       ├── login.html
│       ├── register.html
│       └── profile.html
└── static/
    └── accounts/
        └── css/
            └── form.css
```
