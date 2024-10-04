# Variables
venv_path := justfile_directory() + "/backend/venv"
python := venv_path + "/bin/python"
flask := venv_path + "/bin/flask"
honcho := venv_path + "/bin/honcho"

# Default command to list available commands
default:
    @just --list

# Command to list all available commands
list:
    @echo "Available commands:"
    @echo "  just run-api   - Run the Flask backend with hot reloading"
    @echo "  just run-ui    - Run the React frontend with hot reloading"
    @echo "  just run       - Run both backend and frontend simultaneously"

# Run Flask backend (API)
run-api:
    cd backend
    FLASK_ENV=development FLASK_APP=backend/app flask run --reload

# Run React frontend (UI) with hot reloading
run-ui:
    cd frontend && pnpm run dev

# Run both backend and frontend using honcho and the Procfile
run:
    honcho start