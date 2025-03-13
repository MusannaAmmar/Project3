from rest_framework.response import Response
from rest_framework import status
from urllib.parse import urlparse

SUCCESS_CODES = [
    status.HTTP_200_OK,
    status.HTTP_201_CREATED,
    status.HTTP_202_ACCEPTED,
    status.HTTP_204_NO_CONTENT,
    status.HTTP_206_PARTIAL_CONTENT
]


def map_response(status_code=status.HTTP_200_OK, message="success", data=None, success=True, error=None):
    status_str = 'success'
    if status_code not in SUCCESS_CODES:
        if message == 'success':
            message = 'An Error'
            status_str = 'fail'

    response = {
        # "status": status_str,
        "message": message,
        'success': success
    }

    if data is not None:  # Only include 'data' if it is not None or empty
        response["data"] = data
    if error:
        response["error"] = error
        response['success'] = False

    return Response(response, status=status_code)


def get_relative_path(full_url):
    parts = full_url.split('/')  
    last_three_parts = parts[-3:] 
    return f"media/{'/'.join(last_three_parts)}" 