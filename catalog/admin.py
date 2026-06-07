from django.contrib import admin

from .models import Author, Genre, Book, BookInstance, Language, Tag, Record

admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Tag)


class BooksInline(admin.TabularInline):
    model = Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birth', 'date_of_death')
    fields = ['name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre')
    inlines = [BooksInstanceInline]


admin.site.register(Book, BookAdmin)


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )


class RecordInline(admin.TabularInline):
    model = Record


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('book_instance', 'borrower', 'borrow_date', 'return_date')
    list_filter = ('borrow_date', 'return_date')
