---
title: "Lead-DBS 2.6 released"
# the browser title (head.html adds " – Lead-DBS")
htmlTitle: "Version 2.6 released"
description: "Lead-DBS 2.6, the last release before the move to BIDS: fixes under the hood, many more electrode models and six new atlases."
date: 2022-02-24
slug: "lead-dbs-v2-6-out-now"
# the picture shown when the page is shared (head.html)
share: "images/renders/lead-closeup.jpg"
---

Lead-DBS 2.6 is the last "classic" release before version 3, which moves projects to the BIDS format.
It has few new features but runs more stably and conveniently: 306 commits since version 2.5.3.

## Many more electrodes

Lead-DBS supports most electrode models, among them new directional designs with 16 contacts and several
sEEG electrodes. Johannes Achtzehn shows them in a [video](https://www.youtube.com/watch?v=winHo7_qmJI).
Missing a model? [Tell us](/helpsupport/#get-help).

## New atlases

Thanks to the colleagues who contributed them:

- [Dystonia response tract atlas](/helpsupport/knowledge-base/atlasesresources/atlases-2/#dystonia-response-tract-atlas-horn-2022) (Horn 2022): pathways linked to optimal outcome in 80 patients with generalized and cervical dystonia
- [Essential tremor hypointensity](/helpsupport/knowledge-base/atlasesresources/atlases-2/#essential-tremor-hypointensity-neudorfer-2022) (Neudorfer 2022): a hypointensity on FGATIR images that coincides with an optimal target for essential tremor, with sweet and sour spots
- Cognitive decline network (Reich 2022): a functional network linked to cognitive decline after STN-DBS in 44 patients with Parkinson's disease
- [Essential tremor probabilistic mapping](/helpsupport/knowledge-base/atlasesresources/atlases-2/#essential-tremor-probabilistic-mapping-nowacki-2022) (Nowacki 2022): sweet spots from 119 patients in five European centres
- [Levinson-Bari Limbic Brainstem Atlas](/helpsupport/knowledge-base/atlasesresources/atlases-2/#levinson-bari-limbic-brainstem-atlas-levinson-2022): five brainstem nuclei involved in limbic processing
- [HybraPD atlas](/helpsupport/knowledge-base/atlasesresources/atlases-2/#hybrapd-atlas-yu-2021) (Yu 2021): 12 subcortical nuclei related to Parkinson's disease, from QSM and T1-weighted MRI

{{< button href="/download/" >}}Download Lead-DBS{{< /button >}}

All changes since 2.5.3 are in the [list of changes on GitHub](https://github.com/netstim/leaddbs/compare/v2.5.3...v2.6).
What came next: [Lead-DBS 3.0](/lead-dbs-3-0-out-now/).
