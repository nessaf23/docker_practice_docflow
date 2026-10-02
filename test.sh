#!/bin/bash

log() {
  echo $@ > /dev/stdout
}

err() {
  log $@
  log "test failed"
  exit 1
}

upload_image() {
  upload_result=$(curl -f -m 5 -s -X POST -F "image=@testdata/python-large.png" http://localhost:18080/compress)
  if [[ $? != 0 ]]
  then
    err "can not upload image"
  fi

  IMAGE=$(echo "$upload_result" | jq -r '.message')
  if [[ "$IMAGE" == "null" ]]
  then
    err "can not extract image name"
  fi

  log "test image uploaded OK"
}

download_image() {
  curl -f -m 5 -s -o "/tmp/${IMAGE}" "http://localhost:18080/?image=${IMAGE}" 2>/dev/null
  if [[ $? != 0 ]]
  then
    err "can not download image"
  fi

  log "compressed image downloaded OK"

  if ! file "/tmp/${IMAGE}" | grep 'PNG image data, 51 x 51' >/dev/null
  then
    err "image size verification failed"
  fi

  log "compressed image size verified"
}

upload_image
download_image

log "test OK!"
