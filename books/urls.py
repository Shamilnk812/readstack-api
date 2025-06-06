from django.urls import path
from .views import * 

urlpatterns = [
    path('create/', CreateBookView.as_view(), name='create-book'),
    path('update/<int:id>/',UpdateBookView.as_view(), name='update-book'),
    path('delete/<int:id>/', DeleteBookView.as_view(), name='delete-book'),
    path('upload/<int:id>/', UploadBookView.as_view(), name='upload-book'),
    path('list/', BookListView.as_view(), name='list-book'),

    path('create-reading-list/', CreateReadingListView.as_view(), name='create-reading-list'),
    path('delete-reading-list/<int:reading_list_id>/', DeleteReadingListView.as_view(), name='delete-reading-list'),
    path('get-reading-lists/', GetReadingListView.as_view(), name='get-reading-lists'),

    path('add-to-reading-list/<int:reading_list_id>/', AddBookToReadingListView.as_view(), name='add-to-reading-list'),
    path('remove-from-reading-list/<int:reading_list_id>/', RemoveBookFromReadingListView.as_view(), name='remove-from-reading-list'),
    path('reorder-reading-list/<int:reading_list_id>/', ReorderBooksInReadingListView.as_view(), name='reorder-reading-list'),
    path('get-reading-list-items/<int:reading_list_id>/', GetReadingListItems.as_view(), name='get-reading-list-items'),
    
    
]