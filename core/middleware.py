import logging

logger = logging.getLogger(__name__)

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log every request
        logger.info(
            f"{request.method} {request.get_full_path()} GET={request.GET.dict()}"
        )
        return self.get_response(request)
