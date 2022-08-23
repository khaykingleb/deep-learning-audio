#!/bin/bash

get_lj_speech_dataset () {
    mkdir -p "$1"
    wget --output-document "$1"/LJSpeech.tar.bz2 "$2" && \
        tar -xvf "$1"/LJSpeech.tar.bz2 --directory "$1" && \
        mv "$1"/LJSpeech-1.1 "$1"/lj_speech && \
        rm "$1"/LJSpeech.tar.bz2
}

"$@"
