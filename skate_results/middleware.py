# skate_results/middleware.py

import logging
from django.middleware.csrf import CsrfViewMiddleware

logger = logging.getLogger("django.request")  # or "django.csrf"

class VerboseCsrfMiddleware(CsrfViewMiddleware):
    def _reject(self, request, reason):
        logger.error(
            f"CSRF FAILED on {request.path} — reason={reason!r}, "
            f"Host={request.get_host()}, Origin={request.META.get('HTTP_ORIGIN')}"
        )
        return super()._reject(request, reason)
