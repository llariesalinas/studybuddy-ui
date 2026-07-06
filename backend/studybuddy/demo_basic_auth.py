import base64

from django.conf import settings
from django.http import HttpResponse


class DemoBasicAuthMiddleware:
    """Gates every request behind a single shared HTTP Basic Auth credential.

    Only wired into MIDDLEWARE when DEMO_BASIC_AUTH_USER/DEMO_BASIC_AUTH_PASSWORD
    are set (see settings.py), so this has no effect on local dev or real
    production. See ADR-0005 for why Basic Auth was chosen over Vercel's paid
    Password Protection add-on.

    Credentials travel on X-Demo-Auth, not Authorization -- the app's own JWT
    Bearer tokens already own that header, and the two can't share it.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Browsers never attach custom headers to CORS preflight requests, so let
        # OPTIONS through unauthenticated -- CorsMiddleware (which runs after this
        # one) handles the preflight response. The actual request that follows
        # still goes through the check below.
        if request.method == 'OPTIONS':
            return self.get_response(request)

        # Render's health checker (and similar platform monitors) never sends
        # Basic Auth credentials, so let the liveness check through unauthenticated.
        if request.path == '/healthz':
            return self.get_response(request)

        # Media (avatars, enrollment-proof uploads, etc.) is rendered via plain <img>
        # tags, which can't attach the custom X-Demo-Auth header -- so it would 401
        # forever if gated here. Production already serves media without JWT auth for
        # the same reason (see the "serve media files unconditionally" fix); the demo
        # gate just needs the same carve-out.
        if request.path.startswith('/media/'):
            return self.get_response(request)

        header = request.META.get('HTTP_X_DEMO_AUTH', '')
        if header.startswith('Basic '):
            try:
                decoded = base64.b64decode(header[6:]).decode('utf-8')
                username, _, password = decoded.partition(':')
            except (ValueError, UnicodeDecodeError):
                username, password = '', ''
            if (
                username == settings.DEMO_BASIC_AUTH_USER
                and password == settings.DEMO_BASIC_AUTH_PASSWORD
            ):
                return self.get_response(request)

        response = HttpResponse('Authentication required', status=401)
        response['WWW-Authenticate'] = 'Basic realm="Studybuddy Demo"'
        return response
