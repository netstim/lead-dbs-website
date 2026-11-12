---
title: "Lead-OR"
description: "Lead-OR, the 3D Slicer extension for research during DBS surgery: recordings and test stimulation shown on the images in real time."
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
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/helpsupport/first-steps/", text: "Install Lead-DBS and prepare your first patient"}
  - {page: "/helpsupport/knowledge-base/lead-dbs-methods/#tools", name: "Tools and modules", text: "Lead Group, Lead Connectome, OSS-DBS, Lead Tutor"}
  - {page: "/gallery/", text: "Figures from papers, those made with Lead-OR marked"}
---

Lead-OR brings Lead-DBS into the operating theatre: a sister tool of Lead-DBS for research during DBS
surgery.

{{< summary >}}
What
: Invasive recordings (microelectrode recordings and local field potentials) shown on the patient's images in real time, and the effect of test stimulation on fibre tracts modelled

Runs in
: [3D Slicer](https://www.slicer.org/), as part of the SlicerNetstim extension, with the coregistrations and segmentations made in Lead-DBS

Get it
: Free and open source: [SlicerNetstim on GitHub](https://github.com/netstim/SlicerNetstim); setup in the manual ([imaging setup](https://netstim.gitbook.io/leaddbs/lead-or/imaging-setup))

Cite
: Oxenford et al. 2022, *eLife* 11: e72929, [doi:10.7554/eLife.72929](https://doi.org/10.7554/eLife.72929) ([full citation](#what-to-cite))
{{< /summary >}}

![A 3D scene of a patient's skull in the stereotactic frame during surgery, with the planned electrode paths leading to small target structures deep in the brain](gallery/oxenford2022_fig1.jpg "Lead-OR during surgery: the stereotactic frame, the planned trajectories and their targets. Figure 1 of Oxenford et al., eLife 2022 (CC BY 4.0).")

## Use it in 3D Slicer

Lead-OR runs in [3D Slicer](https://www.slicer.org/), as part of the
[SlicerNetstim](https://github.com/netstim/SlicerNetstim) extension. Prepare the patient's images in
Lead-DBS first; the manual's chapter on the imaging setup takes you from there.

{{< button href="https://netstim.gitbook.io/leaddbs/lead-or/imaging-setup" >}}Get started with Lead-OR{{< /button >}}

{{< button href="https://github.com/netstim/SlicerNetstim" >}}Lead-OR on GitHub{{< /button >}}

## What to cite

{{% copybox label="Copy the citation" %}}
{{< paper oxenford2022 "full" >}}
{{% /copybox %}}

Lead-OR was released as open source in August 2021, with a
[preprint on medRxiv](https://www.medrxiv.org/content/10.1101/2021.08.09.21261792v1); the paper appeared
in eLife in 2022.

## See it in action {#videos}

{{< youtube id="lDMc-4L1tTU" title="Lead-OR in action" >}}

{{< youtube id="COd2iOWoykI" title="Lead-OR walkthrough tutorial" >}}
