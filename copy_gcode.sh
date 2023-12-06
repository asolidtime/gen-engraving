#!/bin/bash

# Check if filename is provided
if [ -z "$1" ]
then
    echo "No filename provided. Usage: ./script.sh filename"
    exit 1
fi

# Set variables
filename=$1
remote_dir="/home/pi/klipper_sdcard/"
remote_user="pi"
remote_host="192.168.1.177"

# Copy file using SFTP
sftp ${remote_user}@${remote_host}:${remote_dir} <<< $"put ${filename}"