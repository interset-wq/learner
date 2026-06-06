import os
from random import randint, choice
from datetime import timedelta
from typing import List, Iterable

from faker import Faker
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from learning_logs.models import Topic, Entry

fake = Faker()


def delete_all():
    topics = Topic.objects.all()
    for topic in topics:
        topic.delete()


def create_fake_data(
        topic_count: int,
        response_count: List[int] | range | Iterable[int]
):
    topics = []
    entries = []
    now = timezone.now()

    for _ in range(topic_count):
        date_added = fake.date_time_between(
            start_date=now - timedelta(days=60),
            end_date=now,
            tzinfo=timezone.get_current_timezone()
        )
        topic = Topic(
            text=fake.sentence(nb_words=6, variable_nb_words=True),
            date_added=date_added,
        )
        topics.append(topic)

    Topic.objects.bulk_create(topics)

    total_entry = 0
    for topic in topics:
        date_added = fake.date_time_between(
            start_date=now - timedelta(days=60),
            end_date=now,
            tzinfo=timezone.get_current_timezone()
        )
        choice_count = choice(list(response_count))
        total_entry += choice_count
        for _ in range(choice_count):
            entry = Entry(
                topic=topic,
                text=fake.sentence(nb_words=60, variable_nb_words=True),
                date_added=date_added,
            )
            entries.append(entry)

    Entry.objects.bulk_create(entries)

    print(f"Created Topic: {topic_count}")
    print(f"Created Entry: {total_entry}")


if __name__ == "__main__":
    delete_all()
    create_fake_data(500, range(3, 5))
