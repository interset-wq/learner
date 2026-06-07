# local_library
A Django project which is simple and useful to learn the features of Django.


```text
+----------------+        +----------------+
|     GENRE      |        |     AUTHOR     |
+----------------+        +----------------+
| id (PK)        |        | id (PK)        |
| name (Unique)  |        | name           |
+----------------+        | date_of_birth  |
       ^                  | date_of_death  |
       | m                 +----------------+
       |                         ^
       | n                       | 1
+----------------+               |
|      BOOK      | <-------------+ n
+----------------+
| id (PK)        |
| title          |
| summary        |
| ISBN (Unique)  | <-----------+ n
| author_id (FK) |             |
| language_id(FK)|             |
+----------------+             |
       | 1                     |
       |                       | 
       | n                     | 1
       v                       v
+----------------+        +----------------+
|  BOOKINSTANCE  |        |    LANGUAGE    |
+----------------+        +----------------+
| id (UUID, PK)  |        | id (PK)        |
| imprint        |        | name (Unique)  |
| due_back       |        +----------------+
| status         |               
| book_id (FK)   |               
| borrower_id(FK)| 
+----------------+
```

```mermaid
erDiagram
    GENRE {
        int id PK
        string name UK
    }
    LANGUAGE {
        int id PK
        string name UK
    }
    AUTHOR {
        int id PK
        string name
        date date_of_birth
        date date_of_death
    }
    BOOK {
        int id PK
        string title
        string summary
        string ISBN UK
        int author_id FK
        int language_id FK
    }
    BOOKINSTANCE {
        uuid id PK
        string imprint
        date due_back
        string status
        uuid borrower_id FK
        int book_id FK
    }
    USER {
        int id PK
    }

    AUTHOR ||--o{ BOOK : "1 : 1..*"
    LANGUAGE ||--o{ BOOK : "1 : 1..*"
    BOOK ||--o{ BOOKINSTANCE : "1 : 0..*"
    USER ||--o{ BOOKINSTANCE : "1 : 0..*"
    GENRE }|--|{ BOOK : "m : n"
```

