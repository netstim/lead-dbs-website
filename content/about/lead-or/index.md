---
title: "Lead-OR"
description: "Lead-OR supports research during DBS surgery in 3D Slicer, displaying recordings and modelling test stimulation on patient images in real time."
date: "2023-07-07T18:58:13"
lastmod: "2026-11-11"
weight: 4
# the old site's page on 3D Slicer, which Lead-OR extends
aliases: ["/portfolio-item/3d-slicer/"]
# the picture shown when the page is shared (head.html)
share: "gallery/oxenford2022_fig1.jpg"
# "Related" at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/helpsupport/first-steps/"}
  - {page: "/helpsupport/knowledge-base/lead-dbs-methods/#tools", name: "Tools and modules"}
  - {page: "/gallery/"}
# Lead-OR at a glance (layouts/_shortcodes/cells.html)
glance:
  - {label: "Runs in", value: "3D Slicer"}
  - {label: "Extension", value: "SlicerNetstim"}
  - {label: "Licence", value: "Open source"}
  - {label: "Released", value: "August 2021"}
layout: "showcase"
---

<div class="page-intro"><div class="page-intro__text">

**Lead-OR supports research** during DBS surgery.

</div>
<p class="page-intro__actions"><a class="btn btn--primary btn--ext" href="{{< relref "/manual/lead-or/imaging-setup/" >}}">Get started</a><a class="btn btn--secondary btn--ext" href="https://github.com/netstim/SlicerNetstim">SlicerNetstim on GitHub<span class="ext-mark" aria-hidden="true">↗</span><span class="sr-only"> (another site)</span></a></p>
</div>

{{< cells key="glance" label="Lead-OR at a glance" >}}

{{% hub-section %}}
## Recordings and stimulation modelling

Lead-OR shows invasive recordings (microelectrode recordings and local field potentials) on the patient's
images as they are made, and models the effect of test stimulation on fibre tracts.

![A 3D scene of a patient's skull in the stereotactic frame during surgery, with the planned electrode paths leading to small target structures deep in the brain](gallery/oxenford2022_fig1.jpg "The stereotactic frame, the planned trajectories and their targets. Figure 1 of Oxenford et al., eLife 2022 (CC BY 4.0).")
{{% /hub-section %}}

{{% hub-section %}}
## Imaging setup {#download}

**Prepare the images in Lead-DBS first.**

Lead-OR uses coregistrations and segmentations prepared in Lead-DBS. Follow the
[imaging setup](/manual/lead-or/imaging-setup/) instructions in the manual.
{{% /hub-section %}}

{{% hub-section %}}
## What to cite

**Oxenford et al. 2022,** eLife.

{{% copybox label="Copy the citation" %}}
{{< paper oxenford2022 "full" >}}
{{% /copybox %}}

The preprint is on [medRxiv](https://www.medrxiv.org/content/10.1101/2021.08.09.21261792v1).
{{% /hub-section %}}

## See it in action {#videos}

{{< youtube id="lDMc-4L1tTU" title="Lead-OR in action" >}}

{{< youtube id="COd2iOWoykI" title="Lead-OR walkthrough tutorial" >}}
