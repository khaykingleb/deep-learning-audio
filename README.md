# Research Playground

It's a library I created for efficient ML/DL research on various tasks (inspired by [ashleve/lightning-hydra-template](https://github.com/ashleve/lightning-hydra-template) and [NVIDIA/NeMo](https://github.com/NVIDIA/NeMo)).

## Key features:
- 🚀 Production-ready training pipelines
- 🧠 Actual model implementations
- ⚡️ Easy configuration management with Hydra
- 📊 Experiment tracking with Weights & Biases
- 🔧 Modular architecture for quick prototyping
- 🐳 Docker support for reproducible environments
- ☸️ Multi-GPU training with K3s and Terraform (soon) 

## Getting Started

1. Install [asdf](https://asdf-vm.com/guide/getting-started.html) to manage different tools' runtime versions.

2. Update `.env.example` to your needs.

3. Setup your training Hydra config in `configs/experiments/` folder.

4. Choose between local development outside or inside Docker container.

    * Outside of Docker (not recommended):

        ```bash
        make init-local
        poetry shell && python3 src train --experiment <experiment_name>
        ```
    * Inside Docker:

        ```bash
        make init && make build && make run
        python3 src train --experiment <experiment_name>
        ```

## Notes

* Use `make help` to see all available commands.

* Use `python3 src --help` to see all available CLI arguments.
