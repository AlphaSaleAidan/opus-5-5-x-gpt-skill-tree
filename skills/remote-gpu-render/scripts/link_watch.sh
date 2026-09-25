#!/bin/bash
# Server side: probe the GPU PC through the reverse tunnel every 60 s, log state CHANGES only.
# usage: link_watch.sh <port> <user> <key> <logfile>      stop: touch /tmp/gpu-link-watch-stop
# run detached: setsid nohup link_watch.sh 52122 gpuuser ~/.ssh/id_gpupc /var/log/gpu_link.log < /dev/null > /dev/null 2>&1 &
PORT=${1:?port}; U=${2:?user}; KEY=${3:?key}; L=${4:?logfile}; prev=""
while [ ! -f /tmp/gpu-link-watch-stop ]; do
  if timeout 25 ssh -o BatchMode=yes -o ConnectTimeout=15 -p "$PORT" -i "$KEY" "$U@localhost" "echo ok" >/dev/null 2>&1; then s=UP; else s=DOWN; fi
  [ "$s" != "$prev" ] && echo "$(date '+%F %T') GPU link $s" >> "$L"; prev=$s; sleep 60
done
