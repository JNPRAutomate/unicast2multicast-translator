#!/usr/bin/env bash
# Exit on first error
set -o errexit
# Install FFmpeg
apt-get update && apt-get install -y ffmpeg