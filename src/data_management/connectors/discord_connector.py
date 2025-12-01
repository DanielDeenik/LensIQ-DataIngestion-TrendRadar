"""
Discord Data Connector for LensIQ
Ingests unstructured data from Discord for trend analysis
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    logging.warning("discord.py not installed. Discord connector will use mock data.")

logger = logging.getLogger(__name__)


@dataclass
class DiscordMessage:
    """Structured Discord message data."""
    message_id: str
    channel_id: str
    channel_name: str
    server_id: str
    server_name: str
    content: str
    author: str
    author_id: str
    created_at: datetime
    edited_at: Optional[datetime] = None
    reactions: int = 0
    mentions: List[str] = None
    attachments: List[str] = None
    
    def __post_init__(self):
        if self.mentions is None:
            self.mentions = []
        if self.attachments is None:
            self.attachments = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'message_id': self.message_id,
            'channel_id': self.channel_id,
            'channel_name': self.channel_name,
            'server_id': self.server_id,
            'server_name': self.server_name,
            'content': self.content,
            'author': self.author,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat(),
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'reactions': self.reactions,
            'mentions': self.mentions,
            'attachments': self.attachments
        }


class DiscordConnector:
    """Connector for ingesting data from Discord."""
    
    def __init__(self, bot_token: Optional[str] = None):
        """
        Initialize Discord connector.
        
        Args:
            bot_token: Discord bot token
        """
        self.bot_token = bot_token or os.getenv('DISCORD_BOT_TOKEN')
        self.client = None
        self.is_ready = False
        
        if DISCORD_AVAILABLE and self.bot_token:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.messages = True
            intents.guilds = True
            
            self.client = discord.Client(intents=intents)
            self._setup_events()
            logger.info("Discord connector initialized")
        else:
            logger.warning("Discord connector using mock mode (no token or library)")
    
    def _setup_events(self):
        """Setup Discord client events."""
        @self.client.event
        async def on_ready():
            self.is_ready = True
            logger.info(f'Discord bot logged in as {self.client.user}')
        
        @self.client.event
        async def on_message(message):
            # Handle real-time messages if needed
            if message.author == self.client.user:
                return
            logger.debug(f"New message in {message.channel}: {message.content[:50]}")
    
    async def connect(self):
        """Connect to Discord."""
        if self.client and self.bot_token:
            try:
                await self.client.start(self.bot_token)
            except Exception as e:
                logger.error(f"Failed to connect to Discord: {e}")
    
    async def disconnect(self):
        """Disconnect from Discord."""
        if self.client:
            await self.client.close()
    
    async def get_channel_messages(self,
                                   channel_id: int,
                                   limit: int = 100,
                                   before: Optional[datetime] = None,
                                   after: Optional[datetime] = None) -> List[DiscordMessage]:
        """
        Get messages from a Discord channel.
        
        Args:
            channel_id: Discord channel ID
            limit: Maximum number of messages to retrieve
            before: Get messages before this datetime
            after: Get messages after this datetime
            
        Returns:
            List of Discord messages
        """
        if not self.client or not self.is_ready:
            return self._get_mock_messages(channel_id, limit)
        
        try:
            channel = self.client.get_channel(channel_id)
            if not channel:
                logger.error(f"Channel {channel_id} not found")
                return self._get_mock_messages(channel_id, limit)
            
            messages = []
            async for message in channel.history(limit=limit, before=before, after=after):
                discord_message = DiscordMessage(
                    message_id=str(message.id),
                    channel_id=str(message.channel.id),
                    channel_name=message.channel.name,
                    server_id=str(message.guild.id) if message.guild else "DM",
                    server_name=message.guild.name if message.guild else "Direct Message",
                    content=message.content,
                    author=str(message.author),
                    author_id=str(message.author.id),
                    created_at=message.created_at,
                    edited_at=message.edited_at,
                    reactions=sum(reaction.count for reaction in message.reactions),
                    mentions=[str(mention) for mention in message.mentions],
                    attachments=[attachment.url for attachment in message.attachments]
                )
                messages.append(discord_message)
            
            logger.info(f"Retrieved {len(messages)} messages from channel {channel_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error retrieving messages from channel {channel_id}: {e}")
            return self._get_mock_messages(channel_id, limit)
    
    async def get_server_messages(self,
                                  server_id: int,
                                  limit_per_channel: int = 50,
                                  channel_filter: Optional[List[str]] = None) -> List[DiscordMessage]:
        """
        Get messages from all channels in a Discord server.
        
        Args:
            server_id: Discord server (guild) ID
            limit_per_channel: Maximum messages per channel
            channel_filter: List of channel names to include (None = all)
            
        Returns:
            List of Discord messages from all channels
        """
        if not self.client or not self.is_ready:
            return self._get_mock_messages(server_id, limit_per_channel * 5)
        
        try:
            guild = self.client.get_guild(server_id)
            if not guild:
                logger.error(f"Server {server_id} not found")
                return self._get_mock_messages(server_id, limit_per_channel * 5)
            
            all_messages = []
            for channel in guild.text_channels:
                # Apply channel filter if specified
                if channel_filter and channel.name not in channel_filter:
                    continue
                
                try:
                    channel_messages = await self.get_channel_messages(
                        channel.id,
                        limit=limit_per_channel
                    )
                    all_messages.extend(channel_messages)
                except Exception as e:
                    logger.error(f"Error retrieving messages from channel {channel.name}: {e}")
                    continue
            
            logger.info(f"Retrieved {len(all_messages)} total messages from server {server_id}")
            return all_messages
            
        except Exception as e:
            logger.error(f"Error retrieving messages from server {server_id}: {e}")
            return self._get_mock_messages(server_id, limit_per_channel * 5)
    
    async def search_messages(self,
                            channel_id: int,
                            query: str,
                            limit: int = 100) -> List[DiscordMessage]:
        """
        Search for messages containing specific text.
        
        Args:
            channel_id: Discord channel ID
            query: Search query
            limit: Maximum number of messages to search through
            
        Returns:
            List of Discord messages matching the query
        """
        messages = await self.get_channel_messages(channel_id, limit=limit)
        
        # Filter messages containing the query
        matching_messages = [
            msg for msg in messages
            if query.lower() in msg.content.lower()
        ]
        
        logger.info(f"Found {len(matching_messages)} messages matching '{query}'")
        return matching_messages
    
    def _get_mock_messages(self, channel_id: int, limit: int) -> List[DiscordMessage]:
        """Generate mock Discord messages for testing."""
        messages = []
        for i in range(min(limit, 10)):
            message = DiscordMessage(
                message_id=f"mock_{i}",
                channel_id=str(channel_id),
                channel_name="esg-discussion",
                server_id="mock_server",
                server_name="ESG Community",
                content=f"Mock Discord message about sustainability trends. Message {i+1}.",
                author=f"User{i}",
                author_id=f"user_{i}",
                created_at=datetime.now() - timedelta(hours=i),
                reactions=10 - i,
                mentions=[],
                attachments=[]
            )
            messages.append(message)
        return messages


class DiscordDataCollector:
    """High-level Discord data collector with async support."""
    
    def __init__(self, bot_token: Optional[str] = None):
        """Initialize Discord data collector."""
        self.connector = DiscordConnector(bot_token)
        self.collection_tasks = []
    
    async def start(self):
        """Start the Discord connector."""
        if self.connector.client:
            asyncio.create_task(self.connector.connect())
            # Wait for bot to be ready
            while not self.connector.is_ready:
                await asyncio.sleep(0.5)
    
    async def stop(self):
        """Stop the Discord connector."""
        await self.connector.disconnect()
    
    async def collect_from_channels(self,
                                    channel_ids: List[int],
                                    limit_per_channel: int = 100) -> List[DiscordMessage]:
        """
        Collect messages from multiple channels.
        
        Args:
            channel_ids: List of Discord channel IDs
            limit_per_channel: Maximum messages per channel
            
        Returns:
            Combined list of messages from all channels
        """
        all_messages = []
        
        for channel_id in channel_ids:
            messages = await self.connector.get_channel_messages(
                channel_id,
                limit=limit_per_channel
            )
            all_messages.extend(messages)
        
        logger.info(f"Collected {len(all_messages)} messages from {len(channel_ids)} channels")
        return all_messages
    
    async def collect_from_servers(self,
                                   server_ids: List[int],
                                   limit_per_channel: int = 50) -> List[DiscordMessage]:
        """
        Collect messages from multiple servers.
        
        Args:
            server_ids: List of Discord server IDs
            limit_per_channel: Maximum messages per channel
            
        Returns:
            Combined list of messages from all servers
        """
        all_messages = []
        
        for server_id in server_ids:
            messages = await self.connector.get_server_messages(
                server_id,
                limit_per_channel=limit_per_channel
            )
            all_messages.extend(messages)
        
        logger.info(f"Collected {len(all_messages)} messages from {len(server_ids)} servers")
        return all_messages


# Convenience functions
def get_discord_connector() -> DiscordConnector:
    """Get Discord connector instance."""
    return DiscordConnector()


async def collect_discord_data(channel_ids: List[int], limit: int = 100) -> List[DiscordMessage]:
    """
    Convenience function to collect Discord data.
    
    Args:
        channel_ids: List of channel IDs to collect from
        limit: Messages per channel
        
    Returns:
        List of Discord messages
    """
    collector = DiscordDataCollector()
    await collector.start()
    messages = await collector.collect_from_channels(channel_ids, limit)
    await collector.stop()
    return messages

