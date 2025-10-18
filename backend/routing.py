from channels.routing import URLRouter
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/updates/", consumers.UpdateConsumer.as_asgi()),
]

# Legacy support
from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
