from django.http import Http404

class BlockNonHtmxRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.is_ajax():
            raise Http404
        return self.get_response(request)