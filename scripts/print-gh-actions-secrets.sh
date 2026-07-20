#!/usr/bin/env bash
# Mostra os valores para colar em GitHub → Settings → Secrets and variables → Actions
# Não versiona a chave: lê ~/.ssh/github-actions/bibliotecaquintal_deploy (mesma chave da VPS o5o)
set -euo pipefail
KEY="${HOME}/.ssh/github-actions/bibliotecaquintal_deploy"
if [[ ! -f "$KEY" ]]; then
  echo "Chave não encontrada: $KEY" >&2
  exit 1
fi

echo "Repo: JallsBR/ControleFinanceiro"
echo "Settings → Secrets and variables → Actions → New repository secret"
echo
echo "=== Recomendado: VPS_SSH_KEY_B64 (cole a linha inteira abaixo) ==="
base64 -w0 "$KEY"
echo
echo
echo "=== Alternativa (frágil): VPS_SSH_KEY (bloco PEM completo) ==="
cat "$KEY"
echo
echo "=== Opcional: DEPLOY_HOOK_TOKEN ==="
echo "(mesmo token configurado no VPS para /__deploy__/deploy)"
echo
echo "Host fixo no workflow: root@76.13.231.242"
echo "Branch de deploy: deploy"
