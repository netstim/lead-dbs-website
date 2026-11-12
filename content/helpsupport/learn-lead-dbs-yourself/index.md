---
title: "Practice dataset (Lead Tutor)"
description: "The open training dataset of ten DBS patients with expert electrode localizations: what it holds, how to get it and what to cite."
weight: 1
linkTitle: "Practice dataset (Lead Tutor)"
date: "2025-02-28T17:20:40"
lastmod: "2026-11-12"
keywords: ["Lead Tutor", "Lead-Tutor", "tutorial", "training", "training dataset", "practise", "practice", "dataset", "exercise", "OSF", "ground truth", "expert localizations"]
facts:
  - title: "10 patients"
    text: "Bilateral implants; directional leads in nine patients."
  - title: "MRI and CT"
    text: "Preoperative MRI and postoperative CT."
  - title: "Expert benchmark"
    text: "Two experts and ten trained non-experts."
  - title: "Anonymized data"
    text: "NIfTI files organized in BIDS format."
# the picture shown when the page is shared (head.html)
share: "Screenshot-2025-02-28-at-11.18.44-AM-1030x1005.png"
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - {name: "Install Lead-DBS", url: "/download/#install"}
  - "/helpsupport/knowledge-base/walkthrough-videos/"
  - "/events/"
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/helpsupport/knowledge-base/walkthrough-videos/", text: "Whole analyses on screen"}
  - {page: "/helpsupport/knowledge-base/lead-dbs-methods/", text: "Every method and tool, with its manual chapter"}
---

<span id="learn-lead-dbs-yourself"></span>

Practise electrode localization on ten patients, then compare your results with expert localizations in Lead-DBS. Start with [First steps](/helpsupport/first-steps/#lead-tutor).
{.dataset-intro}

{{< facts label="Lead Tutor at a glance" >}}

<div class="resource-actions">

{{< button href="https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c" variant="primary" external="true" >}}Download dataset{{< /button >}}

<a class="link link--ext" href="https://doi.org/10.52294/001c.129658">Read the paper <span class="ext-mark" aria-hidden="true">↗</span></a>

</div>

<details class="more dataset-details">
<summary>Dataset details</summary>

{{< summary >}}
Patients
: Ten, implanted on both sides: eight with Parkinson's disease, one with dystonia, one with epilepsy

Imaging
: Preoperative MRI (T1- and T2-weighted, in some patients FLAIR) and postoperative CT, defaced and anonymized, as NIfTI files in BIDS

Electrodes
: Boston Scientific Vercise Cartesia (six patients), Medtronic SenSight (two) and 3387 (one), Abbott Infinity (one); directional in nine patients

Benchmark
: Localizations by two experts, and those of ten trained non-experts for the range of usual results

Access
: Free download from OSF; shared openly with the approval of the institutional review board of Brigham and Women's Hospital, Boston, where the images were acquired

{{< /summary >}}

</details>

## Your report

After *Submit Results…*, Lead Tutor shows for each patient how far your electrodes lie from the experts'
in distance and rotation, colour-coded by how non-experts usually do. The patients are ordered from
easiest to hardest; a few were included on purpose because their images are hard to read.

![Lead Tutor report comparing a user's localizations with those of experts, per patient](Screenshot-2025-02-28-at-11.18.44-AM-1030x1005.png "Lead Tutor's feedback: the Euclidean and rotational distances of your electrode placements from the expert benchmark, per patient. Colours mark standard deviations, calculated from the performance of non-experts relative to experts, so you see whether a localization falls within or outside the optimal range.")

The manual explains each step: [Self-tutoring with Lead Tutor](https://netstim.gitbook.io/leaddbs/lead-dbs/self-tutoring-with-lead-tutor).

## What to cite

{{% copybox label="Copy the citation" %}}
{{< paper madan2025 "full" >}}
{{% /copybox %}}

![First page of the Lead-Tutor paper in Aperture Neuro](Screenshot-2025-02-28-at-11.14.43-AM.png)
