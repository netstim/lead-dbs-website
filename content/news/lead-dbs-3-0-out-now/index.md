---
title: "Lead-DBS 3.0 released"
description: "Lead-DBS 3.0: projects stored in the BIDS format, three explorers to map DBS effects, WarpDrive, OSS-DBS pathway activation and six new atlases."
date: "2023-10-27T13:59:14"
lastmod: "2026-11-11"
slug: "lead-dbs-3-0-out-now"
# the picture shown when the page is shared (head.html)
share: "images/renders/lead-closeup.jpg"
---

Lead-DBS 3.0 is the largest update to the toolbox yet, the work of more than two years. It stores
projects in a new format based on the BIDS standard and brings three explorers to map DBS effects,
WarpDrive, pathway activation modelling with OSS-DBS and six new atlases. The paper on this version:
[Neudorfer et al. 2023](https://doi.org/10.1016/j.neuroimage.2023.119862).

## Projects in the BIDS format

Version 3 keeps its data in a new format based on the BIDS standard. Projects from version 2 open
after converting them to BIDS, with the import tool that comes with Lead-DBS. Before you switch:

- finish projects in version 2 that are close to completion;
- back up your data in the old format;
- get to know the new format with the manual's [overview](/manual/lead-dbs/step0-overview/)
  and the [BIDS walkthrough video](https://www.youtube.com/watch?v=nvZ-PnVpnDg).

## Three explorers to map DBS effects

The DBS sweetspot, fibre filtering and network mapping explorers, first introduced in
[version 2.5](/lead-dbs-v2-5-out-now/), have grown much further and are the methodological centrepiece
of version 3. What each one does is under [Methods](/helpsupport/knowledge-base/lead-dbs-methods/).

## WarpDrive

Simón Oxenford's WarpDrive is now officially released. With it you refine normalization warp fields by
hand, to bring patient images into standard space more precisely and to segment patient anatomy in
native space more accurately.

## Pathway activation with OSS-DBS

The interface to [OSS-DBS](https://doi.org/10.1371/journal.pcbi.1008023) (Butenko et al. 2020) is
officially released: advanced bioelectrical modelling, such as pathway activation, with open-source
tools. Konstantin Butenko built it together with Ningfei Li. OSS-DBS v2 followed in
[Lead-DBS 3.1](/lead-dbs-3-1-out-now/).

## New atlases

Thanks to the colleagues who contributed them:

- [Allen Human Reference Atlas](/helpsupport/knowledge-base/atlasesresources/atlases-2/#the-allen-human-reference-atlas-ding-2020) (Ding 2020)
- Alzheimer Response Network (Rios 2022)
- [Essential tremor probabilistic mapping](/helpsupport/knowledge-base/atlasesresources/atlases-2/#essential-tremor-probabilistic-mapping-nowacki-2022) (Nowacki 2022)
- PD Depression Network (Irmen 2020)
- Probabilistic Thalamus Atlas (Iglesias 2018)
- HCPex (Huang 2021)

<details class="more">
<summary>Who made version 3</summary>

- Ningfei Li, for overseeing the development and keeping the binaries working on all three operating systems
- Nanditha Rajamani, for complex features including multitract fibre filtering and advanced stimulation detection
- Konstantin Butenko, for OSS-DBS and many code contributions beyond it
- Simón Oxenford, for WarpDrive, Lead-OR and many other tools
- Garance Meyer, for PCA-based fibre filtering and a great deal of beta testing
- Johannes Achtzehn, for the DICOM import tool
- Clemens Neudorfer, for writing the Lead-DBS v3 paper
- Enrico Opri, for discussions, bug fixes and code
- Till Dembek, for help and code in the DBS Sweetspot Explorer
- Lauren Hart, for testing the BIDS import tool, among many others
- Barbara Hollunder, Helen Friedrich and Lukas Goede, for testing
- Helen Friedrich, Barbara Hollunder and Ningfei Li, for the new logo
- Aysu Sahin, Patricia Zvárova, Kavisha Fernando and Khoa Nguyen, for updating the manual
- Greydon Gilmore and Jonathan Lau, for advice before the move to BIDS
- Julian Neumann and Jonathan Vanhoecke, for their spirit during the move to BIDS
- Johannes Achtzehn and Nanditha Rajamani, the main drivers of the move to BIDS
- Michael Loftus, for code and beta testing
- Andreas Husch and Mehri Baniasadi, for including FastField and DBSegment
- Ningfei Li, Simón Oxenford, Konstantin Butenko and Nanditha Rajamani, for the conda environment inside Lead-DBS
- Bassam Al-Fatly, Matteo Vissani and the Richardson Lab, Melissa Chua and Jordy Tasserie, for testing, bug reports and support
- and the many colleagues who contributed data and atlases

</details>

{{< button href="/download/" >}}Download Lead-DBS{{< /button >}}

All changes since 2.6 are in the [list of changes on GitHub](https://github.com/netstim/leaddbs/compare/v2.6...v3.0).
