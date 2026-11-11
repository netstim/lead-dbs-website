---
title: "Learn Lead-DBS yourself"
date: "2025-02-28T17:20:40"
lastmod: "2025-02-28T17:20:41"
---

## Lead Tutor {#learn-lead-dbs-yourself}

{{% row %}}
{{% col "1/2" %}}
Lead Tutor lets you practise electrode localization with Lead-DBS on your own. It includes

- A [scientific paper](https://apertureneuro.org/article/129658-lead-tutor-an-open-access-educational-resource-for-deep-brain-stimulation-electrode-localizations) summarizing the effort
- A [dataset](https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c) of anonymized imaging data from ten DBS patients
- A tool (integrated into Lead-DBS) that you can use to check your results against those of experts

{{% /col %}}
{{% col "1/2" %}}
![First page of the Lead-Tutor paper in Aperture Neuro](Screenshot-2025-02-28-at-11.14.43-AM.png)

{{% /col %}}
{{% /row %}}

{{% row %}}
{{% col "1/4" %}}
{{< button href="https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c" >}}Download the Tutor Dataset{{< /button >}}

{{% /col %}}
{{% col "1/4" %}}
{{< button href="https://apertureneuro.org/article/129658-lead-tutor-an-open-access-educational-resource-for-deep-brain-stimulation-electrode-localizations" >}}Check out the Paper{{< /button >}}

{{% /col %}}
{{% col "1/2" %}}
![Lead Tutor report comparing a user's localizations with those of experts, per patient](Screenshot-2025-02-28-at-11.18.44-AM-1030x1005.png)  

**Example of Lead Tutor feedback.** A screenshot from the Lead Tutor interface, displaying user localization results for each patient. The interface visualizes the Euclidean and rotational distances of electrode placements compared to expert benchmarks. The results are color-coded based on standard deviations, which are calculated from the performance of non-experts relative to experts for each patient. This feedback helps users identify whether their localizations fall within or outside the optimal range, guiding improvements in their accuracy and consistency.

{{% /col %}}
{{% /row %}}

How to load the dataset and submit your results is explained in the manual: [Self-tutoring with Lead Tutor](https://netstim.gitbook.io/leaddbs/lead-dbs/self-tutoring-with-lead-tutor). New to Lead-DBS altogether? Start with the [installation guide](https://netstim.gitbook.io/leaddbs/installation) and the [walkthrough videos](/helpsupport/knowledge-base/walkthrough-videos/).
