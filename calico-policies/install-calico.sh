#!/usr/bin/env bash
# Install Calico on the flannel-less K3s variant (see ansible-k3s README
# for the required k3s_server_extra_args). Run on tpi2-2 with KUBECONFIG set.
# VERIFY operator version against https://github.com/projectcalico/calico/releases
set -euo pipefail

CALICO_VERSION="${CALICO_VERSION:-v3.30.1}"

kubectl create -f "https://raw.githubusercontent.com/projectcalico/calico/${CALICO_VERSION}/manifests/tigera-operator.yaml" || true

kubectl apply -f - <<'EOF'
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  calicoNetwork:
    ipPools:
      - cidr: 10.42.0.0/16          # matches k3s --cluster-cidr
        encapsulation: VXLAN
EOF

kubectl wait --for=condition=Available tigeraStatus/calico --timeout=600s || \
  kubectl get tigerastatus
echo "Calico installed. Apply policies with: kubectl apply -f policies/"
