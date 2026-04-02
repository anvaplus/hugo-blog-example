# personal-blog

This repository README is focused on Docker build and container delivery details for the blog.

## Container Build

Build the container image for your local machine:

```bash
docker buildx build --load -t personal-blog:local .
```

Build an explicit Linux `arm64` image:

```bash
docker buildx build --platform linux/arm64 --load -t personal-blog:arm64 .
```

Build an explicit Linux `amd64` image:

```bash
docker buildx build --platform linux/amd64 --load -t personal-blog:amd64 .
```

Build a multi-architecture image for both `amd64` and `arm64` and push it to a registry:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t your-registry/personal-blog:latest --push .
```

## GitHub Actions Docker Workflows

This repository uses thin trigger workflows that delegate to reusable workflows in [`anvaplus/homelab-github-workflows`](https://github.com/alpian-technologies/ispwm-platform-github-workflows).

Centralized reusable workflows:

- `anvaplus/homelab-github-workflows/.github/workflows/Hugo_MergeRequest.yaml`
- `anvaplus/homelab-github-workflows/.github/workflows/Hugo_Deploy.yaml`

### Pull Request Validation

Wrapper file: `.github/workflows/MergeRequest.yaml`

Trigger behavior:

- PR opened against `main`
- PR reopened against `main`
- PR updated with new commits against `main`

Wrapper behavior:

- calls centralized `Hugo_MergeRequest.yaml`
- passes `SONAR_ORGANIZATION` as input
- passes `SONAR_TOKEN` as secret

### Publish After Merge

Wrapper file: `.github/workflows/Deploy.yaml`

Trigger behavior:

- push to `main`

Wrapper behavior:

- calls centralized `Hugo_Deploy.yaml`
- passes `dockerhub_username` (`anvaplus`) and `SONAR_ORGANIZATION` as inputs
- passes `DOCKERHUB_TOKEN` and `SONAR_TOKEN` as secrets

Required GitHub repository secrets:

- `DOCKERHUB_TOKEN`
- `SONAR_TOKEN`

Required GitHub repository variables:

- `SONAR_ORGANIZATION`

Example published image name:

- `docker.io/anvaplus/hugo-blog-example:v1.3.0-alpha.1`

## Run The Container

```bash
docker run --rm -p 8080:8080 personal-blog:local
```

For full Dockerfile stage-by-stage details and runtime behavior, see [docker/README.md](docker/README.md).