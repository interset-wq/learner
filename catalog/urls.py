from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('manage/', views.staff_dashboard, name='staff-dashboard'),

    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),

    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),

    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('myhistory/', views.BorrowHistoryListView.as_view(), name='my-history'),
    path('borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),
    path('book/<int:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
    path('bookinstance/<int:pk>/borrow/', views.borrow_book, name='borrow-book'),
    path('bookinstance/<int:pk>/return/', views.return_book, name='return-book'),

    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genre/<int:pk>/', views.GenreDetailView.as_view(), name='genre-detail'),
    path('genre/create/', views.GenreCreate.as_view(), name='genre-create'),
    path('genre/<int:pk>/update/', views.GenreUpdate.as_view(), name='genre-update'),
    path('genre/<int:pk>/delete/', views.GenreDelete.as_view(), name='genre-delete'),

    path('languages/', views.LanguageListView.as_view(), name='languages'),
    path('language/<int:pk>/', views.LanguageDetailView.as_view(), name='language-detail'),
    path('language/create/', views.LanguageCreate.as_view(), name='language-create'),
    path('language/<int:pk>/update/', views.LanguageUpdate.as_view(), name='language-update'),
    path('language/<int:pk>/delete/', views.LanguageDelete.as_view(), name='language-delete'),

    path('bookinstances/', views.BookInstanceListView.as_view(), name='bookinstances'),
    path('bookinstance/<int:pk>/', views.BookInstanceDetailView.as_view(), name='bookinstance-detail'),
    path('bookinstance/create/', views.BookInstanceCreate.as_view(), name='bookinstance-create'),
    path('bookinstance/<int:pk>/update/', views.BookInstanceUpdate.as_view(), name='bookinstance-update'),
    path('bookinstance/<int:pk>/delete/', views.BookInstanceDelete.as_view(), name='bookinstance-delete'),

    path('tags/', views.TagListView.as_view(), name='tags'),
    path('tag/<int:pk>/', views.TagDetailView.as_view(), name='tag-detail'),
    path('tag/create/', views.TagCreate.as_view(), name='tag-create'),
    path('tag/<int:pk>/update/', views.TagUpdate.as_view(), name='tag-update'),
    path('tag/<int:pk>/delete/', views.TagDelete.as_view(), name='tag-delete'),

    path('records/', views.RecordListView.as_view(), name='records'),
    path('record/<int:pk>/', views.RecordDetailView.as_view(), name='record-detail'),
    path('record/create/', views.RecordCreate.as_view(), name='record-create'),
    path('record/<int:pk>/update/', views.RecordUpdate.as_view(), name='record-update'),
    path('record/<int:pk>/delete/', views.RecordDelete.as_view(), name='record-delete'),
]
