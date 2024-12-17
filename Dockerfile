FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu24.04
WORKDIR /app

# Set SHELL to bash with pipefail option as we use pipes in our scripts
# See https://github.com/hadolint/hadolint/wiki/DL4006 for more information
SHELL ["/bin/bash", "-l", "-o", "pipefail", "-c"]

# Install general dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl=8.5.0-2ubuntu10.5 \
                                                  git=1:2.43.0-1ubuntu7.1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install asdf
RUN git clone https://github.com/asdf-vm/asdf.git "$HOME/.asdf" --branch v0.14.1 \
    && echo ". $HOME/.asdf/asdf.sh" >> "$HOME/.profile" \
    && echo ". $HOME/.asdf/asdf.sh" >> "$HOME/.bashrc" \
    && echo ". $HOME/.asdf/completions/asdf.bash" >> "$HOME/.bashrc"
COPY .tool-versions .

# Install Python build dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -y zlib1g-dev=1:1.3.dfsg-3.1ubuntu2.1 \
                                                  libssl-dev=3.0.13-0ubuntu3.4 \
                                                  libbz2-dev=1.0.8-5.1build0.1 \
                                                  libsqlite3-dev=3.45.1-1ubuntu2 \
                                                  libffi-dev=3.4.6-1build1 \
                                                  libreadline-dev=8.2-4build1 \
                                                  liblzma-dev=5.6.1+really5.4.5-1build0.1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python
RUN asdf plugin-add python https://github.com/asdf-community/asdf-python.git \
    && asdf install python

# Install Poetry package manager
RUN asdf plugin-add poetry https://github.com/asdf-community/asdf-poetry.git \
    && asdf install poetry \
    && poetry config virtualenvs.create false

# Poetry dependencies installation
RUN apt-get update \
    && apt-get install --no-install-recommends -y libsndfile1=1.2.2-1ubuntu5 \
                                                  libsox-dev=14.4.2+git20190427-4build4 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/$/.cache/pypoetry/cache \
    --mount=type=cache,target=/root/.cache/pypoetry/artifacts \
    poetry install \
        --no-interaction \
        --no-ansi \
        --no-root \
        --no-cache \
        --only main,audio

# Install root package
COPY . .
RUN poetry install --only-root
