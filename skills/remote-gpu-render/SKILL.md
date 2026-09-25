---
name: remote-gpu-render
description: Use when a GPU job (FaceFusion face swap/face editor/face enhancer, Real-ESRGAN upscale to 4K, Seed-VC voice conversion, any CUDA onnxruntime/torch job) is too slow on a CPU server and a Windows PC with an NVIDIA card is available over SSH, or when that PC's tunnel drops, CUDA libraries fail to load, or its output doesn't match what was requested.
---

# Remote GPU render (Windows RTX box over a reverse tunnel)

## Overview
The CPU server orchestrates; the Windows PC does the CUDA work. The PC dials OUT to the server with a
reverse SSH tunnel (no port-forwarding on the home router), a keep-awake supervisor keeps it up, and the
PC's own Claude session watches the PC side. **Nothing the PC reports counts until the server has
ffprobed the output file itself.**

Routing rule: FaceFusion swap/gaze/restore, ESRGAN 4K, Seed-VC → GPU. Light assembly, mixing,
captions → the server. On CPU the same FaceFusion face_editor pass ran ~11 s/frame (30 min / 169 frames).

## Link setup
1. PC: enable **OpenSSH Server**; admin users' keys go in `C:\ProgramData\ssh\administrators_authorized_keys`
   (not `~\.ssh\authorized_keys`), ACL admin+SYSTEM only.
2. Server: the PC's tunnel key in `authorized_keys` restricted with `permitlisten="localhost:<port>"` —
   the port must match what the PC requests, or the forward silently fails.
3. PC: `scripts/tunnel_keepawake.ps1 -Server user@server -Port 52122 -Key ...` (SetThreadExecutionState
   + restart loop with `ExitOnForwardFailure`, `ServerAliveInterval 30`). Run as a logon task.
4. Server: reach the PC with `ssh -p 52122 -i ~/.ssh/<key> <pcuser>@localhost`; watchdog
   `scripts/link_watch.sh 52122 <pcuser> <key> <log>` under `setsid nohup … < /dev/null &` (logs changes only).
5. A tunnel that "just died" after weeks: check whether something else on the server took the port
   (an sshd port change killed ours once) before debugging the PC.

## FaceFusion on CUDA — gotchas we hit
| Symptom | Fix |
|---|---|
| `onnxruntime_providers_cuda.dll … depends on cublasLt64_12.dll which is missing` (falls back to CPU silently) | `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12 nvidia-cuda-runtime-cu12` and prepend each package's `bin` dir to PATH in the launcher `.bat` (`site-packages\nvidia\*\bin`) |
| `ModuleNotFoundError: onnxruntime` after installing | install `onnxruntime-gpu` into the SAME venv FaceFusion runs from (`install.py --onnxruntime cuda`), not the user site |
| protobuf version clash on import (another package upgraded it) | reinstall the protobuf version FaceFusion's requirements pin |
| `torchvision … requires torch==2.5.1+cu121` after upgrading torch | install the matching torchvision from the same CUDA index (`--index-url …/cu124`) |
| 4K upscale | use `--output-video-scale 2.0`, not a resolution flag. ALWAYS `ffprobe` width/height/frames of the output |
| Card is power-capped (≈370 W) | keep `--execution-thread-count 2` |
Proof that CUDA is live: log line `execution_providers=['cuda']` AND an onnxruntime session listing
`CUDAExecutionProvider` first; GPU utilisation in `nvidia-smi` during the run.

## Job pattern
```bash
scp -P 52122 in.mp4 user@localhost:C:/jobs/in.mp4
ssh -p 52122 user@localhost "C:\\jobs\\ffgpu.bat headless-run -t C:\\jobs\\in.mp4 -o C:\\jobs\\out.mp4 \
  --processors frame_enhancer --frame-enhancer-model real_esrgan_x2 --output-video-scale 2.0 \
  --execution-providers cuda --execution-thread-count 2"
scp -P 52122 user@localhost:C:/jobs/out.mp4 .
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=width,height,nb_read_frames,r_frame_rate -of csv=p=0 out.mp4   # verify, then use
```
`ffgpu.bat` = activate the venv, set the CUDA DLL PATH, `python facefusion.py %*`.

## Pairing with the PC's own Claude session
- The PC session owns PC-side setup (installs, drivers, keep-awake, tunnel) and guards the machine;
  the server session owns jobs and verification. Message it concrete asks; never ask it to change its
  own permissions.
- Its "done" is a claim. Verify from output only: file exists, ffprobe dims/frames/fps match the ask,
  a frame grab looks right at client zoom.

## What FAILED
- Assuming FaceFusion used the GPU because `--execution-providers cuda` was passed: it fell back to CPU
  on the missing cuBLAS DLL. Check the providers line.
- An output-resolution flag instead of `--output-video-scale 2.0` for the 4K upscale: don't; and never
  report "4K done" without ffprobe numbers.
- A sleeping PC drops the tunnel (and any job with it) — the keep-awake supervisor is not optional.
- `pgrep -f`/`pkill -f` patterns that also match your own shell: kill by PID found from the port/log.

## Status
`link_watch.sh` is the job's watchdog, generalized. `tunnel_keepawake.ps1` is an **untested template**
written from the setup used on the job.
