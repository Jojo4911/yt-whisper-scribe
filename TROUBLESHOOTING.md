GPU / CUDA Troubleshooting

Symptoms
- SRT contains mostly punctuation (e.g., "!!!!", "..."), words missing
- Works with `--device cpu` but fails on `--device cuda`

Quick fixes
- Force FP32 on GPU: use `--fp16 false`
  Example: `python scripts/transcribe.py "URL" --device cuda --fp16 false`
- Update NVIDIA driver to match the CUDA build used by PyTorch
- Reinstall PyTorch with a compatible CUDA build for your GPU (e.g., cu121)

Why this happens
- Some GPU/driver/PyTorch combinations exhibit unstable FP16 inference for Whisper, producing degenerate outputs
- FP32 is more robust; use it when FP16 quality is poor

Version checks
```
python -c "import torch, platform; print('torch', torch.__version__, 'cuda', torch.version.cuda, 'cuda_available', torch.cuda.is_available()); import subprocess; subprocess.run(['nvidia-smi']); subprocess.run(['ffmpeg','-version'])"
```

If audio extraction is the problem
- Update yt-dlp: `python -m yt_dlp -U`
- Verify ffmpeg availability: `ffmpeg -version`
- Optionally, use cookies for restricted videos: `--cookies-file data/cookies.txt`

