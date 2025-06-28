from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from .serializers import *


# ---------------------- Book Management ---------------


class CreateBookView(APIView):
    """
    Handles creation of a new book entry by an authenticated user.

    This view allows users to upload and register a new book in the system by providing details
    such as title, authors, genre, publication date, an optional description, and a book file (PDF).
    It validates each field using custom validation logic to ensure data quality and prevents duplicate
    titles by the same user. 

    Expected Input:
    - title: str (required, must be unique per user)
    - authors: str (required)
    - genre: str (required, must be one of the predefined choices)
    - publication_date: date (required, must be valid)
    - description: str (optional)
    - book_file: file (required, must be a valid PDF file)

    Returns:
    - 201 Created: If the book is successfully uploaded and created
    - 400 Bad Request: If validation fails for any of the fields
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookCreateUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(uploaded_by=request.user)
            return Response({
                "status": "success",
                "message": "Book created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)




class UpdateBookView(APIView):
    """
    Handles updating an existing book entry created by the authenticated user.

    This view allows a user to update the details of a book they previously created. It verifies
    ownership of the book based on the provided `id` and the authenticated user. The user can update
    fields such as title, authors, genre, publication date, description, and book file.
    All input is validated using the (BookCreateUpdateSerializer) serializer.

    Expected Input:
    - id: int (URL parameter, required, must refer to a book created by the user)
    - title: str (required)
    - authors: str (required)
    - genre: str (required)
    - publication_date: date (required)
    - description: str (optional)
    - book_file: file (required, must be a valid PDF file)

    Returns:
    - 200 OK: If the book is successfully updated or if not data provided
    - 400 Bad Request: If validation fails
    - 404 Not Found: If the book does not exist or does not belong to the user
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        data = request.data

        try:
            book = Book.objects.get(id=id, uploaded_by=request.user)
        except Book.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Book not found or you do not have permission to update it."
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if no data provided 
        if not any(field in data for field in ['id', 'title', 'authors', 'genre', 'publication_date', 'description', 'book_file', 'uploaded_by']):
            return Response({
                "status": "info",
                "message": "No data provided to update."
            }, status=status.HTTP_200_OK)
        
        serializer = BookCreateUpdateSerializer(book, data=data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save(uploaded_by=request.user)
            return Response({
                "status": "success",
                "message": "Book updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class  DeleteBookView(APIView):
    """
    Handles soft deletion of a book created by the authenticated user.

    This view allows a user to delete a book they have created by marking it as deleted 
    (soft delete). The book is not permanently removed from the database but is flagged 
    with `is_deleted = True`, effectively excluding it from future queries.

    Expected Input:
    - id: int (URL parameter, required, must refer to a book created by the user)

    Returns:
    - 200 OK: If the book is successfully soft deleted
    - 404 Not Found: If the book does not exist, is already deleted, or does not belong to the user
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            book = Book.objects.get(id=id, uploaded_by=request.user, is_deleted=False)

        except Book.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Book not found or already deleted."
            }, status=status.HTTP_404_NOT_FOUND)
        
        book.is_deleted = True
        book.save()

        return Response({
            "status": "success",
            "message": "Book deleted successfully .",
             "data": {
                    "book_id": book.id,
                    "title": book.title
                }

        }, status=status.HTTP_200_OK)
    


#------------------------- Upload Books -------------- 

class UploadBookView(APIView):
    """
    Handles uploading (publishing) a book by the authenticated user.

    This view marks a previously created book as uploaded, making it publicly accessible.
    It ensures the book exists, belongs to the user, is not already uploaded, and has a valid
    book file. Once validated, it sets `is_uploaded` to True and records the upload timestamp.

    Expected Input:
    - id: int (URL parameter, required, must refer to a book created by the user)

    Conditions:
    - Book must not be already uploaded
    - Book must have a valid file attached

    Returns:
    - 200 OK: If the book is successfully uploaded
    - 400 Bad Request: If the book is already uploaded or the book file is missing
    - 404 Not Found: If the book does not exist or does not belong to the user
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            book = Book.objects.get(id=id, uploaded_by=request.user, is_deleted=False)

        except Book.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Book not found"
            }, status=status.HTTP_404_NOT_FOUND)    
        

        if book.is_uploaded:
            return Response({
                "status": "error",
                "message": "Book is already uploaded.",
                "data": {
                    "book_id": book.id,
                    "title": book.title
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        if not book.book_file:
            return Response({
                "status": "error",
                "message": "Failed to upload . Book file is missing, Please check the file before publishing."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        book.is_uploaded = True
        book.upload_date = timezone.now()  
        book.save()

        return Response({
            "status": "success",
            "message": "Book uploaded successfully.",
            "data": {
                "book_id": book.id,
                "title": book.title,
            }
        }, status=status.HTTP_200_OK)
    


# ----------------------- List all uploaded books to all other users -------------------

class BookListView(APIView):
    """
    Retrieves a list of all uploaded books visible to authenticated users.

    This view returns all books that are marked as uploaded (`is_uploaded=True`) and not deleted
    (`is_deleted=False`). The books are ordered by their creation date in descending order, 
    showing the most recently uploaded books first.

    Access is restricted to authenticated users.

    Returns:
    - 200 OK: A list of all publicly uploaded books
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.filter(is_deleted=False, is_uploaded=True).order_by('-created_at')

        paginator = PageNumberPagination()
        paginator.page_size = 12
        paginated_qs = paginator.paginate_queryset(books, request)

        serializer = BookListSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)
       



# --------------------------  Reading list management ( create and remove favorite books list)------------------

class CreateReadingListView(APIView):
    """
    Creates a new reading list for the authenticated user.

    This view allows a user to create a personalized reading list by providing a unique name.
    The name is validated to ensure it meets length and format requirements.
    Users cannot create multiple reading lists with the same name that are not deleted.

    Expected Input:
    - name: string (required) — Name of the reading list, validated for uniqueness per user.

    Returns:
    - 201 Created: On successful creation with reading list details
    - 400 Bad Request: If validation fails or a reading list with the same name already exists
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        serializer = ReadingListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "status": "success",
                "message": "Reading list created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "error",
            "message": "Failed to create reading list.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)      
    


class DeleteReadingListView(APIView):
    """
    Soft deletes a reading list belonging to the authenticated user.

    This endpoint marks the specified reading list as deleted without removing it from the database.
    Only reading lists owned by the requesting user and not already deleted can be deleted.

    Path Parameters:
    - reading_list_id (int): ID of the reading list to be deleted.

    Responses:
    - 200 OK: Reading list successfully marked as deleted.
    - 404 Not Found: Reading list not found or does not belong to the user.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, reading_list_id):
        try:
            reading_list  = ReadingList.objects.get(id=reading_list_id, user=request.user, is_deleted=False)

        except ReadingList.DoesNotExist:
             return Response({
                "status": "error",
                "message": "Reading list not found .",
            }, status=status.HTTP_404_NOT_FOUND)    
        
        reading_list_name = reading_list.name
        reading_list.is_deleted = True
        reading_list.save()

        return Response({
            "status": "success",
            "message":  f"Reading list '{reading_list_name}' deleted successfully.",
        }, status=status.HTTP_200_OK)
    


class GetReadingListView(APIView):
    """
    Retrieve all reading lists (non-deleted) belonging to the authenticated user.
    Returns a list of reading lists created by the requesting user.
    If no reading lists are found, returns an informational message.

    Response:
        - 200 OK with reading lists data if any exist.
        - 200 OK with an info message if no reading lists are found.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        reading_lists = ReadingList.objects.filter(user=request.user, is_deleted=False)
        if not reading_lists.exists():
            return Response({
                "status": "info",
                "message": "You don't have any reading lists. Please create one.",
            }, status=status.HTTP_200_OK)
        
        paginator = PageNumberPagination()
        paginator.page_size = 8
        paginated_qs = paginator.paginate_queryset(reading_lists, request)
        serializer = ReadingListSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)
       
        



# ------------------------ Add and Remove Books to reading list (Add to favorite Books) ---------------------

class AddBookToReadingListView(APIView):
    """
    Add a book to a user's specific reading list.

    Parameters:
        - reading_list_id (int): ID of the reading list to add the book to (from URL path).
        - book_id (int): ID of the book to add (from request body).

    - Validates that the reading list exists and belongs to the user.
    - Validates that the book exists, is uploaded, and not deleted.
    - Prevents adding duplicate books to the same reading list.
    - Assigns the book the next order position in the reading list.
    - Creates a ReadingListItem to link the book and reading list.

    Responses:
        - 201 Created: Book added successfully.
        - 400 Bad Request: Book already in the reading list.
        - 404 Not Found: Reading list or book not found/unavailable.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, reading_list_id):
        book_id = request.data.get('book_id')

        try:
            reading_list = ReadingList.objects.get(id=reading_list_id, user=request.user, is_deleted=False)

        except ReadingList.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Reading list not found.",
            }, status=status.HTTP_404_NOT_FOUND)
        

        try:
            book = Book.objects.get(id=book_id, is_deleted=False,  is_uploaded=True)
        except Book.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Book not found or unavailable.",
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the book is already in the reading list to avoid duplicates
        if ReadingListItem.objects.filter(reading_list=reading_list, book=book).exists():
            return Response({
                "status": "error",
                "message": f"Book {book.title} already in this reading list.",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate the next order index for the new book in the reading list
        next_order = reading_list.items.count() + 1
       
        # Create the ReadingListItem linking the book and the reading list
        ReadingListItem.objects.create(
            reading_list=reading_list,
            book=book,
            order=next_order
        )

        return Response({
            "status": "success",
            "message": f'Book {book.title} has been added to reading list {reading_list.name}.',
        }, status=status.HTTP_201_CREATED)
    



class RemoveBookFromReadingListView(APIView):
    """
    Remove a book from a user's specific reading list.

    Permissions:
        - Requires the user to be authenticated.

    Parameters:
        - reading_list_id (int): ID of the reading list from which the book should be removed (from URL path).
        - book_id (int): ID of the book to remove (from request body).

    Behavior:
        - Validates that the reading list exists and belongs to the user.
        - Validates that the book exists.
        - Checks if the book is present in the specified reading list.
        - Removes the book from the reading list.
        - Reorders the remaining books in the reading list to maintain continuous order.

    Responses:
        - 200 OK: Book removed successfully.
        - 400 Bad Request: Missing book_id or book not in the reading list.
        - 404 Not Found: Reading list or book not found.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, reading_list_id):
        book_id = request.data.get('book_id')

        if not book_id:
            return Response({
                "status": "error",
                "message": "Book ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reading_list = ReadingList.objects.get(id=reading_list_id, user=request.user, is_deleted=False)
        except ReadingList.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Reading list not found.",
            }, status=status.HTTP_404_NOT_FOUND)
        

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Book not found.",
            }, status=status.HTTP_404_NOT_FOUND)  
        
        try:
            item = ReadingListItem.objects.get(reading_list=reading_list, book=book)
        except ReadingListItem.DoesNotExist:
            return Response({
                "status": "error",
                "message": f"Book {book.title} is not in this reading list.",
            }, status=status.HTTP_400_BAD_REQUEST)
        

        item.delete()

        # Reorder remaining items
        items = reading_list.items.order_by('order')
        for index, item in enumerate(items, start=1):
            if item.order != index:
                item.order = index
                item.save()

        return Response({
            "status": "success",
            "message": f"Book {book.title} removed from reading list."
        }, status=status.HTTP_200_OK)


        
#------------------------------ Re-order books in user-specific order in a reading list -----------------------------

class ReorderBooksInReadingListView(APIView):
    """
    Reorder books in a user's reading list based on the provided order of book IDs.

    This view allows authenticated users to update the order of books within their own reading list
    by passing a list of book IDs (book_ids) in the desired sequence.

    Args:
        reading_list_id (int): The ID of the reading list to reorder.
            
    Behavior:
        - The reading list must exist and belong to the authenticated user.
        - All provided book IDs must belong to the reading list.

    Responses:
        - 200 OK: Book order updated successfully.
        - 400 Bad Request: One or more books do not belong to this reading list.
        - 404 Not Found: Reading list not found.    
    """

    permission_classes = [IsAuthenticated]

    def put(self, request,  reading_list_id):
        book_ids = request.data.get('book_ids', [])

        try:
            reading_list = ReadingList.objects.get(id=reading_list_id, user=request.user, is_deleted=False)
        except ReadingList.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Reading list not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get existing items from the reading list matching the provided book IDs
        existing_items = ReadingListItem.objects.filter(
            reading_list=reading_list,
            book_id__in=book_ids
        )
        
        # Check if all book IDs belong to the reading list
        if existing_items.count() != len(book_ids):
            return Response({
                "status": "error",
                "message": "One or more books do not belong to this reading list."
            }, status=status.HTTP_400_BAD_REQUEST)
        

        # Update the order field on ReadingListItem according to the user-provided sequence
        for position, book_id in enumerate(book_ids, start=1):
            ReadingListItem.objects.filter(
                reading_list=reading_list,
                book_id=book_id
            ).update(order=position)

        return Response({
            "status": "success",
            "message": "Book order updated successfully."
        }, status=status.HTTP_200_OK)



#------------------------ List all items of a specific reading list ---------------

class GetReadingListItems(APIView):
    """
    Retrieve all books (items) within a specific reading list for the authenticated user.

    Parameters:
        - URL parameter: reading_list_id (int) - The ID of the reading list whose items are to be fetched.

    Behavior:
        - Validates that the reading list exists, belongs to the authenticated user, and is not deleted.
        - Fetches all the ReadingListItem objects associated with the reading list.
        - Serializes the list items along with detailed book information.

    Responses:
        - 200 OK: Returns a list of books in the specified reading list.
        - 404 Not Found: If the reading list does not exist or does not belong to the user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, reading_list_id):
        try:
            reading_list = ReadingList.objects.get(id=reading_list_id, user=request.user, is_deleted=False)
        except ReadingList.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Reading list not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        items = reading_list.items.all()  
        
        serializer = ReadingListItemSerializer(items, many=True)
        
        return Response({
            "status": "success",
            "message": f"Books fetched for reading list '{reading_list.name}'.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


