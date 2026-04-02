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

On Apple Silicon, Docker Desktop will normally build the Linux `arm64` image by default.

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

This repository includes two separate GitHub Actions workflows for container automation.

### 1. Pull Request Validation

Workflow file: `.github/workflows/MergeRequest.yml`

Trigger behavior:

- PR opened against `main`
- PR reopened against `main`
- PR updated with new commits against `main`

What it does:

- checks out the repository with submodules
- runs a Gitleaks secret scan
- runs a Trivy configuration scan
- runs a SonarQube code scan
- sets up Docker Buildx
- builds a local `linux/amd64` image for security verification
- runs a Trivy image scan on that local image
- builds the container for both `linux/amd64` and `linux/arm64`
- verifies that the code builds and that the image can be created
- does not push anything to Docker Hub

### 2. Publish After Merge

Workflow file: `.github/workflows/Deploy.yml`

Trigger behavior:

- push to `main` (post-merge)

What it does:

- checks out the commit on `main`
- runs the custom semantic versioning strategy described in [VERSIONING_STRATEGY](https://github.com/anvaplus/github-actions-common/blob/main/VERSIONING_STRATEGY.md)
- generates an `alpha` semantic version such as `v1.3.0-alpha.1`
- tags the Git repository with that generated version
- builds a local `linux/amd64` image and runs a Trivy image scan before publishing
- builds and pushes a multi-architecture image to Docker Hub for:
	- `linux/amd64`
	- `linux/arm64`
- runs a SonarQube code scan
- publishes the Docker image using only that generated alpha version tag

Required GitHub repository secrets:

- `DOCKERHUB_TOKEN`
- `SONAR_TOKEN`

Required GitHub repository variables:

- `SONAR_ORGANIZATION`

The Docker Hub username used by the deploy workflow is currently set in the workflow as `anvaplus`.

Example published image names:

- `docker.io/anvaplus/hugo-blog-example:v1.3.0-alpha.1`

The workflow needs repository `contents: write` permission because the custom versioning action is configured with `tag-repo: true`.

To ensure only validated PRs can be merged and published, configure branch protection on `main` and mark the PR validation workflow as a required status check.

Run it locally:

```bash
docker run --rm -p 8080:8080 personal-blog:local
```

The image uses a multi-stage build:

- A dedicated Hugo build stage that downloads and verifies the pinned Hugo extended binary
- A non-root nginx runtime stage based on a hardened minimal image
- A custom nginx configuration with basic security headers and dotfile protection
- Explicit Docker Buildx platform support for `linux/amd64` and `linux/arm64`
- A reduced Docker build context via `.dockerignore`

For a detailed explanation of the Dockerfile and runtime design, see [docker/README.md](docker/README.md).

## Notes

- The Blowfish theme is included as a submodule.
- The repository may contain placeholder content where the production blog contains full published articles.
- The public repo is optimized for explaining deployment and platform structure, not for duplicating the complete editorial archive.