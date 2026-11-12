---
title: "First steps"
linkTitle: "First steps"
description: "From download to your first electrode localization: install Lead-DBS, practise on the open Lead Tutor dataset, and fix common errors."
date: "2026-11-11"
weight: 1
keywords: ["getting started", "first steps", "install", "installation", "tutorial", "quick start", "documentation", "docs", "troubleshooting", "error", "errors", "problem", "not working", "FAQ", "frequently asked questions", "ea_restoreprefs", "ea_setpath", "Lead Tutor dataset", "exercise"]
# the picture shown when the page is shared (head.html)
share: "images/renders/insertion-final.png"
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - {name: "Install Lead-DBS", url: "/download/#install"}
  - "/helpsupport/knowledge-base/lead-dbs-methods/"
  - "/helpsupport/slack-user-channel/"
# found by the site search as a result of its own (layouts/home.searchindex.json)
searchEntries:
  - {title: "Troubleshooting: if something goes wrong", id: "troubleshooting", keywords: "troubleshooting FAQ frequently asked questions error errors problem not working ea_restoreprefs ea_setpath unrecognized function", description: "Errors after an update, unrecognized functions, and where to ask when you are stuck."}
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {url: "https://netstim.gitbook.io/leaddbs", name: "Manual", text: "Each step of a full analysis"}
  - {page: "/helpsupport/knowledge-base/walkthrough-videos/", text: "The steps on screen"}
  - {page: "/about/citing_leaddbs/", text: "Before you publish"}
---

Install Lead-DBS, then localize the electrodes of the open Lead Tutor patients and let Lead Tutor score
your result against experts. The [manual](https://netstim.gitbook.io/leaddbs) has the details of each step.

## Download and install Lead-DBS {#install .step}

[Download Lead-DBS](/download/) (about 11 GB) and follow the
[install steps on the download page](/download/#install). You need MATLAB {{< release matlab >}} or later
with SPM12; everything else is listed under [What you need](/download/#what-you-need). No MATLAB? The
[standalone builds](/download/#standalone-version) run without it.

## Localize your first electrodes with Lead Tutor {#lead-tutor .step}

[Lead Tutor](/helpsupport/learn-lead-dbs-yourself/) is an open dataset of ten DBS patients whose
electrodes experts have localized.

{{< button href="https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c" >}}Download the Lead Tutor dataset{{< /button >}}

1. Load the dataset in Lead-DBS and localize the electrodes of each patient.
2. Press *Submit Results…* (top right in Lead-DBS): Lead Tutor compares your localizations with the
   experts' and shows how close you came. Repeat as often as you like.

The manual walks through it in [Self-tutoring with Lead Tutor](https://netstim.gitbook.io/leaddbs/lead-dbs/self-tutoring-with-lead-tutor).

## If something goes wrong {#troubleshooting .step}

- After updating from an older version, errors can come from old settings: run `ea_restoreprefs(1,1)`
  in the MATLAB Command Window and try again.
- *Unrecognized function or variable*: run `ea_setpath` to add all Lead-DBS folders to the search path.
- Still stuck? [Join the user Slack](https://inviter.co/lead-dbs) and ask there; report bugs on
  [GitHub](https://github.com/netstim/leaddbs/issues).
