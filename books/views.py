from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.utils import timezone
from .serializers import *


# ---------------------- Book Management ---------------


class CreateBookView(APIView):
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
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        try:
            book = Book.objects.get(id=id, uploaded_by=request.user)
        except Book.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Book not found or you do not have permission to update it."
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookCreateUpdateSerializer(book, data=request.data, context={'request': request})

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
    


class UploadBookView(APIView):
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
    


class BookListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.filter(is_deleted=False, is_uploaded=True).order_by('-created_at')
        serializer = BookListSerializer(books, many=True)
        return Response({
            "status": "success",
            "message": "Books fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)




# --------------------------  Reading list management ( create and remove favorite books list)------------------

class CreateReadingListView(APIView):
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
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        reading_lists = ReadingList.objects.filter(user=request.user, is_deleted=False)
        if not reading_lists.exists():
            return Response({
                "status": "info",
                "message": "You don't have any reading lists. Please create one.",
            }, status=status.HTTP_200_OK)
        
        serializer = ReadingListSerializer(reading_lists, many=True)
        return Response({
            "status": "success",
            "message": "Reading lists fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        



# ------------------------ Add and Remove Books to reading list (Add to favorite Books) ---------------------

class AddBookToReadingListView(APIView):
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
        
        if ReadingListItem.objects.filter(reading_list=reading_list, book=book).exists():
            return Response({
                "status": "error",
                "message": f"Book {book.title} already in this reading list.",
            }, status=status.HTTP_400_BAD_REQUEST)
        

        next_order = reading_list.items.count() + 1
       
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


        

class ReorderBooksInReadingListView(APIView):
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
        

        existing_items = ReadingListItem.objects.filter(
            reading_list=reading_list,
            book_id__in=book_ids
        )
        
        print('count ',existing_items.count())
        print('items',existing_items)
        print('lenghttt',len(book_ids))
        if existing_items.count() != len(book_ids):
            return Response({
                "status": "error",
                "message": "One or more books do not belong to this reading list."
            }, status=status.HTTP_400_BAD_REQUEST)
        

          # Update order
        for position, book_id in enumerate(book_ids, start=1):
            ReadingListItem.objects.filter(
                reading_list=reading_list,
                book_id=book_id
            ).update(order=position)

        return Response({
            "status": "success",
            "message": "Book order updated successfully."
        }, status=status.HTTP_200_OK)



class GetReadingListItems(APIView):
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


