#!/usr/bin/env python3
"""Turn raw media into web-ready passport assets (Specification §4.8). Never commit the originals.

    python3 tools/process_media.py INPUT_DIR            # writes to assets/media/passport/

Naming convention: chain-stage-subject-NN, e.g.  A3-scraping-hands-01.jpg  ->  A3-scraping-hands-01.webp
The passport finds media by the tier ID at the start of the name (A1..E5, or MAT).
Optional: put alt text in A3-scraping-hands-01.txt next to the output; the build reads it.

 images  .jpg/.jpeg/.png/.tif  resized to <=1600px long edge, EXIF stripped (no device/location data), WebP q80
 raws    .ARW (no extension? rename to .ARW)  export to JPEG from your raw editor first, then run this
 video   .mp4/.mov  re-encoded muted, <=720p, ~2-4 MB MP4 (+ WebP poster frame)  — needs ffmpeg
"""
import pathlib, subprocess, sys, shutil
try:
    from PIL import Image
except ImportError:
    sys.exit("pip install Pillow")
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else sys.exit(__doc__)
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets/media/passport"
OUT.mkdir(parents=True, exist_ok=True)
for f in sorted(SRC.iterdir()):
    ext = f.suffix.lower()
    stem = f.stem
    if ext in (".jpg", ".jpeg", ".png", ".tif", ".tiff"):
        im = Image.open(f); im = im.convert("RGB")
        im.thumbnail((1600, 1600))
        clean = Image.new("RGB", im.size); clean.putdata(list(im.getdata()))   # drops all metadata
        clean.save(OUT / f"{stem}.webp", "WEBP", quality=80, method=6)
        print("image", f.name)
    elif ext in (".mp4", ".mov"):
        if not shutil.which("ffmpeg"): print("skip (no ffmpeg):", f.name); continue
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-an", "-vf", "scale='min(1280,iw)':-2",
                               "-c:v", "libx264", "-crf", "30", "-preset", "slow", "-movflags", "+faststart", "-map_metadata", "-1", str(OUT / f"{stem}.mp4")])
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-frames:v", "1", "-vf", "scale='min(1280,iw)':-2", str(OUT / f"{stem}.poster.webp")])
        print("video", f.name)
    elif ext == ".arw" or ext == "":
        print("raw (export to JPEG first, keep raws OUTSIDE the repo):", f.name)
