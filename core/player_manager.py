# core/player_manager.py

import uuid
from typing import Dict, Optional, List
from core.models import PlayerModel
from core.logger import logger

class PlayerManager:
    """Handles the creation, retrieval, and management of PlayerModel instances."""

    def __init__(self):
        # Stores all players. In Phase 4, this would load from persistence.
        self._players: Dict[str, PlayerModel] = {}
        logger.info("PlayerManager initialized.")

    def register_new_player(self, name: str, email: str = None) -> PlayerModel:
        """Creates a new PlayerModel and adds it to the system."""
        
        # 1. Generate a unique ID
        player_id = str(uuid.uuid4())
        
        # 2. Create the Pydantic model (Pydantic validates the data here)
        try:
            new_player = PlayerModel(
                player_id=player_id,
                name=name,
                email=email
            )
        except Exception as e:
            logger.error(f"Failed to create PlayerModel for {name}: {e}")
            raise
        
        # 3. Store the player
        self._players[player_id] = new_player
        
        logger.info(f"Registered new player: {name} with ID: {player_id[:8]}...")
        return new_player

    def get_player(self, player_id: str) -> Optional[PlayerModel]:
        """Retrieves a player by ID, returns None if not found."""
        return self._players.get(player_id)
    
    def get_all_players(self) -> List[PlayerModel]:
        """Returns a list of all registered players."""
        return list(self._players.values())
    
    # Future functions: update_player, delete_player, etc.

# Initialization for use across the application
player_manager = PlayerManager()
