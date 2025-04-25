import os
from django.core.exceptions import DisallowedHost
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skate_results.settings")
_django_app = get_wsgi_application()

def application(environ, start_response):
    # If the ALB is probing /ping with some Host header, just return 200 OK here
    if environ.get("PATH_INFO") == "/ping":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"pong"]

    try:
        # Delegate everything else back to Django
        return _django_app(environ, start_response)
    except DisallowedHost:
        # If some other request has a bad Host, let it 400
        start_response("400 Bad Request", [("Content-Type", "text/plain")])
        return [b"Bad Host"]
