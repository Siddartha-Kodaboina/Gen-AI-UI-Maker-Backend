class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
        return response