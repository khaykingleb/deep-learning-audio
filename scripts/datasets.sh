#!/bin/bash

get_lj_speech_dataset () {
    mkdir -p resources/datasets/asr && \
        wget --output-document resources/datasets/asr/LJSpeech.tar.bz2 \
        https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2 && \
        tar -xvf resources/datasets/asr/LJSpeech.tar.bz2 --directory resources/datasets/asr && \
        mv resources/datasets/asr/LJSpeech-1.1 resources/datasets/asr/lj_speech && \
        rm resources/datasets/asr/LJSpeech.tar.bz2
}

"$@"
