import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

def broadcast_update(event_type, payload):
    channel_layer = get_channel_layer()
    if not channel_layer:
        logger.warning("Channel layer is not configured; skipping realtime broadcast for %s", event_type)
        return

    async_to_sync(channel_layer.group_send)(
        "updates",
        {
            "type": "broadcast_update",
            "data": {
                "type": event_type,
                "payload": payload,
            },
        },
    )
