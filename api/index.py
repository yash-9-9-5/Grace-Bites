"""
Vercel serverless function wrapper for Django application.
This file allows Django to run on Vercel's serverless infrastructure.
"""
import os
import sys
import traceback
from pathlib import Path
from io import BytesIO

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module BEFORE any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grace_bites_project.settings')

# Import Django components
from django.core.wsgi import get_wsgi_application
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse

# Initialize Django application (lazy initialization)
_django_app = None

def get_django_app():
    """Lazy initialization of Django app to catch errors early."""
    global _django_app
    if _django_app is None:
        try:
            _django_app = get_wsgi_application()
        except Exception as e:
            # Log initialization error
            error_msg = f"Django initialization failed: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            raise
    return _django_app

def handler(request):
    """
    Handle incoming HTTP requests for Vercel serverless functions.
    
    Vercel's Python runtime passes request as an object with attributes:
    - request.method: HTTP method string
    - request.path: URL path string
    - request.headers: dict-like object of headers
    - request.body: request body (string or bytes)
    - request.query: dict of query parameters (optional)
    
    Returns a dict with:
    - statusCode: HTTP status code (int)
    - headers: dict of response headers
    - body: response body as string
    """
    try:
        # Get Django app (with error handling)
        django_app = get_django_app()
        
        # Extract request data - handle both dict and object formats
        if hasattr(request, 'method'):
            method = request.method
            path = getattr(request, 'path', '/')
            headers = getattr(request, 'headers', {})
            body = getattr(request, 'body', '')
            query = getattr(request, 'query', {})
        else:
            # Fallback for dict-like requests
            method = request.get('method', 'GET')
            path = request.get('path', '/')
            headers = request.get('headers', {})
            body = request.get('body', '')
            query = request.get('query', {})
        
        # Convert headers to dict if needed
        if not isinstance(headers, dict):
            headers = dict(headers) if hasattr(headers, 'items') else {}
        
        # Build query string
        query_string = ''
        if query:
            from urllib.parse import urlencode
            query_string = urlencode(query)
        
        # Prepare request body
        if isinstance(body, str):
            body_bytes = body.encode('utf-8')
        elif body is None:
            body_bytes = b''
        else:
            body_bytes = body
        
        # Create WSGI environment dictionary
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': headers.get('content-type', ''),
            'CONTENT_LENGTH': str(len(body_bytes)),
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': headers.get('x-forwarded-proto', 'https'),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
            'SERVER_NAME': headers.get('host', 'localhost'),
            'SERVER_PORT': headers.get('x-forwarded-port', '443'),
            'wsgi.input': BytesIO(body_bytes),
        }
        
        # Add HTTP headers to environ (Django expects HTTP_ prefix)
        for key, value in headers.items():
            # Convert header name to HTTP_ format
            header_key = f'HTTP_{key.upper().replace("-", "_")}'
            environ[header_key] = str(value)
        
        # Add special headers
        if 'host' in headers:
            environ['HTTP_HOST'] = headers['host']
        if 'x-forwarded-for' in headers:
            environ['HTTP_X_FORWARDED_FOR'] = headers['x-forwarded-for']
        if 'x-forwarded-proto' in headers:
            environ['HTTP_X_FORWARDED_PROTO'] = headers['x-forwarded-proto']
        
        # Create Django WSGI request
        django_request = WSGIRequest(environ)
        
        # Process request through Django
        response = django_app(django_request)
        
        # Convert Django response to Vercel format
        response_headers = {}
        for key, value in response.headers.items():
            response_headers[key] = str(value)
        
        # Handle response body
        if isinstance(response.content, bytes):
            response_body = response.content.decode('utf-8', errors='replace')
        else:
            response_body = str(response.content)
        
        return {
            'statusCode': response.status_code,
            'headers': response_headers,
            'body': response_body
        }
        
    except Exception as e:
        # Return error response
        error_trace = traceback.format_exc()
        error_msg = f"Function invocation failed: {str(e)}\n{error_trace}"
        print(error_msg, file=sys.stderr)
        
        # Return a proper error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
            },
            'body': f"""
            <html>
            <head><title>Server Error</title></head>
            <body>
                <h1>500 Internal Server Error</h1>
                <p>An error occurred while processing your request.</p>
                <pre>{error_msg}</pre>
                <p><strong>Common causes:</strong></p>
                <ul>
                    <li>Database connection issues (SQLite won't work on Vercel)</li>
                    <li>Missing environment variables</li>
                    <li>Import errors</li>
                    <li>Settings configuration issues</li>
                </ul>
            </body>
            </html>
            """
        }

