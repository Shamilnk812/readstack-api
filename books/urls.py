from django.urls import path
from .views import * 

urlpatterns = [
    path('create/', CreateBookView.as_view(), name='create-book'),
    path('update/<int:id>/',UpdateBookView.as_view(), name='update-book'),
    path('delete/<int:id>/', DeleteBookView.as_view(), name='delete-book'),
    path('list/', BookListView.as_view(), name='list-book'),

    path('create-reading-list/', CreateReadingListView.as_view(), name='create-reading-list'),
    path('delete-reading-list/<int:reading_list_id>/', DeleteReadingListView.as_view(), name='delete-reading-list'),
    
    
]