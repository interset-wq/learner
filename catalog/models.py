from datetime import date

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse


class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:genre-detail', args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='genre_name_case_insensitive_unique',
                violation_error_message="Genre already exists (case insensitive match)"
            ),
        ]


class Language(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True
    )

    def get_absolute_url(self):
        return reverse('catalog:language-detail', args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='language_name_case_insensitive_unique',
                violation_error_message="Language already exists (case insensitive match)"
            ),
        ]


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:tag-detail', args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='tag_name_case_insensitive_unique',
                violation_error_message="Tag already exists (case insensitive match)"
            ),
        ]


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True)
    summary = models.TextField(max_length=1000)
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    genre = models.ForeignKey('Genre', on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField('Tag', blank=True)

    class Meta:
        ordering = ['title', 'author']

    def display_tags(self):
        return ', '.join([tag.name for tag in self.tags.all()[:3]])

    display_tags.short_description = 'Tags'

    def get_absolute_url(self):
        return reverse('catalog:book-detail', args=[str(self.id)])

    def __str__(self):
        return self.title


class BookInstance(models.Model):
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d'
    )

    @property
    def is_overdue(self):
        return bool(self.due_back and date.today() > self.due_back)

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def get_absolute_url(self):
        return reverse('catalog:bookinstance-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.id} ({self.book.title})'


class Record(models.Model):
    book_instance = models.ForeignKey('BookInstance', on_delete=models.RESTRICT)
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    borrow_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-borrow_date']

    def get_absolute_url(self):
        return reverse('catalog:record-detail', args=[str(self.id)])

    def __str__(self):
        return f'Record {self.id}: {self.book_instance}'


class Author(models.Model):
    name = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('catalog:author-detail', args=[str(self.id)])

    def __str__(self):
        return self.name or f'{self.last_name}, {self.first_name}'