import os
from random import randint, choice, sample
from datetime import timedelta
from typing import List, Iterable

from faker import Faker
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Genre, Language, Author, Book, BookInstance

fake = Faker()


def delete_all():
    BookInstance.objects.all().delete()
    Book.objects.all().delete()
    Author.objects.all().delete()
    Genre.objects.all().delete()
    Language.objects.all().delete()


def create_fake_data(
        genre_count: int,
        lang_count: int,
        author_count: int,
        book_count: int,
        instance_range: List[int] | range | Iterable[int]
):
    genres = []
    languages = []
    authors = []
    books = []
    book_instances = []

    now = timezone.now()

    # 1. Create Genres
    for _ in range(genre_count):
        genre = Genre(name=fake.word().capitalize())
        genres.append(genre)
    Genre.objects.bulk_create(genres)

    # 2. Create Languages
    for _ in range(lang_count):
        lang = Language(name=fake.language_name())
        languages.append(lang)
    Language.objects.bulk_create(languages)

    # 3. Create Authors
    for _ in range(author_count):
        birth_date = fake.date_between(start_date="-120y", end_date="-20y")
        death_date = fake.date_between(start_date=birth_date, end_date="today") if randint(0, 3) == 0 else None
        author = Author(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            date_of_birth=birth_date,
            date_of_death=death_date
        )
        authors.append(author)
    Author.objects.bulk_create(authors)

    # 4. Create Books
    genre_list = list(Genre.objects.all())
    lang_list = list(Language.objects.all())
    author_list = list(Author.objects.all())

    for _ in range(book_count):
        book = Book(
            title=fake.sentence(nb_words=4, variable_nb_words=True).rstrip("."),
            author=choice(author_list),
            summary=fake.paragraph(nb_sentences=3),
            isbn=fake.isbn13(),
            language=choice(lang_list)
        )
        books.append(book)

    Book.objects.bulk_create(books)

    # Assign Many-to-Many Genre (fixed: use sample instead of choice + k)
    for book in Book.objects.all():
        pick_num = randint(1, 3)
        random_genres = sample(genre_list, k=pick_num)
        book.genre.set(random_genres)

    # 5. Create Book Instances
    loan_status_choices = ['d', 'o', 'a', 'r']
    for book in Book.objects.all():
        instance_num = choice(list(instance_range))
        for _ in range(instance_num):
            due_back = fake.date_between(start_date="today", end_date="+30d") if choice(loan_status_choices) in ("o", "r") else None
            instance = BookInstance(
                book=book,
                imprint=fake.company(),
                due_back=due_back,
                status=choice(loan_status_choices)
            )
            book_instances.append(instance)

    BookInstance.objects.bulk_create(book_instances)

    print(f"Created Genre: {genre_count}")
    print(f"Created Language: {lang_count}")
    print(f"Created Author: {author_count}")
    print(f"Created Book: {book_count}")
    print(f"Created BookInstance: {len(book_instances)}")


if __name__ == "__main__":
    delete_all()
    create_fake_data(8, 6, 200, 800, range(2, 5))