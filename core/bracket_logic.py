# core/bracket_logic.py

import uuid
import random
# Ensure this line correctly imports ALL necessary types, including Optional
from typing import List, Dict, Tuple, Optional 

from core.models import (
    TournamentStateModel, MatchModel, MatchStatus, TournamentPhase, PlayerModel
)
from core.config_manager import config_manager
from core.logger import logger
from math import log2, ceil

class BracketLogic:
    """Encapsulates all core business logic for bracket management."""

    def __init__(self):
        logger.info("BracketLogic initialized.")

    def _determine_bracket_size(self, num_players: int) -> int:
        """Finds the smallest power of 2 greater than or equal to num_players."""
        return 2 ** ceil(log2(num_players))

    def start_tournament(self, state: TournamentStateModel, players: List[PlayerModel]) -> TournamentStateModel:
        """
        Initializes the bracket structure and transitions the tournament phase.
        This function modifies the state model based on the configuration and player list.
        """
        num_players = len(players)
        
        # 1. Validation Checks
        min_p = config_manager.config.min_players
        max_p = config_manager.config.max_players
        if not (min_p <= num_players <= max_p):
            logger.error(f"Cannot start: Player count ({num_players}) is outside required range ({min_p}-{max_p}).")
            state.phase = TournamentPhase.REGISTRATION
            return state
        
        # 2. Update State Financials
        state.phase = TournamentPhase.IN_PROGRESS
        state.total_prize_pool = num_players * config_manager.config.entry_fee_per_person
        
        # 3. Seeding (Simple Random Seeding)
        player_ids = [p.player_id for p in players]
        random.shuffle(player_ids)
        
        # 4. Bracket Generation (Single Elimination)
        bracket_size = self._determine_bracket_size(num_players)
        matches: Dict[str, MatchModel] = {}
        
        num_byes = bracket_size - num_players
        
        # Determine players who get byes (if any)
        bye_players = player_ids[:num_byes]
        match_players = player_ids[num_byes:] # Remaining players compete in Round 1
        
        # Create first round matches
        match_counter = 0
        while len(match_players) >= 2:
            match_id = str(uuid.uuid4())
            team_A = match_players.pop(0)
            team_B = match_players.pop(0)
            
            matches[match_id] = MatchModel(
                match_id=match_id,
                round_name="Round 1",
                teams=[team_A, team_B],
                status=MatchStatus.ACTIVE if match_counter == 0 else MatchStatus.PENDING
            )
            match_counter += 1
            
        logger.info(f"Tournament started with {num_players} players. {num_byes} byes generated.")
        # NOTE: Handling byes (advancing them to round 2) would be a complex feature added here.
        
        state.bracket = matches
        return state.model_copy(deep=True) # Return a modified copy of the state

    def record_match_result(self, state: TournamentStateModel, match_id: str, winner_id: str) -> Tuple[TournamentStateModel, Optional[str]]:
        """
        Records the winner of a match and manages state transition.
        Returns the updated state and the ID of the next match (or None).
        """
        if match_id not in state.bracket:
            logger.warning(f"Attempted to record result for non-existent match: {match_id}")
            return state, None
        
        match = state.bracket[match_id]
        
        # 1. Validation and Update current match
        if match.status != MatchStatus.ACTIVE or winner_id not in match.teams:
            logger.error(f"Invalid result for match {match_id}. Winner: {winner_id}, Status: {match.status.value}")
            return state, None

        match.status = MatchStatus.COMPLETE
        match.winner_id = winner_id
        match.loser_id = next(p for p in match.teams if p != winner_id)
        
        logger.info(f"Match {match_id} completed. Winner: {winner_id}")

        # 2. Advance Winner (Placeholder for complex bracket advancement)
        # This is where the core logic to find the next match and insert the winner would go.
        
        # 3. Activate the next available match
        next_match_id = next((m_id for m_id, m in state.bracket.items() 
                             if m.status == MatchStatus.PENDING), None)
        
        if next_match_id:
            state.bracket[next_match_id].status = MatchStatus.ACTIVE
            logger.info(f"Next match activated: {next_match_id}")
            return state.model_copy(deep=True), next_match_id

        # If no more matches, the tournament is over
        if not state.bracket:
            state.phase = TournamentPhase.FINALIZED
            logger.info("Tournament Finalized: No matches were generated.")
        elif all(m.status == MatchStatus.COMPLETE for m in state.bracket.values()):
            state.phase = TournamentPhase.FINALIZED
            logger.info("Tournament Finalized: All bracket matches completed.")
        
        return state.model_copy(deep=True), None

# Initialization for use across the application
bracket_logic = BracketLogic()
