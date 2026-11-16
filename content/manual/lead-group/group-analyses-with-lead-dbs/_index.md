---
{
  "title": "Group analyses with Lead-DBS",
  "linkTitle": "About Lead Group",
  "layout": "manual",
  "manual_group": "lead-group",
  "description": "An introduction to cohort-level analysis with Lead Group.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-group/group-analyses-with-lead-dbs",
  "manual_lead": "An introduction to cohort-level analysis with Lead Group."
}
---

{{% manual-note "info" %}}
Lead Group is best documented by the [Lead-DBS v3.0 paper](https://www.biorxiv.org/content/10.1101/2020.01.14.904615v1) and the accompanying walkthrough tutorial found on [OSF](https://osf.io/kj456/).

An older resource is the set of [group analysis walkthrough slides](https://www.lead-dbs.org/docs/tutorials/group_analyses_horn.pdf).
{{% /manual-note %}}

Once the coregistration, normalization and reconstruction steps have been performed for a group of patients, you can load these in the group GUI, which you can start by entering the following into the MATLAB command line:

```matlab
lead group
```

From here, several options for visualization and analysis of clinical/multimodal data are available. The rest of this section explains how to [set up an analysis](/manual/lead-group/setup-analysis/), how to create [group visualizations](/manual/lead-group/group-visualization/) and how to [calculate VTA and stats](/manual/lead-group/calculate-vta-and-stats/).

{{% manual-note "info" %}}
Before starting, make sure to check the accuracy of both normalization and reconstruction for each patient you analyse.
{{% /manual-note %}}

![Lead Group GUI](manual/5a1c42d7c3ae4f1b.png "Lead Group GUI")
