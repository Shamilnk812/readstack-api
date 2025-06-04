from rest_framework.response import Response
from rest_framework import status


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        'status': 'error',
        'message': message
    }, status=status_code)


def success_response(message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        'status': 'success',
        'message': message,
        'data': data or {}
    }, status=status_code)