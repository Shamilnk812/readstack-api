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
    
