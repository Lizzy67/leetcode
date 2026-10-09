#!/usr/bin/env bash
# Sync this repo's docs/ -> target repo collections/l00491999/
# (collections is a sibling of docs in the target repo)
# Designed for repeated use (long-term sync).
#
# Usage (run from a machine that can reach the internal git host):
#   export TARGET_GIT_USER='l00491999'
#   export TARGET_GIT_PASS='********'   # do NOT hardcode; prefer prompt / credential helper
#   ./scripts/sync-docs-to-xiaoyi.sh
#
# Optional env:
#   TARGET_REPO_URL  default: https://7.192.174.176/git/xiaoyi/workspace
#   TARGET_BRANCH    default: master (falls back to main)
#   TARGET_PREFIX    default: collections/l00491999
#   COMMIT_MSG       default: sync docs from source repo

set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DOCS="${SOURCE_ROOT}/docs"

TARGET_REPO_URL="${TARGET_REPO_URL:-https://7.192.174.176/git/xiaoyi/workspace}"
TARGET_PREFIX="${TARGET_PREFIX:-collections/l00491999}"
TARGET_BRANCH="${TARGET_BRANCH:-}"
COMMIT_MSG="${COMMIT_MSG:-sync: update ${TARGET_PREFIX} from local docs}"
if [[ ! -d "${SOURCE_DOCS}" ]]; then
  echo "ERROR: source docs not found: ${SOURCE_DOCS}" >&2
  exit 1
fi

if [[ -z "${TARGET_GIT_USER:-}" ]]; then
  read -r -p "Git username: " TARGET_GIT_USER
fi
if [[ -z "${TARGET_GIT_PASS:-}" ]]; then
  read -r -s -p "Git password / token: " TARGET_GIT_PASS
  echo
fi

# Embed credentials only in a temporary URL (never written to disk config permanently).
# URL-encode password minimally for common special chars.
urlencode() {
  python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"
}
USER_ENC="$(urlencode "${TARGET_GIT_USER}")"
PASS_ENC="$(urlencode "${TARGET_GIT_PASS}")"

# Support .../workspace or .../workspace.git
BASE_URL="${TARGET_REPO_URL%/}"
BASE_URL="${BASE_URL%.git}"
AUTH_URL="https://${USER_ENC}:${PASS_ENC}@${BASE_URL#https://}"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/xiaoyi-sync.XXXXXX")"
cleanup() {
  rm -rf "${WORK}"
}
trap cleanup EXIT

echo "==> Cloning target repo..."
# Internal hosts sometimes use self-signed certs
GIT_SSL_NO_VERIFY="${GIT_SSL_NO_VERIFY:-1}"
export GIT_SSL_NO_VERIFY

git clone --depth 1 "${AUTH_URL}" "${WORK}/repo"
cd "${WORK}/repo"

if [[ -z "${TARGET_BRANCH}" ]]; then
  TARGET_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
fi
git checkout "${TARGET_BRANCH}"

mkdir -p "${TARGET_PREFIX}"
echo "==> Syncing ${SOURCE_DOCS}/ -> ${TARGET_PREFIX}/"
# Archive copy preserves structure; delete removed files in destination.
rsync -a --delete \
  --exclude '.git/' \
  "${SOURCE_DOCS}/" \
  "${TARGET_PREFIX}/"

git add -A -- "${TARGET_PREFIX}"
if git diff --cached --quiet; then
  echo "==> No changes to push."
  exit 0
fi

git -c user.name="${GIT_AUTHOR_NAME:-${TARGET_GIT_USER}}" \
    -c user.email="${GIT_AUTHOR_EMAIL:-${TARGET_GIT_USER}@users.noreply.local}" \
    commit -m "${COMMIT_MSG}"

echo "==> Pushing to ${TARGET_BRANCH}..."
git push origin "HEAD:${TARGET_BRANCH}"
echo "==> Done. Synced to ${TARGET_PREFIX}"
