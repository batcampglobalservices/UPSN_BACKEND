from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def broadcast_update(event_type, payload):
    channel_layer = get_channel_layer()
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
