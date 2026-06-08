import os
import sys
from datetime import date, timedelta
from random import choice, randint, sample
from random import seed as set_seed
from random import uniform

import django
from django.utils import timezone
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User

from catalog.models import Author, Book, BookInstance, Genre, Language, Record, Tag
from core.models import Choice, Question
from learning_logs.models import Entry, Topic

SEED = 42
fake = Faker()
Faker.seed(SEED)
set_seed(SEED)


def delete_all():
    Record.objects.all().delete()
    BookInstance.objects.all().delete()
    Book.objects.all().delete()
    Tag.objects.all().delete()
    Author.objects.all().delete()
    Genre.objects.all().delete()
    Language.objects.all().delete()
    Entry.objects.all().delete()
    Topic.objects.all().delete()
    Choice.objects.all().delete()
    Question.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()


def create_staff_users():
    staff_data = [
        ("admin", "admin@example.com", "admin123", True, False),
        ("librarian1", "lib1@example.com", "staff123", False, True),
        ("librarian2", "lib2@example.com", "staff123", False, True),
        ("librarian3", "lib3@example.com", "staff123", False, True),
    ]
    created = []
    for username, email, password, is_superuser, is_staff in staff_data:
        if User.objects.filter(username=username).exists():
            print(f"  {username} already exists, skipping")
            created.append(User.objects.get(username=username))
            continue
        if is_superuser:
            user = User.objects.create_superuser(username, email, password)
        else:
            user = User.objects.create_user(
                username, email, password, is_staff=is_staff
            )
            from django.contrib.auth.models import Permission

            perms = Permission.objects.filter(
                codename__in=[
                    "can_mark_returned",
                    "add_book",
                    "change_book",
                    "delete_book",
                    "add_author",
                    "change_author",
                    "delete_author",
                    "add_genre",
                    "change_genre",
                    "delete_genre",
                    "add_language",
                    "change_language",
                    "delete_language",
                    "add_bookinstance",
                    "change_bookinstance",
                    "delete_bookinstance",
                    "add_tag",
                    "change_tag",
                    "delete_tag",
                    "add_record",
                    "change_record",
                    "delete_record",
                ]
            )
            user.user_permissions.set(perms)
        created.append(user)
        print(f"  Created {username}")
    return created


def create_users(count):
    users = []
    for i in range(count):
        username = f"user{i+1}"
        user = User(
            username=username,
            email=f"{username}@example.com",
        )
        user.set_password("testpass123")
        users.append(user)
    User.objects.bulk_create(users)
    print(f"  Created {count} regular users")
    return list(User.objects.all())


def create_catalog_data(book_count, instance_min, instance_max):
    genres = []
    languages = []
    tags = []
    authors = []
    books = []
    book_instances = []

    genre_names = [
        "Fiction",
        "Non-Fiction",
        "Science Fiction",
        "Fantasy",
        "Mystery",
        "Thriller",
        "Romance",
        "Historical Fiction",
        "Biography",
        "Science",
        "Philosophy",
        "Poetry",
        "Drama",
        "Horror",
        "Adventure",
        "Self-Help",
        "Travel",
        "Cooking",
        "Art",
        "Technology",
    ]
    for name in genre_names:
        genres.append(Genre(name=name))
    Genre.objects.bulk_create(genres)

    language_names = [
        "English",
        "Spanish",
        "French",
        "German",
        "Chinese",
        "Japanese",
        "Korean",
        "Italian",
        "Portuguese",
        "Russian",
    ]
    for name in language_names:
        languages.append(Language(name=name))
    Language.objects.bulk_create(languages)

    tag_names = [
        "Classic",
        "Bestseller",
        "Award Winner",
        "New Release",
        "Vintage",
        "Illustrated",
        "Hardcover",
        "Paperback",
        "Signed",
        "First Edition",
        "Rare",
        "Reference",
        "Textbook",
        "Children",
        "Young Adult",
        "Graphic Novel",
        "Audiobook",
        "Large Print",
        "Bilingual",
        "Collector",
    ]
    for name in tag_names:
        tags.append(Tag(name=name))
    Tag.objects.bulk_create(tags)

    for _ in range(300):
        birth = fake.date_between(start_date="-100y", end_date="-20y")
        death = (
            fake.date_between(start_date=birth, end_date="today")
            if randint(0, 4) == 0
            else None
        )
        authors.append(
            Author(
                name=fake.name(),
                date_of_birth=birth,
                date_of_death=death,
            )
        )
    Author.objects.bulk_create(authors)

    genre_list = list(Genre.objects.all())
    lang_list = list(Language.objects.all())
    author_list = list(Author.objects.all())
    tag_list = list(Tag.objects.all())

    for _ in range(book_count):
        books.append(
            Book(
                title=fake.sentence(
                    nb_words=randint(2, 6), variable_nb_words=True
                ).rstrip("."),
                author=choice(author_list),
                summary=fake.paragraph(nb_sentences=randint(2, 5)),
                genre=choice(genre_list),
                language=choice(lang_list),
            )
        )
    Book.objects.bulk_create(books)

    for book in Book.objects.all():
        book.tags.set(sample(tag_list, k=randint(0, 4)))

    statuses = ["d", "o", "a", "r"]
    status_weights = [0.1, 0.3, 0.5, 0.1]
    users = list(User.objects.filter(is_superuser=False))

    for book in Book.objects.all():
        num_instances = randint(instance_min, instance_max)
        for _ in range(num_instances):
            status = weighted_choice(statuses, status_weights)
            borrower = None
            due_back = None
            if status == "o" and users:
                borrower = choice(users)
                due_back = fake.date_between(start_date="-7d", end_date="+30d")
            elif status == "r":
                due_back = fake.date_between(start_date="today", end_date="+30d")

            book_instances.append(
                BookInstance(
                    book=book,
                    imprint=fake.company() + " Editions",
                    due_back=due_back,
                    borrower=borrower,
                    status=status,
                )
            )
    BookInstance.objects.bulk_create(book_instances)

    records = []
    for bi in BookInstance.objects.filter(status="o", borrower__isnull=False):
        borrow_date = fake.date_between(start_date="-60d", end_date="today")
        records.append(
            Record(
                book_instance=bi,
                borrower=bi.borrower,
                borrow_date=borrow_date,
                return_date=None,
            )
        )

    for bi in BookInstance.objects.filter(status="a"):
        if users and randint(0, 2) == 0:
            borrower = choice(users)
            borrow_date = fake.date_between(start_date="-90d", end_date="-1d")
            return_date = fake.date_between(start_date=borrow_date, end_date="today")
            records.append(
                Record(
                    book_instance=bi,
                    borrower=borrower,
                    borrow_date=borrow_date,
                    return_date=return_date,
                )
            )
    Record.objects.bulk_create(records)

    print(f"  Genre: {len(genres)}")
    print(f"  Language: {len(languages)}")
    print(f"  Tag: {len(tags)}")
    print(f"  Author: {len(authors)}")
    print(f"  Book: {len(books)}")
    print(f"  BookInstance: {len(book_instances)}")
    print(f"  Record: {len(records)}")


