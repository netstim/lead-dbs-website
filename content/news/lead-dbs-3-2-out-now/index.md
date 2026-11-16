---
title: "Lead-DBS 3.2 released"
description: "Lead-DBS 3.2 brings Lead Tutor, an open dataset to practise electrode localization, new atlases and many smaller fixes."
date: 2025-02-28
slug: "lead-dbs-3-2-out-now"
image: "lead-tutor.png"
image_alt: "Title of the Lead Tutor paper in Aperture Neuro, over electrodes on a brain section"
---

Lead-DBS 3.2, released by Ningfei Li, adds [Lead Tutor](/manual/lead-dbs/self-tutoring-with-lead-tutor/) for practising electrode localization, new atlases and fixes.

{{< button href="/download/" >}}Download Lead-DBS{{< /button >}}

## Lead Tutor: learn electrode localizations yourself

Lead Tutor is the first training dataset for Lead-DBS and includes a tool to compare your localizations with expert results. We thank the team behind it, especially Lauren Hart and Savir Madan, for making the dataset openly available.

Download the dataset, localize the electrodes and select “Submit Results” to compare your localizations with expert results.

![Localizing a Lead Tutor dataset](lead-tutor-localize.png "Localizing a Lead Tutor dataset.")

![Results of user localizations compared to expert users, a report created automatically by Lead Tutor](lead-tutor-report.png "Results of user localizations compared to expert users, a report created automatically by Lead Tutor.")

{{% row %}}
{{% col "1/3" %}}
{{< button href="https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c" >}}Download Lead Tutor{{< /button >}}
{{% /col %}}
{{% col "1/3" %}}
{{< button href="https://apertureneuro.org/article/129658-lead-tutor-an-open-access-educational-resource-for-deep-brain-stimulation-electrode-localizations" >}}Read the Lead Tutor paper{{< /button >}}
{{% /col %}}
{{% col "1/3" %}}
{{< button href="/helpsupport/learn-lead-dbs-yourself/" >}}Lead Tutor{{< /button >}}
{{% /col %}}
{{% /row %}}

## New atlases

New atlas resources in v3.2:

- [Morel Atlas](https://zenodo.org/records/13918589) (Jakab 2008)
- The THOMAS Atlas was updated ([Saranathan 2021](https://www.nature.com/articles/s41597-021-01062-y))
- PD non-motor tracts (Meyer, in prep)
- Von Economo–Koskinas Brain Atlas ([Scholtens 2018](https://pubmed.ncbi.nlm.nih.gov/28040542/))

![Morel atlas](morel-atlas.jpeg)

The Morel atlas used to be available to users who completed a data sharing agreement. [Its authors have made the atlas openly available](https://zenodo.org/records/13918589). We would like to thank Dr. Andras Jakab for reaching out to let us know that we can integrate it into Lead-DBS.

## Institute for Network Stimulation in Cologne

Andreas Horn is founding a new Institute for Network Stimulation at the University Hospital Cologne this coming May. More details have been posted [on Bluesky](https://bsky.app/profile/andreashorn.org/post/3lidmydib722q).

Neuromodulation is one of the research focus areas of the University Hospital Cologne, which offers extensive stereotactic capabilities through the Stereotaxy Department of Dr. Veerle Visser-Vandewalle and provides deep brain stimulation for both neurological and psychiatric indications.

All changes since 3.1 are in the [full list of changes on GitHub](https://github.com/netstim/leaddbs/compare/v3.1...v3.2).

Read the original announcement [in our newsletter](https://www.lead-dbs.org/?na=view&id=31).
