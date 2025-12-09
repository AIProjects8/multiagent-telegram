#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"
PROD_COMPOSE_FILE="docker-compose.prod.yml"

echo "=== Multiagent Telegram Bot Deployment Script ==="
echo ""

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file based on .env.example"
    exit 1
fi

echo "Step 1: Checking Docker and Docker Compose..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed"
    exit 1
fi

COMPOSE_CMD="docker compose"
if ! docker compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
fi

echo "✓ Docker and Docker Compose found"
echo ""

echo "Step 2: Stopping existing containers..."
$COMPOSE_CMD -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" down
echo ""

echo "Step 3: Pulling latest code (if using git)..."
if [ -d ".git" ]; then
    git pull || echo "Warning: Git pull failed, continuing with local code"
    echo ""
fi

echo "Step 4: Updating localizations (generating .mo files)..."
if command -v python3 &> /dev/null; then
    if [ -f "manage_translations.py" ]; then
        python3 manage_translations.py update-all
        echo "✓ Localizations updated"
    else
        echo "Warning: manage_translations.py not found, skipping localization update"
    fi
else
    echo "Warning: python3 not found, skipping localization update"
fi
echo ""

echo "Step 5: Building Docker images..."
$COMPOSE_CMD -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" build --no-cache
echo ""

echo "Step 6: Starting services..."
$COMPOSE_CMD -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" up -d
echo ""

echo "Step 7: Waiting for services to be healthy..."
echo "Waiting for database to be ready..."
for i in {1..30}; do
    if $COMPOSE_CMD -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" exec -T postgres pg_isready > /dev/null 2>&1; then
        echo "✓ Database is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Warning: Database not ready after 30 seconds, continuing anyway"
    else
        sleep 1
    fi
done
sleep 2

echo "Step 8: Running database migrations (Alembic)..."
if $COMPOSE_CMD -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" ps | grep -q "bot.*Up"; then
    echo "Running Alembic migrations in bot container..."
    if $COMPOSE_CMD -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" exec -T bot sh -c "cd /app && alembic upgrade head"; then
        echo "✓ Migrations completed successfully"
    else
        echo "✗ Migration failed, but continuing deployment"
        echo "To debug, run: $COMPOSE_CMD -f $COMPOSE_FILE -f $PROD_COMPOSE_FILE exec bot alembic upgrade head"
    fi
else
    echo "Warning: Bot container not running yet, migrations will run on bot startup"
fi
echo ""

echo "Step 8: Checking service status..."
$COMPOSE_CMD -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" ps
echo ""

echo "Step 9: Viewing logs (last 50 lines)..."
echo "--- Bot logs ---"
$COMPOSE_CMD -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" logs --tail=50 bot
echo ""
echo "--- Scheduler logs ---"
$COMPOSE_CMD -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" logs --tail=50 scheduler
echo ""

echo "=== Deployment completed! ==="
echo ""
echo "Useful commands:"
echo "  View logs:        $COMPOSE_CMD -f $COMPOSE_FILE -f $PROD_COMPOSE_FILE logs -f [service]"
echo "  Stop services:    $COMPOSE_CMD -f $COMPOSE_FILE -f $PROD_COMPOSE_FILE down"
echo "  Restart service:  $COMPOSE_CMD -f $COMPOSE_FILE -f $PROD_COMPOSE_FILE restart [service]"
echo "  View status:      $COMPOSE_CMD -f $COMPOSE_FILE -f $PROD_COMPOSE_FILE ps"

