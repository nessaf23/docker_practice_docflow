#!/bin/bash

IMAGE="${1:?}"

curl -o "/tmp/${IMAGE}" "http://localhost:18080/?image=${IMAGE}"