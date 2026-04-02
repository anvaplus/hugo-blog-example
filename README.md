# personal-blog

This repository is the public, deployment-focused companion for my blog at [andreivasiliu.com](https://andreivasiliu.com).

It exists to document how the site is structured and how it is prepared for self-hosting on Kubernetes. The goal is not to mirror the full published archive, but to expose the mechanics behind the platform work: Hugo layout, content structure, theme integration, and the pieces that support containerization and delivery.

## Scope

This repository is intentionally limited in scope.

What is included:

- Hugo site structure
- Blowfish theme integration
- Content layout and page bundle structure
- Custom layouts and styling overrides
- Example placeholder content that explains the repository purpose
- Deployment-oriented site wiring used for the blog platform

What is intentionally not included:

- The full blog archive
- Every article published on the production site
- A one-to-one copy of [andreivasiliu.com](https://andreivasiliu.com)

If you want to read the actual articles, use the production site instead:

- [Main blog](https://andreivasiliu.com)
- [Archive](https://andreivasiliu.com/archive/)
- [Roadmap post: From Hashnode to Kubernetes](https://andreivasiliu.com/from-hashnode-to-kubernetes-why-im-self-hosting-my-blog-like-a-bank-website/)

## Why This Repo Exists

The blog is being used as a real public-facing workload to demonstrate how platform engineering components fit together end to end.

The main blog explains the why and the migration roadmap. This repository shows the how for the delivery side:

- How the Hugo site is organized
- How posts are structured as page bundles
- How the site is prepared for containerization
- How the repository can support CI/CD, Helm, and GitOps-driven Kubernetes deployment

## Repository Structure

Key directories:

- `config/_default/` Hugo configuration
- `content/` site pages and placeholder content
- `content/blog/` public blog-facing content kept in this repo
- `assets/css/` custom styling overrides
- `layouts/` Hugo layout overrides on top of the Blowfish theme
- `static/` static assets such as the favicon
- `scripts/` helper automation scripts
- `themes/blowfish/` theme source via git submodule

## Local Development

Clone the repository with submodules:

```bash
git clone --recurse-submodules https://github.com/anvaplus/hugo-blog-example.git
cd hugo-blog-example
```

Run the local development server:

```bash
hugo server --disableFastRender --noHTTPCache
```

Build the site:

```bash
hugo
```

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

- `anvaplus/homelab-github-workflows/.github/workflows/Hugo_PullRequest.yaml`
- `anvaplus/homelab-github-workflows/.github/workflows/Hugo_Deploy.yaml`

### Pull Request Validation

Wrapper file: `.github/workflows/PullRequest.yaml`

Trigger behavior:

- PR opened against `main`
- PR reopened against `main`
- PR updated with new commits against `main`

Wrapper behavior:

- calls centralized `Hugo_PullRequest.yaml`
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