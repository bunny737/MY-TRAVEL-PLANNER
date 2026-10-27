#!/usr/bin/env bash
# Build and release the site on Google Cloud Run + Cloud SQL (Module 07). Run from the repository root.
#
#   export PROJECT_ID=mytravelplanner-prod REGION=asia-south1 SQL_CONNECTION=pglive-prod:asia-south1:pglive-pg-prod
#   deploy/cloudrun/deploy.sh release            # build image -> migrate (job) -> deploy service
#
# The database is a separate database on PGLive's Cloud SQL instance (docs/deployment.md "Sharing PGLive's instance").
# Everything this script creates lives in PROJECT_ID, never in a pglive-* project, and it never changes the instance.
#   deploy/cloudrun/deploy.sh manage reset_admin_mfa owner
#   deploy/cloudrun/deploy.sh schedule           # daily clearsessions via Cloud Scheduler (once)
#
# Needs: gcloud (logged in), env.prod.yaml filled from env.prod.yaml.example, and these Secret Manager secrets:
#   travel-secret-key, travel-db-password, travel-email-password  (+ travel-admin-password for createsuperuser).
# Nothing in this script prints a secret. Steps and first-time setup: docs/deployment.md.
set -euo pipefail

: "${PROJECT_ID:?set PROJECT_ID}"
: "${REGION:?set REGION (Cloud Run region, e.g. asia-south1)}"
: "${SQL_CONNECTION:?set SQL_CONNECTION (project:region:instance of the existing Cloud SQL instance)}"
if [[ "$PROJECT_ID" == pglive-* ]]; then
  echo "PROJECT_ID=$PROJECT_ID is a PGLive project. Deploy into the travel project; only the database is shared." >&2; exit 1
fi
SERVICE="${SERVICE:-travel-web}"
REPO="${REPO:-travel}"                       # Artifact Registry Docker repository
ENV_FILE="${ENV_FILE:-deploy/cloudrun/env.prod.yaml}"
RUNTIME_SA="${RUNTIME_SA:-}"                 # runtime service account email (blank = project default)
TAG="${TAG:-$(date +%Y%m%d-%H%M%S)}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:${TAG}"
SECRETS="SECRET_KEY=travel-secret-key:latest,DB_PASSWORD=travel-db-password:latest,EMAIL_HOST_PASSWORD=travel-email-password:latest"

GCLOUD=(gcloud --project "$PROJECT_ID" --quiet)
# The edge lock (EdgeSecretMiddleware) turns on once the travel-edge-secret secret exists, i.e. after the nginx edge works.
if "${GCLOUD[@]}" secrets describe travel-edge-secret >/dev/null 2>&1; then
  SECRETS="$SECRETS,EDGE_SHARED_SECRET=travel-edge-secret:latest"
fi
SA_FLAG=()
[[ -n "$RUNTIME_SA" ]] && SA_FLAG=(--service-account "$RUNTIME_SA")

[[ -f "$ENV_FILE" ]] || { echo "Missing $ENV_FILE (copy env.prod.yaml.example and fill it)." >&2; exit 1; }
if grep -v '^[[:space:]]*#' "$ENV_FILE" | grep -q '<'; then
  echo "$ENV_FILE still has <placeholders>:" >&2; grep -v '^[[:space:]]*#' "$ENV_FILE" | grep '<' >&2; exit 1
fi

build() {
  echo "==> Building $IMAGE"
  "${GCLOUD[@]}" builds submit backend --config deploy/cloudrun/cloudbuild.yaml --substitutions "_IMAGE=$IMAGE"
}

# One job definition per purpose, always on the image being released.
deploy_job() {  # name, then the container args
  local name="$1"; shift
  local args; args=$(IFS=,; echo "$*")
  "${GCLOUD[@]}" run jobs deploy "$name" --region "$REGION" --image "$IMAGE" \
    --set-cloudsql-instances "$SQL_CONNECTION" --env-vars-file "$ENV_FILE" --set-secrets "$SECRETS" \
    --command python --args "$args" --max-retries 0 --task-timeout 600s "${SA_FLAG[@]}"
}

migrate() {
  echo "==> Migrating the database"
  deploy_job "${SERVICE}-migrate" manage.py migrate --noinput
  "${GCLOUD[@]}" run jobs execute "${SERVICE}-migrate" --region "$REGION" --wait
  deploy_job "${SERVICE}-cachetable" manage.py createcachetable
  "${GCLOUD[@]}" run jobs execute "${SERVICE}-cachetable" --region "$REGION" --wait
}

deploy_service() {
  echo "==> Deploying $SERVICE"
  "${GCLOUD[@]}" run deploy "$SERVICE" --region "$REGION" --image "$IMAGE" \
    --allow-unauthenticated --port 8080 --add-cloudsql-instances "$SQL_CONNECTION" \
    --env-vars-file "$ENV_FILE" --set-secrets "$SECRETS" \
    --cpu 1 --memory 512Mi --concurrency 40 \
    --min-instances "${MIN_INSTANCES:-0}" --max-instances "${MAX_INSTANCES:-2}" "${SA_FLAG[@]}"
  # MAX_INSTANCES: each instance can open 8 connections (2 workers x 4 threads) on PGLive's db-g1-small (~50 in all);
  # travel_app's CONNECTION LIMIT 12 is the hard cap. Raise both only after checking PGLive's headroom.
  deploy_job "${SERVICE}-manage" manage.py check --deploy
  deploy_job "${SERVICE}-clearsessions" manage.py clearsessions
  "${GCLOUD[@]}" run services describe "$SERVICE" --region "$REGION" --format 'value(status.url)'
}

manage() {  # run one management command as a job execution, e.g. "manage reset_admin_mfa owner"
  [[ $# -gt 0 ]] || { echo "usage: $0 manage <command> [args...]" >&2; exit 1; }
  local args; args=$(IFS=,; echo "manage.py,$*")
  local extra=()
  if [[ "$1" == "createsuperuser" ]]; then  # non-interactive: password from Secret Manager, never on the command line
    extra=(--update-secrets "DJANGO_SUPERUSER_PASSWORD=travel-admin-password:latest")
    "${GCLOUD[@]}" run jobs update "${SERVICE}-manage" --region "$REGION" "${extra[@]}"
  fi
  "${GCLOUD[@]}" run jobs execute "${SERVICE}-manage" --region "$REGION" --args "$args" --wait
}

schedule() {
  : "${SCHEDULER_SA:?set SCHEDULER_SA (service account allowed to run Cloud Run jobs)}"
  echo "==> Daily session clean-up at 03:30 IST"
  "${GCLOUD[@]}" scheduler jobs create http "${SERVICE}-clearsessions-daily" --location "$REGION" \
    --schedule "30 3 * * *" --time-zone "Asia/Kolkata" --http-method POST \
    --uri "https://run.googleapis.com/v2/projects/${PROJECT_ID}/locations/${REGION}/jobs/${SERVICE}-clearsessions:run" \
    --oauth-service-account-email "$SCHEDULER_SA"
}

case "${1:-}" in
  build) build ;;
  migrate) migrate ;;
  deploy) deploy_service ;;
  release) build; migrate; deploy_service ;;
  manage) shift; manage "$@" ;;
  schedule) schedule ;;
  *) echo "usage: $0 {release|build|migrate|deploy|manage <command> [args]|schedule}" >&2; exit 1 ;;
esac
