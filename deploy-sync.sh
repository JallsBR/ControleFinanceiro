#!/bin/bash
set -euo pipefail
cd /opt/o5o/apps/controlefinanceiro
LOCK=/var/lock/controlefinanceiro-deploy.lock
exec 9>"$LOCK"
flock -n 9 || { echo "deploy já em andamento"; exit 0; }

git fetch origin deploy >/dev/null 2>&1
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/deploy)
FORCE=${1:-}
if [ "$LOCAL" = "$REMOTE" ] && [ "$FORCE" != "--force" ]; then
  exit 0
fi
echo "$(date -Is) deploy $LOCAL -> $REMOTE" >> /var/log/controlefinanceiro-deploy.log
git checkout deploy >/dev/null 2>&1 || true
git reset --hard origin/deploy
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build >> /var/log/controlefinanceiro-deploy.log 2>&1
echo "$(date -Is) ok $(git rev-parse --short HEAD)" >> /var/log/controlefinanceiro-deploy.log
