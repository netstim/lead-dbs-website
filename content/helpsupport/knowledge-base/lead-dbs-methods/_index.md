---
title: "Lead-DBS methods"
description: "What Lead-DBS does, step by step: electrode localization, normalization, stimulation modelling, group and network analyses, with manual and paper."
weight: 3
linkTitle: "Methods"
date: "2017-04-19T16:59:05"
lastmod: "2026-11-11"
keywords: ["methods", "features", "what it does", "electrode localization", "reconstruction", "normalization", "registration", "WarpDrive", "VTA", "volume of tissue activated", "electric field", "OSS-DBS", "sweet spot", "fibre filtering", "fiber filtering", "network mapping", "Lead Group", "group analysis"]
# the picture shown when the page is shared (head.html)
share: "images/renders/fiber-filtering-wide.jpg"
---

The [Lead-DBS v3 paper](https://doi.org/10.1016/j.neuroimage.2023.119862) (Neudorfer et al. 2023)
summarizes all of these methods.

## Single patients

| Method | What it does | Manual | Paper |
| --- | --- | --- | --- |
| Registration and normalization | Aligns pre- and postoperative images and warps them into MNI space (ICBM 2009b); WarpDrive refines the warp by hand | [Volume registrations](https://netstim.gitbook.io/leaddbs/lead-dbs/step3-volume-registrations) | [Ewert 2019](https://doi.org/10.1016/j.neuroimage.2018.09.061), [Oxenford 2024](https://doi.org/10.1016/j.media.2023.103041) |
| Electrode localization | Reconstructs the electrodes from postoperative MRI or CT, with algorithms such as TRAC/CORE and PaCER | [Reconstruction of electrode trajectories](https://netstim.gitbook.io/leaddbs/lead-dbs/step5-optional-reconstruction-of-electrode-trajectories) | [Horn & Kühn 2015](https://doi.org/10.1016/j.neuroimage.2014.12.002), [Husch 2018](https://doi.org/10.1016/j.nicl.2017.10.004) |
| Visualization | Shows electrodes in 2D and 3D with atlases, fibre tracts and stimulation volumes | [Visualization](https://netstim.gitbook.io/leaddbs/lead-dbs/step7-visualization) | [Horn & Kühn 2015](https://doi.org/10.1016/j.neuroimage.2014.12.002) |
| Stimulation modelling | Volume of tissue activated, electric field and pathway activation, with the integrated [OSS-DBS v2](/about/lead-dbs-dependencies/#stimulation-modelling-oss-dbs) | [Calculate VTA and stats](https://netstim.gitbook.io/leaddbs/lead-group/calculate-vta-and-stats) | [Butenko 2020](https://doi.org/10.1371/journal.pcbi.1008023), [Zimmermann 2026](https://doi.org/10.64898/2026.10.10.26365197) (preprint) |
| Connectivity | Structural and functional connectivity of a stimulation site, from normative or patient-specific connectomes ([Lead Connectome](/about/lead-connectome/)) | [Connectomics](https://netstim.gitbook.io/leaddbs/connectomics/connectomic-analyses) | [Horn & Blankenburg 2016](https://doi.org/10.1016/j.neuroimage.2015.08.048) |
| [AC/PC to MNI conversion](/helpsupport/knowledge-base/lead-dbs-methods/acpc-to-mni-conversion-2/) | Converts surgical AC/PC coordinates into MNI space and back | In the Tools menu (see the page) | [Horn 2017](https://doi.org/10.1016/j.neuroimage.2017.02.004) |
{.table--stack caption="Methods for single patients"}

## Groups of patients

| Method | What it does | Manual | Paper |
| --- | --- | --- | --- |
| Group analysis | Electrode placement across a cohort and its relation to clinical outcome, in Lead Group | [Group analyses](https://netstim.gitbook.io/leaddbs/lead-group/group-analyses-with-lead-dbs) | [Treu 2020](https://doi.org/10.1016/j.neuroimage.2020.117018) |
| Sweet-spot mapping | Maps hot and cold spots of outcome within the target region from the stimulation volumes | [Sweetspot Explorer](https://netstim.gitbook.io/leaddbs/lead-group/sweetspot-explorer) | [Neudorfer 2023](https://doi.org/10.1016/j.neuroimage.2023.119862) |
| [DBS network mapping](/helpsupport/knowledge-base/lead-dbs-methods/connectivity-benefit-mapping/) and fibre filtering | Relates the connections of stimulation sites, whole-brain maps or single fibre tracts, to clinical outcome | [Connectomics](https://netstim.gitbook.io/leaddbs/connectomics/connectomic-analyses) | [Horn 2017](https://doi.org/10.1002/ana.24974), [Neudorfer 2023](https://doi.org/10.1016/j.neuroimage.2023.119862) |
| [Subcortical electrophysiology mapping](/helpsupport/knowledge-base/lead-dbs-methods/subcortical-electrophysiology-mapping-sem/) | Pools recordings from DBS electrodes across patients into a 3D map | [Group analyses](https://netstim.gitbook.io/leaddbs/lead-group/group-analyses-with-lead-dbs) | [Horn 2017](https://doi.org/10.1002/hbm.23594) |
{.table--stack caption="Methods for groups of patients"}

## Beyond the desktop

| Tool | What it does | Manual | Paper |
| --- | --- | --- | --- |
| [Lead-OR](/about/lead-or/) | Electrode localization and recordings in the operating theatre, in 3D Slicer | [Lead-OR](https://netstim.gitbook.io/leaddbs/lead-or/imaging-setup) | [Oxenford 2022](https://doi.org/10.7554/eLife.72929) |
| [Lead Tutor](/helpsupport/learn-lead-dbs-yourself/) | Practise electrode localization on an open dataset, scored against experts | [Self-tutoring with Lead Tutor](https://netstim.gitbook.io/leaddbs/lead-dbs/self-tutoring-with-lead-tutor) | [Madan 2025](https://doi.org/10.52294/001c.129658) |
{.table--stack caption="Tools beyond the desktop"}

All methods papers, with full references, are listed under
[Publications](/about/publications/#methodological-publications); which ones to cite is on
[Cite Lead-DBS](/about/citing_leaddbs/). Background reading:
[how AC/PC targets were brought into MNI space](/helpsupport/knowledge-base/lead-dbs-methods/acpc-to-mni-conversion-2/#background)
and [About the MNI space(s)](/about-the-mni-spaces/).

## Next

New to Lead-DBS? Start with [First steps](/helpsupport/first-steps/). The atlases and connectomes these
methods use are listed under [Atlases and data](/helpsupport/knowledge-base/atlasesresources/).
