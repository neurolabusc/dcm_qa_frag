
## About

Two DICOM series from [dcm_qa_xa30i](https://github.com/neurolabusc/dcm_qa_xa30i),
recompressed and fragmented with [gdcmconv](https://manpages.ubuntu.com/manpages/jammy/man1/gdcmconv.1.html) 3.2.2:

- `5001_anat-T1w_acq-tfl` — JPEG Lossless (`--jpeg`)
- `6001_anat-T1w_acq-tfl` — JPEG2000 Lossless (`--j2k`)

Both pass `--split 3000` so a single codec bitstream spans multiple
`(FFFE,E000)` items — the multi-fragment, single-frame edge case.
Fragmentation inflates file size and is poorly supported in practice,
so it should be avoided when authoring DICOMs. This repo validates
that dcm2niix handles it correctly. `gdcm2frag.py` regenerates `In/`
from a directory of uncompressed slices.

## Running

Run `batch.sh`. It converts `In/` → `Out/` and diffs against `Ref/`.
Requires dcm2niix v1.0.20260603 or later, built with OpenJPEG
(`-DUSE_OPENJPEG=ON`).
