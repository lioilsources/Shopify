#!/usr/bin/env bash
# Deploy SlopMarket (brain + web + tunnel) to JODA. Idempotent: the tunnel and
# its DNS record are created on the first run, on JODA, and never leave it.
# Public step: run only on Olin's explicit "nasaď".
#   infra/joda/deploy.sh [ssh-host]     (default: joda; SLOP_HOST overrides the hostname)
set -euo pipefail
host=${1:-joda}
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
dest=deploy/Shopify
public=${SLOP_HOST:-slop.ol1n.com}
x=(--exclude node_modules --exclude .svelte-kit --exclude build --exclude .venv --exclude __pycache__ --exclude .env --exclude tests)

echo "==> sync to $host:$dest"
ssh "$host" "mkdir -p $dest/src/services $dest/src/apps $dest/media $dest/cloudflared"
rsync -a --delete "${x[@]}" "$repo/services/brain" "$host:$dest/src/services/"
rsync -a --delete "${x[@]}" "$repo/apps/web" "$host:$dest/src/apps/"
rsync -a "$repo/infra/joda/docker-compose.app.yml" "$host:$dest/"
rsync -a "$repo/infra/joda/cloudflared/config.yml.example" "$host:$dest/cloudflared/"
[ -d "$repo/run/media" ] && rsync -a "$repo/run/media/" "$host:$dest/media/"

ssh "$host" PUBLIC="$public" bash -s -- "$dest" <<'REMOTE'
set -euo pipefail
cd "$1"
touch .env && chmod 600 .env
grep -q '^ADMIN_TOKEN=' .env || echo "ADMIN_TOKEN=$(openssl rand -hex 24)" >> .env
if [ ! -f cloudflared/config.yml ]; then
  # --config /dev/null: never fall back to ~/.cloudflared/config.yml (another tunnel).
  cf() { cloudflared tunnel --config /dev/null --origincert ~/.cloudflared/cert.pem "$@"; }
  tunnel_id() { cf list -o json 2>/dev/null | python3 -c 'import sys,json;print(next((t["id"] for t in json.load(sys.stdin) if t["name"]=="slopmarket"),""))'; }
  ID=$(tunnel_id)
  [ -n "$ID" ] || { cf create slopmarket >/dev/null 2>&1; ID=$(tunnel_id); }
  [ -n "$ID" ] || { echo "tunnel slopmarket not created" >&2; exit 1; }
  install -m 644 ~/.cloudflared/"$ID".json cloudflared/"$ID".json
  sed -e "s/<TUNNEL-ID>/$ID/g" -e "s/<PUBLIC>/$PUBLIC/g" cloudflared/config.yml.example > cloudflared/config.yml
  cf route dns "$ID" "$PUBLIC" 2>&1 | tail -1 || true
  echo "tunnel slopmarket = $ID"
fi
docker compose -p shopify-app -f docker-compose.app.yml up -d --build
mkdir -p ~/deploy
printf '{"at":"%s","project":"Shopify","service":"slopmarket","host":"%s"}\n' "$(date -u +%FT%TZ)" "$PUBLIC" >> ~/deploy/events.jsonl
docker ps --filter name=shopify-app --format '{{.Names}} {{.Status}}'
REMOTE
echo "==> https://$public/"
