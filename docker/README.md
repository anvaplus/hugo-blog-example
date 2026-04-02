# Docker Build Guide

This repository includes a multi-stage Docker build that packages the Hugo site into a small runtime image.

The container does two separate jobs:

1. Build the static site with Hugo.
2. Serve the generated files with nginx.

This separation keeps the final image smaller, removes build tooling from runtime, and makes the container easier to run in Kubernetes.

## Files Involved

- `../Dockerfile`: defines the multi-stage image build
- `nginx.conf`: nginx runtime configuration used in the final container
- `../.dockerignore`: removes unnecessary files from the Docker build context

## How The Dockerfile Works

The Dockerfile has three stages.

### Stage 1: `hugo-installer`

This stage downloads a pinned Hugo Extended release and verifies it with the official checksum file.

What it does:

- Uses `alpine:3.22` as a minimal base
- Detects the current build architecture with `uname -m`
- Maps the architecture to either `amd64` or `arm64`
- Downloads the matching Hugo Extended archive from the Hugo GitHub releases page with `curl`
- Follows redirects only when they stay on HTTPS
- Downloads the official checksum file with the same HTTPS-only redirect policy
- Verifies the archive before extracting it
- Installs the `hugo` binary into `/usr/local/bin/hugo`

Why this stage exists:

- Keeps Hugo version pinning explicit
- Prevents downgrade to insecure redirect targets during download
- Verifies the downloaded binary before using it
- Avoids depending on an external prebuilt Hugo image

### Stage 2: `builder`

This stage builds the site.

What it does:

- Uses `alpine:3.22`
- Installs the runtime libraries Hugo needs on Alpine
- Creates a non-root `builder` user
- Copies the Hugo binary from the previous stage
- Copies only the files needed to build the site
- Runs `hugo --gc --minify --cacheDir /tmp/hugo_cache --destination /tmp/public`

Why this stage exists:

- Produces a clean static site output under `/tmp/public`
- Keeps the build isolated from the final runtime image
- Avoids serving source files directly from the runtime image

### Stage 3: `runtime`

This is the final image that actually runs in Docker or Kubernetes.

What it does:

- Uses `cgr.dev/chainguard/nginx:latest`
- Copies `nginx.conf` into `/etc/nginx/nginx.conf`
- Copies the generated site from `/tmp/public` into `/usr/share/nginx/html/`
- Runs as non-root user `65532`
- Exposes port `8080`

Why this stage exists:

- Uses a minimal hardened runtime image
- Serves only static files
- Keeps the final image smaller and lower risk than a full build environment

## What nginx Does In This Setup

The final container does not run Hugo. Hugo is only used at build time.

At runtime, nginx is responsible for:

- Listening on port `8080`
- Serving static files from `/usr/share/nginx/html`
- Returning `/healthz` for health checks
- Adding security headers to responses
- Denying access to hidden files such as dotfiles
- Writing logs to stdout and stderr for container platforms

This behavior is defined in `nginx.conf`.

## Security Choices

This setup includes a few practical security layers.

- Multi-stage build: keeps build tools out of the final image
- Pinned Hugo version: avoids drifting to an untested release
- HTTPS-only redirects for Hugo downloads: prevents fallback to insecure redirect targets
- Checksum verification: validates the downloaded Hugo archive
- Non-root builder user: reduces risk during the build stage
- Non-root runtime user: avoids running nginx as root
- Minimal runtime image: reduces attack surface
- Security headers in nginx:
  - `X-Content-Type-Options`
  - `X-Frame-Options`
  - `Referrer-Policy`
  - `Permissions-Policy`
  - `Content-Security-Policy`
- Dotfile blocking: prevents accidental exposure of hidden files
- Reduced build context via `.dockerignore`

## Build Commands

Build for the current local machine:

```bash
docker buildx build --load -t personal-blog:local .
```

Build explicitly for Linux ARM64:

```bash
docker buildx build --platform linux/arm64 --load -t personal-blog:arm64 .
```

Build explicitly for Linux AMD64:

```bash
docker buildx build --platform linux/amd64 --load -t personal-blog:amd64 .
```

Build and push a multi-architecture image:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t your-registry/personal-blog:latest --push .
```

## Run The Container

Run the image locally:

```bash
docker run --rm -p 8080:8080 personal-blog:local
```

Test the container:

```bash
curl -I http://127.0.0.1:8080/
curl http://127.0.0.1:8080/healthz
```

## Build Flow Summary

End-to-end flow:

1. Docker downloads and verifies Hugo.
2. Hugo builds the static site into `/tmp/public`.
3. The runtime image copies only the generated static files.
4. nginx serves the site on port `8080`.

That means the final container contains the website output, not the full Hugo toolchain.