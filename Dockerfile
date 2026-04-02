# syntax=docker/dockerfile:1.7

ARG HUGO_VERSION=0.157.0

FROM alpine:3.22 AS hugo-installer

ARG HUGO_VERSION

RUN set -eux; \
    apk add --no-cache ca-certificates curl tar; \
        arch="$(uname -m)"; \
        case "$arch" in \
            x86_64|amd64) hugo_arch='amd64' ;; \
            aarch64|arm64) hugo_arch='arm64' ;; \
            *) echo "Unsupported architecture: $arch" >&2; exit 1 ;; \
    esac; \
        hugo_archive="hugo_extended_${HUGO_VERSION}_linux-${hugo_arch}.tar.gz"; \
        curl --proto '=https' --tlsv1.2 -fsSL -o "/tmp/${hugo_archive}" "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/${hugo_archive}"; \
        curl --proto '=https' --tlsv1.2 -fsSL -o /tmp/hugo_checksums.txt "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_checksums.txt"; \
        cd /tmp; \
        grep " ${hugo_archive}$" /tmp/hugo_checksums.txt | sha256sum -c -; \
        tar -xzf "/tmp/${hugo_archive}" -C /tmp hugo; \
    install -m 0755 /tmp/hugo /usr/local/bin/hugo

FROM alpine:3.22 AS builder

ENV HUGO_ENV=production \
    HUGO_ENVIRONMENT=production

WORKDIR /src

RUN set -eux; \
    apk add --no-cache ca-certificates git libc6-compat libgcc libstdc++; \
    addgroup -S builder; \
    adduser -S -G builder -h /home/builder builder; \
    mkdir -p /src /tmp/hugo_cache /home/builder; \
    chown -R builder:builder /src /tmp/hugo_cache /home/builder

COPY --from=hugo-installer /usr/local/bin/hugo /usr/local/bin/hugo

COPY --chown=builder:builder archetypes/ /src/archetypes/
COPY --chown=builder:builder assets/ /src/assets/
COPY --chown=builder:builder config/ /src/config/
COPY --chown=builder:builder content/ /src/content/
COPY --chown=builder:builder data/ /src/data/
COPY --chown=builder:builder i18n/ /src/i18n/
COPY --chown=builder:builder layouts/ /src/layouts/
COPY --chown=builder:builder static/ /src/static/
COPY --chown=builder:builder themes/ /src/themes/

USER builder

RUN set -eux; \
    hugo --gc --minify --cacheDir /tmp/hugo_cache --destination /tmp/public

FROM cgr.dev/chainguard/nginx:latest AS runtime

LABEL org.opencontainers.image.title="personal-blog" \
      org.opencontainers.image.description="Hardened container image for the public Hugo blog companion repository" \
      org.opencontainers.image.source="https://github.com/anvaplus/hugo-blog-example"

COPY --chown=65532:65532 docker/nginx.conf /etc/nginx/nginx.conf
COPY --from=builder --chown=65532:65532 /tmp/public/ /usr/share/nginx/html/

USER 65532:65532

EXPOSE 8080
