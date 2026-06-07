from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Book, Author, BookInstance, Genre, Language, Tag, Record
from catalog.forms import RenewBookForm, BookSearchForm


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }
    return render(request, 'catalog/index.html', context)


@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('catalog:index')

    borrowed = BookInstance.objects.filter(status='o').order_by('due_back')
    overdue = borrowed.filter(due_back__lt=date.today())

    context = {
        'num_books': Book.objects.count(),
        'num_authors': Author.objects.count(),
        'num_genres': Genre.objects.count(),
        'num_languages': Language.objects.count(),
        'num_tags': Tag.objects.count(),
        'num_instances': BookInstance.objects.count(),
        'num_available': BookInstance.objects.filter(status='a').count(),
        'num_borrowed': borrowed.count(),
        'num_overdue': overdue.count(),
        'recent_borrowed': borrowed[:10],
    }
    return render(request, 'catalog/staff_dashboard.html', context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                | Q(author__name__icontains=q)
                | Q(isbn__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = BookSearchForm(self.request.GET)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class BookDetailView(generic.DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_copies'] = self.object.bookinstance_set.filter(status='a')
        return context


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class GenreListView(generic.ListView):
    model = Genre
    paginate_by = 10


class GenreDetailView(generic.DetailView):
    model = Genre


class LanguageListView(generic.ListView):
    model = Language
    paginate_by = 10


class LanguageDetailView(generic.DetailView):
    model = Language


class BookInstanceListView(generic.ListView):
    model = BookInstance
    paginate_by = 10


class BookInstanceDetailView(generic.DetailView):
    model = BookInstance


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user, status__exact='o')
            .order_by('due_back')
        )


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            return HttpResponseRedirect(reverse('catalog:all-borrowed'))
    else:
        proposed_renewal_date = date.today() + timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'catalog/book_renew_librarian.html', context)


@login_required
def borrow_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk, status='a')

    if request.method == 'POST':
        due_date = date.today() + timedelta(weeks=3)
        book_instance.status = 'o'
        book_instance.borrower = request.user
        book_instance.due_back = due_date
        book_instance.save()

        Record.objects.create(
            book_instance=book_instance,
            borrower=request.user,
            borrow_date=date.today(),
        )

        messages.success(request, f'You have borrowed "{book_instance.book.title}". Due back: {due_date}.')
        return redirect('catalog:my-borrowed')

    context = {
        'book_instance': book_instance,
        'due_date': date.today() + timedelta(weeks=3),
    }
    return render(request, 'catalog/book_borrow_confirm.html', context)


@login_required
def return_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    is_owner = book_instance.borrower == request.user
    is_staff = request.user.has_perm('catalog.can_mark_returned')
    if not is_owner and not is_staff:
        return redirect('catalog:my-borrowed')

    if request.method == 'POST':
        record = Record.objects.filter(
            book_instance=book_instance, return_date__isnull=True
        ).first()
        if record:
            record.return_date = date.today()
            record.save()

        book_instance.status = 'a'
        book_instance.borrower = None
        book_instance.due_back = None
        book_instance.save()

        messages.success(request, f'You have returned "{book_instance.book.title}".')
        if is_staff and not is_owner:
            return redirect('catalog:all-borrowed')
        return redirect('catalog:my-borrowed')

    context = {'book_instance': book_instance}
    return render(request, 'catalog/book_return_confirm.html', context)


class BorrowHistoryListView(LoginRequiredMixin, generic.ListView):
    model = Record
    template_name = 'catalog/borrow_history.html'
    paginate_by = 10

    def get_queryset(self):
        return Record.objects.filter(borrower=self.request.user).order_by('-borrow_date')


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.add_author'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.change_author'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('catalog:authors')
    permission_required = 'catalog.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception:
            return HttpResponseRedirect(reverse("catalog:author-delete", kwargs={"pk": self.object.pk}))


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'tags']
    permission_required = 'catalog.add_book'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'tags']
    permission_required = 'catalog.change_book'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('catalog:books')
    permission_required = 'catalog.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception:
            return HttpResponseRedirect(reverse("catalog:book-delete", kwargs={"pk": self.object.pk}))


class GenreCreate(PermissionRequiredMixin, CreateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.add_genre'


class GenreUpdate(PermissionRequiredMixin, UpdateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.change_genre'


class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy('catalog:genres')
    permission_required = 'catalog.delete_genre'


class LanguageCreate(PermissionRequiredMixin, CreateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.add_language'


class LanguageUpdate(PermissionRequiredMixin, UpdateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.change_language'


class LanguageDelete(PermissionRequiredMixin, DeleteView):
    model = Language
    success_url = reverse_lazy('catalog:languages')
    permission_required = 'catalog.delete_language'


class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    fields = ['book', 'imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.add_bookinstance'


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    fields = ['imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.change_bookinstance'


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    success_url = reverse_lazy('catalog:bookinstances')
    permission_required = 'catalog.delete_bookinstance'


class TagListView(generic.ListView):
    model = Tag
    paginate_by = 10


class TagDetailView(generic.DetailView):
    model = Tag


class TagCreate(PermissionRequiredMixin, CreateView):
    model = Tag
    fields = ['name']
    permission_required = 'catalog.add_tag'


class TagUpdate(PermissionRequiredMixin, UpdateView):
    model = Tag
    fields = ['name']
    permission_required = 'catalog.change_tag'


class TagDelete(PermissionRequiredMixin, DeleteView):
    model = Tag
    success_url = reverse_lazy('catalog:tags')
    permission_required = 'catalog.delete_tag'


class RecordListView(generic.ListView):
    model = Record
    paginate_by = 10


class RecordDetailView(generic.DetailView):
    model = Record


class RecordCreate(PermissionRequiredMixin, CreateView):
    model = Record
    fields = ['book_instance', 'borrower', 'borrow_date', 'return_date']
    permission_required = 'catalog.add_record'


class RecordUpdate(PermissionRequiredMixin, UpdateView):
    model = Record
    fields = ['book_instance', 'borrower', 'borrow_date', 'return_date']
    permission_required = 'catalog.change_record'


class RecordDelete(PermissionRequiredMixin, DeleteView):
    model = Record
    success_url = reverse_lazy('catalog:records')
    permission_required = 'catalog.delete_record'
