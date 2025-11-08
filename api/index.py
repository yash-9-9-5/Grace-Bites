"""
Vercel serverless function wrapper for Django application.
This file allows Django to run on Vercel's serverless infrastructure.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grace_bites_project.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from io import BytesIO

# Initialize Django application
django_app = get_wsgi_application()

def handler(request):
    """
    Handle incoming HTTP requests for Vercel serverless functions.
    
    Vercel passes a request object with:
    - method: HTTP method (GET, POST, etc.)
    - path: URL path
    - headers: dict of headers
    - body: request body as string
    - query: query parameters dict
    
    Returns a dict with:
    - statusCode: HTTP status code
    - headers: dict of response headers
    - body: response body as string
    """
    # Create WSGI environment
    environ = {
        'REQUEST_METHOD': request.get('method', 'GET'),
        'PATH_INFO': request.get('path', '/'),
        'QUERY_STRING': '',
        'CONTENT_TYPE': request.get('headers', {}).get('content-type', ''),
        'CONTENT_LENGTH': str(len(request.get('body', '') or '')),
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': request.get('headers', {}).get('x-forwarded-proto', 'https'),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
        'SERVER_NAME': request.get('headers', {}).get('host', ''),
        'SERVER_PORT': request.get('headers', {}).get('x-forwarded-port', '443'),
    }
    
    # Add query string if present
    if 'query' in request:
        from urllib.parse import urlencode
        environ['QUERY_STRING'] = urlencode(request['query'])
    
    # Add request body
    body = request.get('body', '') or ''
    environ['wsgi.input'] = BytesIO(body.encode() if isinstance(body, str) else body)
    
    # Add all headers to environ
    for key, value in request.get('headers', {}).items():
        environ_key = f'HTTP_{key.upper().replace("-", "_")}'
        environ[environ_key] = value
    
    # Create Django request
    django_request = WSGIRequest(environ)
    
    # Process through Django
    response = django_app(django_request)
    
    # Convert Django response to Vercel format
    return {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.content.decode('utf-8') if isinstance(response.content, bytes) else str(response.content)
    }

