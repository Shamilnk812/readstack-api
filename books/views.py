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
            "message": "Book deleted successfully ."
        }, status=status.HTTP_200_OK)
    


class UploadBookView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            book = Book.objects.get(id=id, uploaded_by=request.user, is_deleted=False)

        except Book.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Book not found or you're not authorized."
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

    def get(self, request, id):
        books = Book.objects.filter(is_deleted=False, is_uploaded=True).order_by('-created_at')
        serializer = BookListSerializer(books, many=True)
        return Response({
            "status": "success",
            "message": "Books fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


