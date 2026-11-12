---
title: "Practice dataset (Lead Tutor)"
description: "The open training dataset of ten DBS patients with expert electrode localizations: what it holds, how to get it and what to cite."
weight: 1
linkTitle: "Practice dataset (Lead Tutor)"
date: "2025-02-28T17:20:40"
lastmod: "2026-11-11"
keywords: ["Lead Tutor", "Lead-Tutor", "tutorial", "training", "training dataset", "practise", "practice", "dataset", "exercise", "OSF", "ground truth", "expert localizations"]
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

Lead Tutor is the first open training dataset for DBS electrode localization, with a tool built into
Lead-DBS that scores your localizations against those of experts. The exercise is step 2 of
[First steps](/helpsupport/first-steps/#lead-tutor).

{{< summary >}}
Patients
: Ten, implanted on both sides: eight with Parkinson's disease, one with dystonia, one with epilepsy

Imaging
: Preoperative MRI (T1- and T2-weighted, in some patients FLAIR) and postoperative CT, defaced and anonymized, as NIfTI files in BIDS

Electrodes
: Boston Scientific Vercise Cartesia (six patients), Medtronic SenSight (two) and 3387 (one), Abbott Infinity (one); directional in nine patients

Benchmark
: Localizations by two experts, and those of ten trained non-experts for the range of usual results

Get it
: Free download from OSF; shared openly with the approval of the institutional review board of Brigham and Women's Hospital, Boston, where the images were acquired

Cite
: Madan et al. 2025, *Aperture Neuro* 5, [doi:10.52294/001c.129658](https://doi.org/10.52294/001c.129658) ([full citation](#what-to-cite))
{{< /summary >}}

{{< button href="https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c" >}}Download the Lead Tutor dataset{{< /button >}}

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
