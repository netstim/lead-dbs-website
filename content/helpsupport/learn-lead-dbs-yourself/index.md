---
title: "Practice dataset (Lead Tutor)"
description: "Ten DBS patients with expert electrode localizations, free to practise on."
weight: 1
linkTitle: "Practice dataset (Lead Tutor)"
date: "2025-02-28T17:20:40"
lastmod: "2026-11-12"
keywords: ["Lead Tutor", "Lead-Tutor", "tutorial", "training", "training dataset", "practise", "practice", "dataset", "exercise", "OSF", "ground truth", "expert localizations"]
# the picture shown when the page is shared (head.html)
share: "Screenshot-2025-02-28-at-11.18.44-AM-1030x1005.png"
# "Related" at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/helpsupport/knowledge-base/walkthrough-videos/"}
  - {page: "/helpsupport/knowledge-base/lead-dbs-methods/"}
# the dataset at a glance (layouts/_shortcodes/cells.html; text: Markdown)
glance:
  - {label: "Patients", value: "10 with bilateral electrodes", text: "Eight with Parkinson's disease, one with dystonia, one with epilepsy."}
  - {label: "Imaging", value: "MRI and CT", text: "Preoperative T1, T2 and in some FLAIR; postoperative CT. Defaced, as NIfTI in BIDS."}
  - {label: "Electrodes", value: "Directional in nine", text: "Boston Scientific Vercise Cartesia (6), Medtronic SenSight (2) and 3387 (1), Abbott Infinity (1)."}
  - {label: "Benchmark", value: "Two experts", text: "Localizations from ten trained non-experts provide a comparison range."}
layout: "showcase"
---

<span id="learn-lead-dbs-yourself"></span>

**Practise on imaging data from ten patients,** then compare your electrode localizations with those of two experts.
{.dataset-intro}

<div class="resource-actions">

{{< button href="https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c" variant="primary" external="true" >}}Download the dataset{{< /button >}}

<a class="link link--ext" href="{{< relref "/manual/lead-dbs/self-tutoring-with-lead-tutor/" >}}">Guide in the manual </a>

</div>

{{< cells key="glance" label="Lead Tutor at a glance" >}}

{{% hub-section %}}
## Your report {#your-report}

**The report shows** positional and rotational differences from expert localizations for each patient, ordered from easy to hard.

<div class="report-shot">

![Lead Tutor report comparing a user's localizations with those of experts, per patient](Screenshot-2025-02-28-at-11.18.44-AM-1030x1005.png)

</div>

The colours show the range of non-expert localizations relative to the expert results.
{.fine-print}
{{% /hub-section %}}

{{% hub-section %}}
## The dataset {#dataset}

**Open data,** free to download from OSF.

Shared openly with the approval of the institutional review board of Brigham and Women's Hospital, Boston,
where the images were acquired.
{{% /hub-section %}}

{{% hub-section %}}
## What to cite {#what-to-cite}

**Madan et al. 2025,** Aperture Neuro.

<div class="cite-row">
<div class="cite-row__paper">

[![First page of the Lead-Tutor paper in Aperture Neuro](Screenshot-2025-02-28-at-11.14.43-AM.png)](https://doi.org/10.52294/001c.129658)

</div>
<div class="cite-row__text">

{{% copybox label="Copy the citation" %}}
{{< paper madan2025 "full" >}}
{{% /copybox %}}

</div>
</div>
{{% /hub-section %}}
