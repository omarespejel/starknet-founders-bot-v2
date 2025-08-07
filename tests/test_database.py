"""Tests for database operations."""
import pytest
from unittest.mock import Mock, patch
from src.bot.database import Database


class TestDatabase:
    """Test cases for Database class."""
    
    @patch('src.bot.database.create_client')
    def test_database_init(self, mock_create_client):
        """Test database initialization."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        db = Database()
        
        assert db.client == mock_client
        mock_create_client.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_message_success(self):
        """Test successful message saving."""
        # This will be implemented when we have actual Supabase setup
        pass
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_success(self):
        """Test successful conversation history retrieval."""
        # This will be implemented when we have actual Supabase setup
        pass