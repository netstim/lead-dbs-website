---
title: "Practice dataset (Lead Tutor)"
description: "The open training dataset of ten DBS patients with expert electrode localizations: what it holds, how to get it and what to cite."
weight: 1
linkTitle: "Practice dataset (Lead Tutor)"
date: "2025-02-28T17:20:40"
lastmod: "2026-11-12"
keywords: ["Lead Tutor", "Lead-Tutor", "tutorial", "training", "training dataset", "practise", "practice", "dataset", "exercise", "OSF", "ground truth", "expert localizations"]
# the four numbers under the intro (layouts/_shortcodes/facts.html, style="stats"): title is the number
stats:
  - {title: "10", text: "patients, both sides implanted"}
  - {title: "9", text: "with directional leads"}
  - {title: "2", text: "expert localizations each"}
  - {title: "10", text: "non-experts for the usual range"}
# the picture shown when the page is shared (head.html)
share: "Screenshot-2025-02-28-at-11.18.44-AM-1030x1005.png"
# a showcase page: its sections use the full width, no sidebar and no table of contents
sidebar: false
toc: false
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

**Practise on ten real patients.** Localize their electrodes in Lead-DBS, then see how close you came to the experts.
{.dataset-intro}

{{< facts key="stats" style="stats" label="Lead Tutor in numbers" >}}

<div class="resource-actions">

{{< button href="https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c" variant="primary" external="true" >}}Download the dataset{{< /button >}}

<a class="link link--ext" href="https://netstim.gitbook.io/leaddbs/lead-dbs/self-tutoring-with-lead-tutor">Guide in the manual <span class="ext-mark" aria-hidden="true">↗</span></a>

</div>

<ol class="how-tiles" aria-label="How it works">
<li><b>Download</b><span>The dataset from OSF: defaced MRI and CT, in BIDS.</span></li>
<li><b>Localize</b><span>Each patient’s electrodes in Lead-DBS, as you would your own.</span></li>
<li><b>Submit</b><span>Press <em>Submit Results…</em> and get your report.</span></li>
</ol>

{{% hub-section %}}
## Your report {#your-report}

**How close you came:** distance and rotation from the experts, patient by patient, from easy to hard.

<div class="report-shot">

![Lead Tutor report comparing a user's localizations with those of experts, per patient](Screenshot-2025-02-28-at-11.18.44-AM-1030x1005.png)

</div>

The colours show the usual range of non-experts.
{.fine-print}
{{% /hub-section %}}

{{% hub-section %}}
## The dataset {#dataset}

**Open data,** free to download from OSF.

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
{{% /hub-section %}}

{{% hub-section %}}
## What to cite {#what-to-cite}

**Used Lead Tutor?** Cite its paper.

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
