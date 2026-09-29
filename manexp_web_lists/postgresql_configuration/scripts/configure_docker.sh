#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_NAME

log() {
    printf '[%s] %s\n' "$SCRIPT_NAME" "$1"
}

error() {
    printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$1" >&2
}

die() {
    error "$1"
    exit 1
}

require_linux() {
    if [[ "$(uname -s)" != "Linux" ]]; then
        die "This script only supports Linux."
    fi
}

require_root_privileges() {
    if ! command -v sudo >/dev/null 2>&1; then
        die "sudo is required but was not found."
    fi

    if ! sudo -v; then
        die "Unable to obtain sudo privileges."
    fi
}

load_os_release() {
    if [[ ! -r /etc/os-release ]]; then
        die "Cannot determine Linux distribution: /etc/os-release is missing."
    fi

    # shellcheck disable=SC1091
    source /etc/os-release

    readonly OS_ID="${ID:-}"
    readonly OS_VERSION_CODENAME="${VERSION_CODENAME:-}"
}

is_docker_installed() {
    command -v docker >/dev/null 2>&1
}

is_docker_available() {
    sudo docker info >/dev/null 2>&1
}

install_docker_debian() {
    log "Installing Docker Engine using Docker's official APT repository..."

    sudo apt-get update

    sudo apt-get install -y \
        ca-certificates \
        curl

    sudo install -m 0755 -d /etc/apt/keyrings

    if [[ ! -f /etc/apt/keyrings/docker.asc ]]; then
        log "Installing Docker repository signing key..."

        sudo curl \
            --fail \
            --silent \
            --show-error \
            --location \
            https://download.docker.com/linux/"${OS_ID}"/gpg \
            --output /etc/apt/keyrings/docker.asc

        sudo chmod a+r /etc/apt/keyrings/docker.asc
    fi

    log "Configuring Docker APT repository..."

    local docker_sources="/etc/apt/sources.list.d/docker.sources"

    if [[ ! -f "$docker_sources" ]]; then
        sudo tee "$docker_sources" >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/${OS_ID}
Suites: ${OS_VERSION_CODENAME}
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
    fi

    sudo apt-get update

    sudo apt-get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin
}

install_docker() {
    case "$OS_ID" in
        debian|ubuntu)
            if [[ -z "$OS_VERSION_CODENAME" ]]; then
                die "Could not determine the ${OS_ID} release codename."
            fi

            install_docker_debian
            ;;

        *)
            die "Unsupported Linux distribution: ${OS_ID}. Docker installation is not implemented for this distribution."
            ;;
    esac
}

ensure_docker_service() {
    if ! command -v systemctl >/dev/null 2>&1; then
        die "systemctl was not found. This script currently requires systemd."
    fi

    log "Ensuring Docker service is enabled and running..."

    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service

    sudo systemctl start docker.service

    if ! sudo systemctl is-active --quiet docker.service; then
        error "Docker service failed to start."

        sudo systemctl status docker.service --no-pager >&2 || true

        die "Docker daemon is not running."
    fi
}

verify_docker() {
    log "Checking Docker availability..."

    if ! sudo docker info >/dev/null 2>&1; then
        die "Docker is installed but the Docker daemon is not accessible."
    fi

    local docker_version

    docker_version="$(sudo docker version --format '{{.Server.Version}}' 2>/dev/null)" \
        || die "Unable to retrieve Docker server version."

    log "Docker Engine ${docker_version} is available."
}

main() {
    log "Starting Docker configuration..."

    require_linux
    require_root_privileges
    load_os_release

    log "Detected Linux distribution: ${OS_ID}"

    if is_docker_installed; then
        log "Docker CLI is already installed."
    else
        log "Docker CLI is not installed."
        install_docker
    fi

    if ! command -v docker >/dev/null 2>&1; then
        die "Docker installation completed but the docker command is still unavailable."
    fi

    ensure_docker_service
    verify_docker

    log "Docker configuration completed successfully."
}

main "$@"
