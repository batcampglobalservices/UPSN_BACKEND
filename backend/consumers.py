import json
from channels.generic.websocket import AsyncWebsocketConsumer

class UpdateConsumer(AsyncWebsocketConsumer):
    # Store all connected clients for in-memory broadcasting
    connected_clients = set()
    
    async def connect(self):
        # Add to in-memory set for direct broadcasting
        UpdateConsumer.connected_clients.add(self)
        
        # Also add to channel layer group (for Redis when available)
        if self.channel_layer:
            await self.channel_layer.group_add("updates", self.channel_name)
        
        await self.accept()
        print(f"✅ WebSocket client connected. Total clients: {len(UpdateConsumer.connected_clients)}")

    async def disconnect(self, close_code):
        # Remove from in-memory set
        UpdateConsumer.connected_clients.discard(self)
        
        # Also remove from channel layer group
        if self.channel_layer:
            await self.channel_layer.group_discard("updates", self.channel_name)
        
        print(f"🔌 WebSocket client disconnected. Total clients: {len(UpdateConsumer.connected_clients)}")

    async def receive(self, text_data):
        # Echo received message (for testing)
        await self.send(text_data=json.dumps({"message": "Received", "data": text_data}))

    async def broadcast_update(self, event):
        """Called by channel layer when using Redis"""
        await self.send(text_data=json.dumps(event["data"]))
    
    @classmethod
    async def broadcast_to_all(cls, message_data):
        """Direct broadcast to all connected clients (works without Redis)"""
        disconnected = []
        for client in cls.connected_clients:
            try:
                await client.send(text_data=json.dumps(message_data))
            except Exception as e:
                print(f"❌ Failed to send to client: {e}")
                disconnected.append(client)
        
        # Clean up disconnected clients
        for client in disconnected:
            cls.connected_clients.discard(client)
