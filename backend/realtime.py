import logging
import asyncio
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

def broadcast_update(event_type, payload):
    """
    Broadcast update to all connected WebSocket clients.
    Uses both channel layer (Redis when available) and direct broadcast (for InMemory).
    """
    message_data = {
        "type": event_type,
        "payload": payload,
    }
    
    # Try channel layer first (works with Redis)
    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                "updates",
                {
                    "type": "broadcast_update",
                    "data": message_data,
                },
            )
            logger.info(f"✅ Broadcast sent via channel layer: {event_type}")
        except Exception as e:
            logger.error(f"❌ Channel layer broadcast failed: {e}")
    
    # Also do direct broadcast for InMemory (Railway free tier without Redis)
    try:
        from backend.consumers import UpdateConsumer
        # Run async broadcast in the event loop
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If loop is already running, schedule the task
            asyncio.ensure_future(UpdateConsumer.broadcast_to_all(message_data))
        else:
            # If loop is not running, run until complete
            loop.run_until_complete(UpdateConsumer.broadcast_to_all(message_data))
        
        logger.info(f"✅ Direct broadcast sent to {len(UpdateConsumer.connected_clients)} clients: {event_type}")
    except Exception as e:
        logger.warning(f"⚠️  Direct broadcast failed (this is normal if no WebSocket clients connected): {e}")
