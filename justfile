# Default command to list available commands
default:
    @just --list

# Command to list all available commands
list:
    @echo "Available commands:"
    @echo "  just run-api   - Run the Flask backend with hot reloading"
    @echo "  just run-ui    - Run the React frontend with hot reloading"
    @echo "  just run       - Run both backend and frontend simultaneously"

# Run Flask backend (API) with direnv handling the virtual environment
run-api:
    cd backend
    FLASK_ENV=development FLASK_APP=app flask run --reload

# Run React frontend (UI) with hot reloading
run-ui:
    cd frontend && pnpm run dev

# Run both backend and frontend simultaneously
run:
    just run-api &
    just run-ui &
    wait