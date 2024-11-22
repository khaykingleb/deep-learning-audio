# Efficient Deep Learning

Library for efficient deep learning research (inspired by [ashleve/lightning-hydra-template](https://github.com/ashleve/lightning-hydra-template)).


## Getting Started

* Install [asdf](https://asdf-vm.com/guide/getting-started.html) for managing different tool versions.
* For local development outside of Docker, make sure to run `make init-local` first to install dependencies.
* For development inside Docker, run the following commands:

    ```bash
    make init && make build
    ```

  Then you can use `make run` to start the container and work with it.