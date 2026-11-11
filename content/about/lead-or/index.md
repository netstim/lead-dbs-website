---
title: "Lead-OR"
description: "Lead-OR, the 3D Slicer extension for research in the operating theatre during DBS surgery."
date: "2023-07-07T18:58:13"
lastmod: "2026-11-11"
weight: 4
# the old site's page on 3D Slicer, which Lead-OR extends
aliases: ["/portfolio-item/3d-slicer/"]
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - {name: "Lead-OR figures", url: "/gallery/#fig-oxenford2022_fig1"}
  - "/about/publications/"
  - "/helpsupport/slack-user-channel/"
# the picture shown when the page is shared (head.html)
share: "gallery/oxenford2022_fig1.jpg"
---

Lead-OR brings Lead-DBS into the operating theatre. It is a sister tool of Lead-DBS for research during
DBS surgery: building on the coregistrations and segmentations made in Lead-DBS, it shows invasive
recordings (local field potentials and microelectrode recordings) in real time and models the effect of
stimulation on fibre tracts. It runs in [3D Slicer](https://www.slicer.org/), as part of the
[SlicerNetstim](https://github.com/netstim/SlicerNetstim) extension. It was released as open source in
August 2021, with a [preprint on medRxiv](https://www.medrxiv.org/content/10.1101/2021.08.09.21261792v1);
the paper appeared in eLife in 2022.

{{< button href="https://netstim.gitbook.io/leaddbs/lead-or/imaging-setup" >}}Get started with Lead-OR{{< /button >}}

{{< button href="https://github.com/netstim/SlicerNetstim" >}}Lead-OR on GitHub{{< /button >}}

## What to cite

{{% paper oxenford2022 "full" %}}

## Videos

{{< youtube id="lDMc-4L1tTU" title="Lead-OR in action" >}}

{{< youtube id="COd2iOWoykI" title="Lead-OR walkthrough tutorial" >}}

## Next

To get started with Lead-DBS, see [First steps](/helpsupport/first-steps/). Figures from papers that used Lead-OR are marked in [Made with Lead-DBS](/gallery/); the other tools are under [Features](/helpsupport/knowledge-base/lead-dbs-methods/#tools).
