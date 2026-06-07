#!/usr/bin/env bash
# Carga .env sin usar `source` (valores con espacios/comas no rompen bash).
# Uso: source deploy/scripts/load-env.sh && load_dotenv [.env]

load_dotenv() {
  local file="${1:-.env}"
  if [[ ! -f "$file" ]]; then
    echo "ERROR: no existe $file" >&2
    return 1
  fi

  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%$'\r'}"
    [[ -z "${line//[[:space:]]/}" || "$line" =~ ^[[:space:]]*# ]] && continue
    [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]] || continue

    local key="${BASH_REMATCH[1]}"
    local val="${BASH_REMATCH[2]}"
    if [[ "$val" == \"*\" && "$val" == *\" ]]; then
      val="${val:1:${#val}-2}"
    fi
    export "${key}=${val}"
  done <"$file"
}
