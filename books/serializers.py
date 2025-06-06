from rest_framework import serializers
from .models import *
from .validators import *
from .constants import GENRE_CHOICES


class BookCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'authors', 'genre', 'publication_date', 'description', 'book_file', 'uploaded_by']
        read_only_fields = ['id', 'uploaded_by']

    def validate_title(self, value):
        value = custom_validate_title(value)
        request = self.context.get('request')
        user = request.user if request else None
        instance = self.instance  # Will be None for create

        if user:
            qs = Book.objects.filter(title__iexact=value.strip(), uploaded_by=user)
            if instance:
                qs = qs.exclude(pk=instance.pk)  # Exclude current book in update

            if qs.exists():
                raise serializers.ValidationError("You already have a book with this title.")

        return value    
    
    def validate_authors(self, value):
        return custom_validate_authors(value)
    
    def validate_genre(self, value):
        return custom_validate_genre(value)
    
    def validate_book_file(self,value):
        return custom_validate_pdf_file(value)

    def validate_publication_date(self, value):
        return custom_validate_publication_date(value)
    
    def validate_description(self, value):
        return custom_validate_description(value)
    



class BookListSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'authors', 'genre', 'publication_date', 'description', 'book_file', 'upload_date', 'uploaded_by']
    
    def get_uploaded_by(self, obj):
        return {
            "id": obj.uploaded_by.id,
            "username": obj.uploaded_by.username,
            "email": obj.uploaded_by.email
        }



#----------------------  Reading List Serializers --------------------

class ReadingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingList
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at'] 
          
    def validate_name(self, value):
        value = validate_reading_list_name(value)
        request = self.context.get('request')

        if request and request.user:
            if ReadingList.objects.filter(user=request.user, name__iexact=value.strip(), is_deleted=False).exists():
                raise serializers.ValidationError("You already have a reading list with this name.")

        return value


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'authors', 'genre', 'publication_date', 'description', 'book_file', 'upload_date']


class ReadingListItemSerializer(serializers.ModelSerializer):
    book = BookDetailSerializer(read_only=True)

    class Meta:
        model = ReadingListItem
        fields = ['id', 'order', 'book']

