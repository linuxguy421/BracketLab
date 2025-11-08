# tests/test_logic.py

import pytest
import uuid
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from core.models import (
    TournamentStateModel, MatchModel, MatchStatus, TournamentPhase, PlayerModel
)

from core.config_manager import ConfigManager, DEFAULT_CONFIG_PATH
from core.bracket_logic import BracketLogic
from core.models import TournamentStateModel, PlayerModel, MatchStatus, TournamentPhase

# --- Fixture for ConfigManager Testing ---

@pytest.fixture(scope="function")
def temp_config_manager(tmp_path):
    """Provides a ConfigManager isolated to a temporary file path."""
    temp_path = tmp_path / 'test_config.json'
    mgr = ConfigManager(config_path=temp_path)
    yield mgr, temp_path

def test_config_manager_creates_default_file(temp_config_manager):
    """Tests that the manager creates a default config file if none exists."""
    mgr, path = temp_config_manager
    assert path.exists() 
    assert mgr.config.logging_level == "DEBUG"

def test_config_manager_loads_valid_file(temp_config_manager):
    """Tests that a valid custom config file is loaded correctly."""
    mgr, path = temp_config_manager
    custom_config_data = {
        "logging_level": "WARNING",
        "entry_fee_per_person": 10.0,
        "min_players": 8,
        "max_players": 64,
        "side_pots_enabled": False,
        "side_pots": []
    }
    path.write_text(json.dumps(custom_config_data))
    
    mgr_reload = ConfigManager(config_path=path) 
    
    assert mgr_reload.config.logging_level == "WARNING"
    assert mgr_reload.config.min_players == 8

# --- Fixture for Bracket Logic Testing ---

@pytest.fixture
def initial_state_and_players():
    """Fixture to create a clean initial state and 6 players (forcing 2 matches, 2 byes)."""
    players = [
        PlayerModel(player_id=f"P{i}", name=f"Player {i}") for i in range(1, 7) # P1 to P6
    ]
    player_dict = {p.player_id: p for p in players}
    
    initial_state = TournamentStateModel(
        tournament_id=str(uuid.uuid4()),
        name="Test 6 Player Tourney",
        players=player_dict,
        phase=TournamentPhase.REGISTRATION
    )
    return initial_state, players

def test_start_tournament_generates_correct_bracket(initial_state_and_players):
    """Tests that the tournament starts, sets the correct phase, and generates 
       the required number of matches (6 players -> 8 bracket size -> 2 matches, 4 byes)."""
    state, players = initial_state_and_players
    logic = BracketLogic()
    
    updated_state = logic.start_tournament(state, players)
    
    assert updated_state.phase == TournamentPhase.IN_PROGRESS
    assert len(updated_state.bracket) == 2 # 6 players in an 8-slot bracket requires only 2 initial matches
    assert updated_state.total_prize_pool == 30.0 # 6 players * $5 fee
    
    active_matches = [m for m in updated_state.bracket.values() if m.status == MatchStatus.ACTIVE]
    assert len(active_matches) == 1 # Only one match should be active initially

def test_record_match_result_updates_status(initial_state_and_players):
    """Tests that recording a result updates status and sets winner/loser."""
    state, players = initial_state_and_players
    logic = BracketLogic()
    state = logic.start_tournament(state, players)
    
    active_match_id = next(m_id for m_id, m in state.bracket.items() if m.status == MatchStatus.ACTIVE)
    active_match = state.bracket[active_match_id]
    
    # Record a winner
    winner_id = active_match.teams[0]
    
    updated_state, next_match_id = logic.record_match_result(state, active_match_id, winner_id)
    
    # 1. Assert old match status is COMPLETE
    completed_match = updated_state.bracket[active_match_id]
    assert completed_match.status == MatchStatus.COMPLETE
    assert completed_match.winner_id == winner_id
    assert completed_match.loser_id in active_match.teams
    
    # 2. Assert next match is activated (the only other round 1 match)
    assert next_match_id is not None
    assert updated_state.bracket[next_match_id].status == MatchStatus.ACTIVE
