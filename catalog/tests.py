from datetime import date, timedelta

from django.contrib.auth.models import Permission, User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Author, Book, BookInstance, Genre, Language, Record, Tag


def create_user(username="testuser", password="testpass123", is_staff=False):
    return User.objects.create_user(
        username, f"{username}@test.com", password, is_staff=is_staff
    )


def create_book(title="Test Book", author_name="Test Author"):
    author, _ = Author.objects.get_or_create(name=author_name)
    language, _ = Language.objects.get_or_create(name="English")
    genre, _ = Genre.objects.get_or_create(name="Fiction")
    return Book.objects.create(
        title=title,
        author=author,
        summary="A test book.",
        language=language,
        genre=genre,
    )


def create_book_instance(book=None, status="a"):
    if book is None:
        book = create_book()
    return BookInstance.objects.create(
        book=book, imprint="Test Editions", status=status
    )


class AuthorModelTest(TestCase):
    def test_str(self):
        author = Author(name="J.K. Rowling")
        self.assertEqual(str(author), "J.K. Rowling")

    def test_get_absolute_url(self):
        author = Author.objects.create(name="Test Author")
        self.assertEqual(author.get_absolute_url(), f"/catalog/author/{author.id}/")


class GenreModelTest(TestCase):
    def test_str(self):
        genre = Genre(name="Fiction")
        self.assertEqual(str(genre), "Fiction")


class LanguageModelTest(TestCase):
    def test_str(self):
        lang = Language(name="English")
        self.assertEqual(str(lang), "English")


class TagModelTest(TestCase):
    def test_str(self):
        tag = Tag(name="Classic")
        self.assertEqual(str(tag), "Classic")


class BookModelTest(TestCase):
    def test_str(self):
        book = create_book(title="My Book")
        self.assertEqual(str(book), "My Book")

    def test_display_tags(self):
        book = create_book()
        tag1 = Tag.objects.create(name="Classic")
        tag2 = Tag.objects.create(name="Bestseller")
        book.tags.set([tag1, tag2])
        self.assertEqual(book.display_tags(), "Classic, Bestseller")


class BookInstanceModelTest(TestCase):
    def test_str(self):
        bi = create_book_instance()
        self.assertIn(str(bi.id), str(bi))
        self.assertIn("Test Book", str(bi))

    def test_is_overdue_past(self):
        bi = create_book_instance(status="o")
        bi.due_back = date.today() - timedelta(days=1)
        self.assertTrue(bi.is_overdue)

    def test_is_overdue_future(self):
        bi = create_book_instance(status="o")
        bi.due_back = date.today() + timedelta(days=1)
        self.assertFalse(bi.is_overdue)

    def test_is_overdue_none(self):
        bi = create_book_instance()
        bi.due_back = None
        self.assertFalse(bi.is_overdue)


class RecordModelTest(TestCase):
    def test_str(self):
        bi = create_book_instance()
        record = Record.objects.create(
            book_instance=bi, borrower=create_user(), borrow_date=date.today()
        )
        self.assertIn("Record", str(record))


class IndexViewTest(TestCase):
    def test_index_status_code(self):
        response = self.client.get(reverse("catalog:index"))
        self.assertEqual(response.status_code, 200)

    def test_index_context(self):
        create_book()
        response = self.client.get(reverse("catalog:index"))
        self.assertEqual(response.context["num_books"], 1)


class BookListViewTest(TestCase):
    def test_book_list(self):
        create_book()
        response = self.client.get(reverse("catalog:books"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")

    def test_search_by_title(self):
        create_book(title="Django Guide")
        create_book(title="Flask Tutorial")
        response = self.client.get(reverse("catalog:books") + "?q=Django")
        self.assertContains(response, "Django Guide")
        self.assertNotContains(response, "Flask Tutorial")

    def test_search_by_author(self):
        create_book(author_name="Alice")
        create_book(author_name="Bob")
        response = self.client.get(reverse("catalog:books") + "?q=Alice")
        self.assertContains(response, "Alice")
        self.assertNotContains(response, "Bob")


class BookDetailViewTest(TestCase):
    def test_detail(self):
        book = create_book()
        response = self.client.get(reverse("catalog:book-detail", args=[book.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")


class AuthorListViewTest(TestCase):
    def test_author_list(self):
        Author.objects.create(name="Alice")
        response = self.client.get(reverse("catalog:authors"))
        self.assertContains(response, "Alice")


class BorrowBookViewTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)
        self.book = create_book()
        self.instance = create_book_instance(self.book, status="a")

    def test_borrow_book_post(self):
        response = self.client.post(
            reverse("catalog:borrow-book", args=[self.instance.id])
        )
        self.assertRedirects(response, reverse("catalog:my-borrowed"))
        self.instance.refresh_from_db()
        self.assertEqual(self.instance.status, "o")
        self.assertEqual(self.instance.borrower, self.user)
        self.assertTrue(
            Record.objects.filter(
                book_instance=self.instance, borrower=self.user
            ).exists()
        )

    def test_borrow_book_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("catalog:borrow-book", args=[self.instance.id])
        )
        self.assertEqual(response.status_code, 302)


class ReturnBookViewTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)
        self.book = create_book()
        self.instance = create_book_instance(self.book, status="o")
        self.instance.borrower = self.user
        self.instance.due_back = date.today() + timedelta(days=7)
        self.instance.save()
        self.record = Record.objects.create(
            book_instance=self.instance, borrower=self.user, borrow_date=date.today()
        )

    def test_return_book_post(self):
        response = self.client.post(
            reverse("catalog:return-book", args=[self.instance.id])
        )
        self.assertRedirects(response, reverse("catalog:my-borrowed"))
        self.instance.refresh_from_db()
        self.assertEqual(self.instance.status, "a")
        self.assertIsNone(self.instance.borrower)
        self.record.refresh_from_db()
        self.assertIsNotNone(self.record.return_date)


class StaffDashboardTest(TestCase):
    def test_staff_access(self):
        user = create_user(is_staff=True)
        self.client.force_login(user)
        response = self.client.get(reverse("catalog:staff-dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_non_staff_redirected(self):
        user = create_user()
        self.client.force_login(user)
        response = self.client.get(reverse("catalog:staff-dashboard"))
        self.assertRedirects(response, reverse("catalog:index"))

    def test_anonymous_redirected(self):
        response = self.client.get(reverse("catalog:staff-dashboard"))
        self.assertEqual(response.status_code, 302)


class MyBorrowedViewTest(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse("catalog:my-borrowed"))
        self.assertEqual(response.status_code, 302)

    def test_shows_user_borrowed(self):
        user = create_user()
        self.client.force_login(user)
        book = create_book()
        bi = create_book_instance(book, status="o")
        bi.borrower = user
        bi.due_back = date.today() + timedelta(days=7)
        bi.save()
        response = self.client.get(reverse("catalog:my-borrowed"))
        self.assertContains(response, "Test Book")
