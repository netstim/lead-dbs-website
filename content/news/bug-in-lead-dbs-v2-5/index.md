---
title: "Bug in Lead-DBS 2.5"
description: "A bug in Lead-DBS 2.5 to 2.5.2 affected fMRI maps seeded from VTAs with normative functional connectomes. Version 2.5.3 fixes it."
date: "2021-07-16T13:58:53"
lastmod: "2021-07-30T15:24:53"
slug: "bug-in-lead-dbs-v2-5"
# the picture shown when the page is shared (head.html)
share: "images/renders/lead-closeup.jpg"
---

{{% row %}}
{{% col "1/5" %}}

{{% /col %}}
{{% col "4/5" %}}
**Bug in Lead-DBS v2.5**

Unfortunately, we discovered a serious bug in Lead-DBS that would affect calculating fMRI maps using normative connectomes from VTAs in Lead-DBS.

The bug was introduced to the development branch of Lead-DBS on [October 16 2020](https://github.com/netstim/leaddbs/commit/d92b67f5d3ca123c724ff076936e915e46d1b520#diff-0c609fe1a8a9f31b570553c768cda921f922d45c72caff75ecb525344a4c9c7b) and released on the website as [version 2.5 on January 8th 2021](https://github.com/netstim/leaddbs/releases/tag/v2.5).

Again, only analyses that combined the following three conditions are affected:

1. Use of the Lead Mapper tool
2. Normative fMRI connectomes (diffusion MRI is not affected)
3. Seeding from VTAs (seeding from manually defined .nii files is not affected)

A quick fix was pushed to develop on 16th July. A release (v2.5.3) with a bugfix has been pushed to servers on 07/30/2021.

Please do not use Lead-DBS versions 2.5-2.5.2 anymore going forward (at least not when using VTAs and normative functional connectomes).

{{% /col %}}
{{% /row %}}
---

**We would like to use the opportunity again to emphasize that**

- Lead-DBS is research software that unfortunately can come with bugs and comes without any warranty or guarantee whatsoever. It is not intended for clinical use.
- Optimally, tech-savvy personell should supervise the use of the software and as a user, you should fully understand the tools you use, optimally get engaged with the development process, yourself.
- Only with input from expert users will we be able to make the pipeline robust to the many use-cases that it is used for.

---

For people further interested, an attempt to explain **what went wrong?**

- To seed time series from fMRI data (in normative connectomes currently implemented in 2x2x2 mm voxels) from VTAs (which are often represented by nifti files with a very small field of view but a high resolution of ~0.2 mm in Lead-DBS), we need to map the small high res VTAs to the corresponding time series of the fMRI data.
- Since everything is already precisely in MNI space, no co-registration needs to happen at this step, but a reslicing of VTA files to the low-res space.
- This was implemented using SPM routines from ~2017 forward and all was fine.
- In very very rare cases, VTAs are smaller than an fMRI voxel and this could lead to interpolation problems using SPM, sometimes resulted in empty nifti files which produced errors.
- In an attempt to solve this, our team plugged in a routine developed to make a similar process more robust, but unfortunately that routine included a co-registration step.
- In some cases, this led to the VTAs to move in fMRI space, i.e. to mislocalise them within the normative connectome. This would then lead to nonsensical results, unfortunately.
