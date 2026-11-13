---
title: "Bug in Lead-DBS 2.5"
description: "A bug in Lead-DBS 2.5 to 2.5.2 affected fMRI maps seeded from VTAs with normative functional connectomes. Version 2.5.3 fixes it."
date: "2021-07-16T13:58:53"
lastmod: "2026-11-12"
slug: "bug-in-lead-dbs-v2-5"
# the picture shown when the page is shared (head.html)
share: "images/renders/lead-closeup.jpg"
---

We found a serious bug in Lead-DBS that affects fMRI maps calculated from VTAs with normative
connectomes. It entered the development branch on
[16 October 2020](https://github.com/netstim/leaddbs/commit/d92b67f5d3ca123c724ff076936e915e46d1b520#diff-0c609fe1a8a9f31b570553c768cda921f922d45c72caff75ecb525344a4c9c7b)
and was released as [version 2.5 on 8 January 2021](https://github.com/netstim/leaddbs/releases/tag/v2.5).

Only analyses that combine all three of these are affected:

1. the Lead Mapper tool;
2. normative fMRI connectomes (diffusion MRI is not affected);
3. seeding from VTAs (seeding from manually defined .nii files is not affected).

A fix went to the development branch on 16 July 2021, and version 2.5.3 with the fix was released on
30 July 2021. Do not use versions 2.5 to 2.5.2 with VTAs and normative functional connectomes.

Lead-DBS is research software without any warranty and is not intended for clinical use. Ideally,
technically experienced staff supervise its use, and every user understands the tools they use.

## What went wrong

- Seeding fMRI time series from a VTA means mapping the small, high-resolution VTA (about 0.2 mm) onto
  the voxels of the normative connectome (2 × 2 × 2 mm).
- Both are already in MNI space, so this step needs no co-registration, only a reslicing of the VTA to
  the lower resolution. From about 2017 this was done with SPM routines and worked.
- In very rare cases a VTA is smaller than an fMRI voxel. SPM's interpolation could then produce an
  empty NIfTI file and an error.
- To make this more robust, we plugged in a routine built for a similar process, but that routine
  included a co-registration step.
- In some cases this moved the VTAs in fMRI space, so they were mislocalized within the normative
  connectome and the results were wrong.
