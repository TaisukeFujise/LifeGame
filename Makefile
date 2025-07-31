# --- Variables ---
PYTHON = python3
HOST = localhost
PORT = 2000

# Player 1 is the opponent (background), connected first.
P1 ?= random
P1_SCRIPT = sample/$(P1)_player.py

# Player 2 is you (foreground), connected second.
P2 ?= manual
P2_SCRIPT = sample/$(P2)_player.py

SERVER_SCRIPT = sample/server.py

# --- Targets ---
.PHONY: all run server clients stop help

# Default target executed when running `make`
all: help

# Start the server and both players
run:
	@echo "Stopping any existing game processes..."
	@pkill -f "python3 sample/" || echo "No existing processes to stop."
	@sleep 1
	@echo "Starting server in background..."
	@$(PYTHON) $(SERVER_SCRIPT) $(HOST) $(PORT) &
	@echo "Waiting for server to initialize..."
	@sleep 2
	@echo "Starting opponent Player 1 ($(P1)) in background..."
	@$(PYTHON) $(P1_SCRIPT) $(HOST) $(PORT) &
	@sleep 1
	@echo "Starting your Player 2 (manual_player) in foreground..."
	@$(PYTHON) $(P2_SCRIPT) $(HOST) $(PORT)

# Start only the server
server:
	@echo "Starting server in background..."
	@$(PYTHON) $(SERVER_SCRIPT) $(HOST) $(PORT) &

# Start both players
clients:
	@echo "Starting opponent Player 1 ($(P1)) in background..."
	@$(PYTHON) $(P1_SCRIPT) $(HOST) $(PORT) &
	@echo "Starting your Player 2 (manual_player) in foreground..."
	@$(PYTHON) $(P2_SCRIPT) $(HOST) $(PORT)

# Stop all running game processes
stop:
	@echo "Stopping all game processes..."
	@pkill -f "python3 sample/" || echo "No game processes were running."
	@echo "Done."

# Show the help message
help:
	@echo "----------------------------------------"
	@echo "Life Game (T. Fujise)"
	@echo "----------------------------------------"
	@echo "Usage: make [target] [P1=player_name]"
	@echo "----------------------------------------"
	@echo "Targets:"
	@echo "  run      - Start the server and both clients."
	@echo "  server   - Start only the server in the background."
	@echo "  clients  - Start both client players."
	@echo "  stop     - Stop all running game processes."
	@echo "  help     - Show this help message."
	@echo "----------------------------------------"
	@echo "Argument:"
	@echo "  P1       - The name of the opponent player script (default: random_player)."
	@echo "----------------------------------------"
	@echo "Example:"
	@echo "  make run P1=another_ai_player"
	@echo "----------------------------------------"
