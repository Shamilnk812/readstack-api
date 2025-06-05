from django.db import models
from users.models import User
from .constants import *


class Book(models.Model):
    title = models.CharField(max_length=225)
    authors = models.CharField(max_length=255)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES, default='other')
    publication_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    book_file = models.FileField(upload_to='books/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_books")
    created_at = models.DateTimeField(auto_now_add=True)
    is_uploaded = models.BooleanField(default=False)
    upload_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    
    def __str__(self):
        return self.title
    


class ReadingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_lists')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    


class ReadingListItem(models.Model):
    reading_list = models.ForeignKey(ReadingList, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('reading_list', 'book')
        ordering = ['order']

    def __str__(self):
        return f"{self.book.title} in {self.reading_list.name} (Order {self.order})"    
