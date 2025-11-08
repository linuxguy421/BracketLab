# gui/main_window.py

import sys
import uuid # <--- FIX 1: Import uuid here!
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QTabWidget, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt

# Import your core logic and models
from core.bracket_logic import bracket_logic
from core.player_manager import player_manager
from core.models import TournamentStateModel, PlayerModel, TournamentPhase, MatchStatus
from core.logger import logger
from typing import List, Optional

class TournamentApp(QMainWindow):
    """The main application window for BracketLab."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏆 BracketLab - Local Tournament Manager")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central state management
        self.current_state: TournamentStateModel = self._load_initial_state()
        
        # UI Component references
        self.tabs = QTabWidget()
        self.player_table = QTableWidget()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.winner_input = QLineEdit() # Needed for the new dashboard controls
        self.match_control_widget = QWidget() # Container for match controls
        self.status_label = QLabel() # Central status label
        self.match_info_label = QLabel() # Match specific status
        
        self.setCentralWidget(self.tabs)

        # Build UI Tabs
        self.tabs.addTab(self._create_dashboard_tab(), "Dashboard")
        self.tabs.addTab(self._create_registration_tab(), "Player Registration")
        self.tabs.addTab(self._create_config_tab(), "Settings")
        
        # Initial display update
        self._update_player_table() 
        self._update_dashboard_ui() # Initialize dashboard status
        
        logger.info("PyQt6 Main Window initialized.")

    def _load_initial_state(self) -> TournamentStateModel:
        """Creates or loads the initial Tournament State model."""
        return TournamentStateModel(
            tournament_id=str(uuid.uuid4()),
            name="New Darts Tournament"
        )
        
    # --- TAB CREATION METHODS ---
        
    def _create_dashboard_tab(self):
        """Creates the tab for live bracket and match score entry."""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        
        self.status_label.setText(f"Tournament: {self.current_state.name} | Phase: {self.current_state.phase.value}")
        layout.addWidget(QLabel("<h2>Live Tournament Dashboard</h2>"))
        layout.addWidget(self.status_label)
        
        layout.addWidget(QLabel("[Placeholder for Bracket Visualization]"))
        
        start_button = QPushButton("Start Tournament")
        start_button.clicked.connect(self._start_tournament_handler)
        layout.addWidget(start_button)
        
        # --- Match Score Entry UI ---
        
        self.match_info_label.setText("Waiting for tournament to start...")
        layout.addWidget(self.match_info_label)
        
        self.winner_input.setPlaceholderText("Enter Winner ID (e.g., P1, P2)")
        
        record_button = QPushButton("Record Winner & Advance Match")
        record_button.clicked.connect(self._record_result_handler)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.winner_input)
        input_layout.addWidget(record_button)
        
        self.match_control_widget.setLayout(input_layout)
        self.match_control_widget.setVisible(False)
        
        layout.addWidget(self.match_control_widget)

        return dashboard

    def _create_registration_tab(self):
        """Creates the tab for player entry and management."""
        registration = QWidget()
        layout = QVBoxLayout(registration)
        
        # Player Entry Form
        form_layout = QHBoxLayout()
        self.name_input.setPlaceholderText("Player Name (Required)")
        self.email_input.setPlaceholderText("Email (Optional)")

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.email_input)
        
        register_button = QPushButton("Register Player")
        register_button.clicked.connect(self._register_player_handler)
        
        layout.addWidget(QLabel("<h2>Register New Player</h2>"))
        layout.addLayout(form_layout)
        layout.addWidget(register_button)
        
        # Player Table Setup
        self.player_table.setColumnCount(3)
        self.player_table.setHorizontalHeaderLabels(["Name", "Email", "ID"])
        self.player_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(QLabel("<h3>Registered Players</h3>"))
        layout.addWidget(self.player_table)

        return registration

    def _create_config_tab(self):
        """Creates the tab for application settings and prize pool config."""
        config = QWidget()
        layout = QVBoxLayout(config)
        layout.addWidget(QLabel("<h2>Application Settings & Prize Config</h2>"))
        
        # FIX 2: Access config directly using the property method
        layout.addWidget(QLabel(f"Current Entry Fee: ${self.config.entry_fee_per_person:.2f} (from config)")) 
        layout.addWidget(QLabel("[Configuration forms go here]"))
        return config

    # --- CORE LOGIC HANDLERS ---
    
    @property
    def config(self):
        """Shortcut to access the configuration manager's model (FIXED ACCESS)."""
        from core.config_manager import config_manager
        return config_manager.config

    def _update_player_table(self):
        """Fetches players from the state and populates the QTableWidget."""
        
        players: List[PlayerModel] = list(self.current_state.players.values())
        
        self.player_table.setRowCount(len(players))
        
        for row, player in enumerate(players):
            name_item = QTableWidgetItem(player.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.player_table.setItem(row, 0, name_item)
            
            email_item = QTableWidgetItem(player.email or "N/A")
            email_item.setFlags(email_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.player_table.setItem(row, 1, email_item)
            
            id_item = QTableWidgetItem(player.player_id[:8])
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.player_table.setItem(row, 2, id_item)
            
        self.player_table.resizeRowsToContents()
        logger.debug(f"Player table refreshed with {len(players)} entries.")

    def _update_dashboard_ui(self):
        """Updates all dashboard labels based on the current state."""
        self.status_label.setText(f"Tournament: {self.current_state.name} | Phase: {self.current_state.phase.value}")
        
        if self.current_state.phase == TournamentPhase.IN_PROGRESS:
            # Find the currently active match
            active_match = next((m for m in self.current_state.bracket.values() if m.status == MatchStatus.ACTIVE), None)
            
            if active_match:
                team_names = [self.current_state.players.get(p_id).name for p_id in active_match.teams]
                
                self.match_info_label.setText(
                    f"**Active Match:** {active_match.round_name} | {team_names[0]} vs {team_names[1]} (ID: {active_match.match_id[:8]})"
                )
                self.match_control_widget.setVisible(True)
            else:
                self.match_info_label.setText("No active matches. Tournament structure complete.")
                self.match_control_widget.setVisible(False)
                
        elif self.current_state.phase == TournamentPhase.FINALIZED:
             self.match_info_label.setText("TOURNAMENT COMPLETE! Check Rankings.")
             self.match_control_widget.setVisible(False)


    def _register_player_handler(self):
        """Handles button click to register a player using the core manager."""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        
        if not name:
            logger.warning("Attempted to register player with no name.")
            return

        # 1. Call the Core Logic (PlayerManager)
        new_player = player_manager.register_new_player(name, email if email else None)
        
        # 2. Update the Central State (Add new player to the model)
        self.current_state.players[new_player.player_id] = new_player
        
        # 3. Update the GUI
        self.name_input.clear()
        self.email_input.clear()
        self._update_player_table()
        
        logger.info(f"Registered {name}. Total players: {len(self.current_state.players)}")

    def _start_tournament_handler(self):
        """Handles the button click to start the tournament bracket."""
        
        players_list = list(self.current_state.players.values())
        
        # 1. Call the Core Logic (BracketLogic)
        new_state = bracket_logic.start_tournament(self.current_state, players_list)
        
        # 2. Update the Central State
        self.current_state = new_state
        
        # 3. Update the GUI Status, switch to dashboard, and update match info
        self.tabs.setCurrentIndex(0) 
        self._update_dashboard_ui()
        
        logger.info(f"Tournament Started! Phase: {self.current_state.phase.value}. Prize Pool: {self.current_state.total_prize_pool}")

    def _record_result_handler(self):
        """Records the winner of the active match and advances the bracket."""
        
        winner_id = self.winner_input.text().strip()
        
        # Find the active match ID
        active_match = next((m for m in self.current_state.bracket.values() if m.status == MatchStatus.ACTIVE), None)
        
        if not active_match:
            logger.warning("No active match found to record a result.")
            return

        # 1. Call the Core Logic (BracketLogic)
        new_state, next_match_id = bracket_logic.record_match_result(
            self.current_state, active_match.match_id, winner_id
        )
        
        # 2. Update the Central State
        self.current_state = new_state
        
        # 3. Update the GUI
        self.winner_input.clear()
        self._update_dashboard_ui()
        
        logger.info(f"Match {active_match.match_id[:8]} resolved. Next match: {next_match_id}")
