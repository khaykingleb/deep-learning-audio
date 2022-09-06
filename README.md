# Deep-Learning-for-Audio

![release][release]

# Usage

* Initialize the repository:

  ```shell
  git clone https://github.com/khaykingleb/Deep-Learning-for-Audio.git && cd Deep-Learning-for-Audio
  ```
* Build the image:

  ```shell
  docker build -t deep-learning-for-audio .
  ```
* Run the container:

  ```shell
  docker run -dte WANDB_API_KEY="$WANDB_API_KEY" deep-learning-for-audio
  ```
* Get data from S3:

  ```shell
  dvc pull
  ```
* Train a model:

  ```shell
  poetry run python3 -m src.core.<TASK> --config_path=configs/<TASK>/<MODEL>.yaml
  ```

[release]: https://github.com/khaykingleb/Deep-Learning-for-Audio/actions/workflows/release.yaml/badge.svg
