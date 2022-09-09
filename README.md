# Deep-Learning-for-Audio

![release][release]

# Getting Started

Make sure that you have `make --version` greater than 3.81.

* Cloning the repository:
  ```shell
  git clone https://github.com/khaykingleb/Deep-Learning-for-Audio.git && cd Deep-Learning-for-Audio
  ```

* Looking up targets:
  ```shell
  make help
  ```

* Training models:
  ```shell
  poetry shell
  python3 -m src.core.<TASK> --config_path=<CONFIG>.yaml
  ```


[release]: https://github.com/khaykingleb/Deep-Learning-for-Audio/actions/workflows/release.yaml/badge.svg
