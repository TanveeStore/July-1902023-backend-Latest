"""
ASGI config for tanvee project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from ChatApp import routings
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanvee.settings')

# application = get_asgi_application()

django.setup()

django_asgi_app = get_asgi_application()


# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     'websocket': URLRouter(
#         routings.websocket_urlpatterns,

#     )
# })



application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': AuthMiddlewareStack(URLRouter(
        routings.websocket_urlpatterns,

    ))
})
