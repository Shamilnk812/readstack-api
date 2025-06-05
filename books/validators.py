import re
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.html import strip_tags
from datetime import date
from .models import Book
from .constants import GENRE_CHOICES
import os



def custom_validate_title(title):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE)
    
    title = title.strip().title()

    if not title :
        raise ValidationError("Title cannot be empty. Please enter a valid title.")
    
    if '__' in title or '..' in title or '++' in title or '--' in title:
        raise serializers.ValidationError("Title contains invalid repeated symbols like '__' or '..'.")
    
    # No only special characters
    if re.fullmatch(r'[^A-Za-z0-9]+', title):
        raise serializers.ValidationError("Title cannot be only special characters.")
    
    # No start/end with special characters
    if re.match(r'^[^\w]', title) or re.search(r'[^\w]$', title):
        raise serializers.ValidationError("Title cannot start or end with a special character.")
    
    # No emojis
    if emoji_pattern.search(title):
        raise serializers.ValidationError("Title cannot contain emojis or non-text symbols.")
    
     # No disallowed characters
    if not re.match(r'^[\w\s.,!\'"()-]+$', title):
        raise serializers.ValidationError("Title contains unsupported characters. Use only letters, numbers, and basic punctuation.")
    
    # Prevent HTML/JS tags (e.g., <script>)
    stripped = strip_tags(title)
    if stripped != title:
        raise serializers.ValidationError("Title contains HTML or script tags.")
    
    return title




def custom_validate_authors(authors):
    authors = authors.strip()
    if not authors :
        raise ValidationError("Author field cannot be empty. Please enter a valid auther name")
    
    # Prevent disallowed characters
    if not re.match(r'^[\w\s.,]+$', authors):
        raise ValidationError("Authors field contains unsupported characters.")

    # No emojis 
    emoji_pattern = re.compile(
        "[" 
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE
    )
    if emoji_pattern.search(authors):
        raise ValidationError("Authors field cannot contain emojis.")
    
    # Prevent HTML/JS tags (e.g., <script>)
    stripped = strip_tags(authors)
    if stripped != authors:
        raise serializers.ValidationError("Authors contains HTML or script tags. Please enter a valid author name")
    

    # Split by comma to validate individual author names
    author_list = [name.strip() for name in authors.split(',') if name.strip()]
    if not author_list:
        raise ValidationError("No valid author names found.")

    for name in author_list:
        if len(name) < 1:
            raise ValidationError(f"Author name '{name}' is too short.")
        if re.fullmatch(r'[^A-Za-z. ]+', name):
            raise ValidationError(f"Author name '{name}' contains invalid characters.")
        if '__' in name or '..' in name or '++' in name or '--' in name:
            raise ValidationError(f"Author name '{name}' contains invalid repeated symbols.")

    # Format each author to Title Case
    formatted_authors = ', '.join([name.title() for name in author_list])
    
    return formatted_authors



def custom_validate_genre(genre_name):
    allowed_genres = [choice[0] for choice in GENRE_CHOICES]
    normalized_value = genre_name.strip().lower()
    
    # Check if given genre is a valid one
    if normalized_value not in allowed_genres:
        raise serializers.ValidationError(
            f"Invalid genre. Allowed genres are: {', '.join(allowed_genres)}."
        )
        
    return normalized_value
    


def custom_validate_pdf_file(value):
    if not value:
        raise ValidationError("File is required.")
    
    # Check file extension
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError("Only PDF files are allowed.")
    return value


def custom_validate_publication_date(value):
    if not value:
        raise serializers.ValidationError("Publication date cannot be empty. Please provide a valid date.")

    today = date.today()
    
    # Ensure the publication date is not in the future
    if value > today:
        raise serializers.ValidationError("Publication date cannot be in the future.")
    
    # Check if the publication year is realistic (not too far in the past)
    if value.year < 1000:
        raise serializers.ValidationError("Publication date seems unrealistically old.")

    return value


def custom_validate_description(description):
    description = description.strip()
    
    # If description is empty (optional field), return early
    if not description:
        return description
    
    # Limit maximum length
    if len(description) > 2000:
        raise ValidationError("Description cannot exceed 2000 characters.")
    
    # Enforce a minimum length if description is provided (e.g., 10 chars)
    if len(description) < 10:
        raise ValidationError("Description is too short. Please provide more details.")
    
    # Prevent presence of HTML or script tags 
    stripped = strip_tags(description)
    if stripped != description:
        raise ValidationError("Description contains HTML or script tags, which are not allowed.")
    
    # Prevent excessive repeated characters (e.g., "!!!!", ".....")
    if re.search(r'(.)\1{4,}', description):
        raise ValidationError("Description contains excessive repeated characters.")

    # Avoid only special characters (must contain at least one letter or number)
    if not re.search(r'[A-Za-z0-9]', description):
        raise ValidationError("Description must contain at least some letters or numbers.")
    
    # add more like if contunues __ any special characters
    return description



# -------------------------- Reading List Validation ---------------------

def validate_reading_list_name(name):
    value = name.strip()

    # Length check
    if len(value) < 3 :
        raise ValidationError("Reading list name must be at least 3 charaters long")
    if len(value) > 50 :
        raise serializers.ValidationError("Name must be between 3 and 50 characters.")

    # Format check ( only letters, numbers, spaces, hyphens, and underscores allowed)
    if not re.match(r'^[\w\s-]+$', value):
        raise ValidationError("Name can only contain letters, numbers, spaces, hyphens, and underscores.")
    
    # Prevent presence of HTML or script tags 
    stripped = strip_tags(value)
    if stripped != value:
        raise ValidationError("Readin list name contains HTML or script tags, which are not allowed.")
    
    return value

