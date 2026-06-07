import os
from random import randint, choice, sample
from datetime import timedelta

from faker import Faker
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Genre, Language, Author, Book, BookInstance
from learning_logs.models import Topic, Entry
from core.models import Question, Choice
from django.contrib.auth.models import User

fake = Faker()


def delete_all():
    BookInstance.objects.all().delete()
    Book.objects.all().delete()
    Author.objects.all().delete()
    Genre.objects.all().delete()
    Language.objects.all().delete()
    Entry.objects.all().delete()
    Topic.objects.all().delete()
    Choice.objects.all().delete()
    Question.objects.all().delete()


def create_catalog_data(genre_count, lang_count, author_count, book_count, instance_range):
    genres = []
    languages = []
    authors = []
    books = []
    book_instances = []

    for _ in range(genre_count):
        genre = Genre(name=fake.word().capitalize())
        genres.append(genre)
    Genre.objects.bulk_create(genres)

    for _ in range(lang_count):
        lang = Language(name=fake.language_name())
        languages.append(lang)
    Language.objects.bulk_create(languages)

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

    for book in Book.objects.all():
        pick_num = randint(1, 3)
        random_genres = sample(genre_list, k=pick_num)
        book.genre.set(random_genres)

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


def create_learning_logs_data(topic_count, entry_range):
    users = list(User.objects.all())
    if not users:
        print("No users found, skipping learning_logs data")
        return

    topics = []
    entries = []

    for _ in range(topic_count):
        topic = Topic(
            text=fake.sentence(nb_words=3, variable_nb_words=True).rstrip("."),
            owner=choice(users)
        )
        topics.append(topic)
    Topic.objects.bulk_create(topics)

    for topic in Topic.objects.all():
        entry_num = randint(*entry_range) if len(entry_range) == 2 else choice(list(entry_range))
        for _ in range(entry_num):
            entry = Entry(
                text=fake.paragraph(nb_sentences=randint(2, 5)),
                topic=topic
            )
            entries.append(entry)
    Entry.objects.bulk_create(entries)

    print(f"Created Topic: {topic_count}")
    print(f"Created Entry: {len(entries)}")


def create_core_data(question_count, choice_range):
    questions = []
    choices = []

    for _ in range(question_count):
        question = Question(
            question_text=fake.sentence(nb_words=6, variable_nb_words=True).rstrip("?") + "?",
            pub_date=fake.date_time_between(start_date="-30d", end_date="now", tzinfo=timezone.get_current_timezone())
        )
        questions.append(question)
    Question.objects.bulk_create(questions)

    for question in Question.objects.all():
        choice_num = randint(*choice_range) if len(choice_range) == 2 else choice(list(choice_range))
        for _ in range(choice_num):
            c = Choice(
                question=question,
                choice_text=fake.sentence(nb_words=3, variable_nb_words=True).rstrip("."),
                votes=randint(0, 100)
            )
            choices.append(c)
    Choice.objects.bulk_create(choices)

    print(f"Created Question: {question_count}")
    print(f"Created Choice: {len(choices)}")


if __name__ == "__main__":
    delete_all()
    create_catalog_data(8, 6, 200, 800, range(2, 5))
    create_learning_logs_data(50, (3, 8))
    create_core_data(30, (2, 6))
