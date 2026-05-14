# NetflixClone DevSecOps Starter Kit

Generated for a Python Flask service.

## Contents

- `Dockerfile` with a minimal runtime image and non-root execution
- CI pipeline with unit tests, dependency scanning, image scanning, SBOM generation, and IaC scanning
- Kubernetes deployment, service, config, secret example, and optional runtime controls
- Security scanner configuration for Trivy and Checkov

## Quick Start

```bash
docker build -t docker.io/sivanext/netflix_clone:latest .
trivy image --severity HIGH,CRITICAL docker.io/sivanext/netflix_clone:latest
kubectl create namespace devsecops
kubectl apply -n devsecops -f k8s/
```

## Pipeline Gates

The generated pipeline blocks builds on `HIGH,CRITICAL` findings. Adjust the gate only after agreeing on the risk policy for the target environment.

## Supply Chain Additions

Recommended next steps:

- Sign images with cosign before promotion
- Store SBOMs with build artifacts
- Enable Dependabot or Renovate for dependency updates
- Move secrets into Vault, cloud KMS, or SealedSecrets
