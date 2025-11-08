# core/models.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum

# --- ENUMERATIONS ---

class MatchStatus(str, Enum):
    """Status of a single match in the bracket."""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"

class TournamentPhase(str, Enum):
    """Current overall phase of the tournament."""
    REGISTRATION = "REGISTRATION"
    IN_PROGRESS = "IN_PROGRESS"
    FINALIZED = "FINALIZED"

# --- CORE MODELS ---

class PlayerModel(BaseModel):
    """The data model for a single participant."""
    player_id: str = Field(..., description="Unique ID for the player (UUID or slug).")
    name: str = Field(..., description="Player's displayed name.")
    email: Optional[str] = Field(None, description="Contact email.")
    current_rank: Optional[int] = Field(None, ge=1, description="Current rank in the league/system.")

class SidePotModel(BaseModel):
    """Configuration for an optional prize pot (e.g., 'Hat Trick Fund')."""
    name: str = Field(..., description="User-friendly name of the pot.")
    per_entry_fee: float = Field(0.0, ge=0, description="Amount contributed to this pot per entry.")
    trigger_condition: str = Field(..., description="Logic string for payout (e.g., 'First_Hat_Trick').")

class TournamentConfig(BaseModel):
    """The main configuration for the BracketLab instance."""
    logging_level: str = Field("DEBUG", description="Logging level for Loguru (DEBUG, INFO, etc).")
    entry_fee_per_person: float = Field(5.0, ge=0, description="Default tournament entry fee.")
    min_players: int = Field(4, gt=0, description="Minimum number of players to start.")
    max_players: int = Field(32, gt=0, description="Maximum number of players.")
    
    side_pots_enabled: bool = True
    side_pots: List[SidePotModel] = Field(
        [SidePotModel(name="Hat Trick Fund", per_entry_fee=1.0, trigger_condition="First_Hat_Trick")],
        description="List of all custom side pots."
    )

class MatchModel(BaseModel):
    """Represents a single match within the tournament bracket."""
    match_id: str = Field(..., description="Unique ID for the match.")
    round_name: str = Field(..., description="e.g., 'Round 1', 'Semi-Finals'.")
    teams: List[str] = Field(..., min_length=2, max_length=2, description="List of Player IDs participating.")
    status: MatchStatus = MatchStatus.PENDING
    winner_id: Optional[str] = None
    loser_id: Optional[str] = None
    score: Optional[Dict[str, int]] = None

class TournamentStateModel(BaseModel):
    """The CENTRAL, decoupled state of the entire active tournament."""
    tournament_id: str = Field(..., description="Unique ID for this tournament instance.")
    name: str = Field(..., description="Name of the tournament.")
    phase: TournamentPhase = TournamentPhase.REGISTRATION
    
    players: Dict[str, PlayerModel] = Field(default_factory=dict, description="Map of player_id to PlayerModel.")
    bracket: Dict[str, MatchModel] = Field(default_factory=dict, description="Map of match_id to MatchModel.")
    
    total_prize_pool: float = 0.0
    final_rankings: Dict[int, str] = Field(default_factory=dict, description="Final rank -> Player ID.")