def weighted_choice(items, weights):
    total = sum(weights)
    r = uniform(0, total)
    cumulative = 0
    for item, w in zip(items, weights):
        cumulative += w
        if r <= cumulative:
            return item
    return items[-1]


def create_learning_logs_data(topic_count, entry_range):
    users = list(User.objects.filter(is_superuser=False))
    if not users:
        print("  No users found, skipping")
        return

    topics = []
    entries = []

    for _ in range(topic_count):
        topics.append(
            Topic(
                text=fake.sentence(nb_words=3, variable_nb_words=True).rstrip("."),
                owner=choice(users),
            )
        )
    Topic.objects.bulk_create(topics)

    for topic in Topic.objects.all():
        entry_num = randint(*entry_range)
        for _ in range(entry_num):
            entries.append(
                Entry(
                    text=fake.paragraph(nb_sentences=randint(2, 5)),
                    topic=topic,
                )
            )
    Entry.objects.bulk_create(entries)

    print(f"  Topic: {len(topics)}")
    print(f"  Entry: {len(entries)}")


def create_core_data(question_count, choice_range):
    questions = []
    choices_list = []

    for _ in range(question_count):
        questions.append(
            Question(
                question_text=fake.sentence(nb_words=6, variable_nb_words=True).rstrip(
                    "?"
                )
                + "?",
                pub_date=fake.date_time_between(
                    start_date="-30d",
                    end_date="now",
                    tzinfo=timezone.get_current_timezone(),
                ),
            )
        )
    Question.objects.bulk_create(questions)

    for question in Question.objects.all():
        choice_num = randint(*choice_range)
        for _ in range(choice_num):
            choices_list.append(
                Choice(
                    question=question,
                    choice_text=fake.sentence(
                        nb_words=3, variable_nb_words=True
                    ).rstrip("."),
                    votes=randint(0, 100),
                )
            )
    Choice.objects.bulk_create(choices_list)

    print(f"  Question: {len(questions)}")
    print(f"  Choice: {len(choices_list)}")


if __name__ == "__main__":
    print("=== Creating Fake Data (seed=42) ===\n")

    print("Deleting existing data...")
    delete_all()

    print("Creating staff users...")
    create_staff_users()

    print("Creating regular users...")
    create_users(20)

    print("Creating catalog data...")
    create_catalog_data(book_count=250, instance_min=3, instance_max=8)

    print("Creating learning logs data...")
    create_learning_logs_data(50, (3, 8))

    print("Creating core data...")
    create_core_data(30, (2, 6))

    print(
        "\nDone! Staff accounts: admin/admin123, librarian1/staff123, librarian2/staff123, librarian3/staff123"
    )
