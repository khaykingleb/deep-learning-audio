# Deep-Learning-for-Audio

![release][release]

# Usage
* To initialize the repository:
    ```shell
    git clone https://github.com/khaykingleb/Deep-Learning-for-Audio.git && \
        cd Deep-Learning-for-Audio && \
        make repo-init
    ```

* To build the image:
    ```shell
    docker build -t deep-learning-for-audio .
    ```

* To train a model:
    ```shell
    poetry run python3 -m src.core.<TASK> --config_path=configs/<TASK>/<MODEL>.yaml
    ```

[release]: https://github.com/khaykingleb/Deep-Learning-for-Audio/actions/workflows/release.yaml/badge.svg
