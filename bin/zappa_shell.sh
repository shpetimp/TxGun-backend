#!/bin/bash
BIN="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd $BIN/..
docker run -ti \
    -e AWS_PROFILE=$AWS_PROFILE \
    -v $(pwd):/var/task \
    -v ~/.aws/:/root/.aws  \
    --rm \
    lambci/lambda:build-python3.6 \
    bash -c "source pyenv/bin/activate && bash"
