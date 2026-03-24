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