class CSRFDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Debug CSRF token
        if request.method == 'POST':
            csrf_token = request.POST.get('csrfmiddlewaretoken', 'NOT FOUND')
            print(f"CSRF Debug - Token: {csrf_token[:20] if len(csrf_token) > 20 else csrf_token}")
            print(f"CSRF Debug - Session: {request.session.session_key}")
        
        response = self.get_response(request)
        return response 