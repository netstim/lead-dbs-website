---
title: "Lead Tutor: practise on open data"
description: "An open training dataset of ten DBS patients: localize the electrodes yourself and compare your results with those of experts."
weight: 1
linkTitle: "Lead Tutor"
date: "2025-02-28T17:20:40"
lastmod: "2026-11-11"
keywords: ["tutorial", "training", "practise", "practice", "dataset", "exercise"]
# the picture shown when the page is shared (head.html)
share: "Screenshot-2025-02-28-at-11.18.44-AM-1030x1005.png"
---

<span id="learn-lead-dbs-yourself"></span>

Lead Tutor is the first open training dataset for DBS electrode localization, and the best first
exercise after installing Lead-DBS: localize the electrodes of ten DBS patients yourself, then let Lead
Tutor score your result against those of experts. New to Lead-DBS? Start with [First steps](/helpsupport/first-steps/).

{{% row %}}
{{% col "1/2" %}}
**What you get**

- A [dataset](https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c) of anonymized imaging data from ten DBS patients
- A tool, built into Lead-DBS, that checks your localizations against the experts'
- A [paper](https://apertureneuro.org/article/129658-lead-tutor-an-open-access-educational-resource-for-deep-brain-stimulation-electrode-localizations) describing it all

{{< button href="https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c" >}}Download the Lead Tutor dataset{{< /button >}}

{{% /col %}}
{{% col "1/2" %}}
![First page of the Lead-Tutor paper in Aperture Neuro](Screenshot-2025-02-28-at-11.14.43-AM.png)

{{% /col %}}
{{% /row %}}

## How it works

1. Download the dataset and load it in Lead-DBS.
2. Localize the electrodes.
3. Press *Submit Results…*: Lead Tutor shows, for each patient, how far your electrodes lie from the
   experts' in distance and rotation, colour-coded by how non-experts usually do.

![Lead Tutor report comparing a user's localizations with those of experts, per patient](Screenshot-2025-02-28-at-11.18.44-AM-1030x1005.png "Lead Tutor's feedback: the Euclidean and rotational distances of your electrode placements from the expert benchmark, per patient. Colours mark standard deviations, calculated from the performance of non-experts relative to experts, so you see whether a localization falls within or outside the optimal range.")

The manual explains each step: [Self-tutoring with Lead Tutor](https://netstim.gitbook.io/leaddbs/lead-dbs/self-tutoring-with-lead-tutor).

## What to cite

Madan, S., Hart, L. A., Li, N., Dembek, T. A., Butenko, K., Meyer, G. M., et al. (2025). Lead-Tutor: An
open-access educational resource for deep brain stimulation electrode localizations. *Aperture Neuro*.
[doi:10.52294/001c.129658](https://doi.org/10.52294/001c.129658)

## Next

The [walkthrough videos](/helpsupport/knowledge-base/walkthrough-videos/) show whole analyses on screen,
and [Methods](/helpsupport/knowledge-base/lead-dbs-methods/) lists everything Lead-DBS does, with the
manual chapter for each.
