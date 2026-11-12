---
title: "Docs and help"
description: "The Lead-DBS documentation and where to get help: first steps, the manual, Lead Tutor, walkthrough videos, the user Slack and bug reports."
linkTitle: "Docs and help"
date: "2017-01-04T21:27:30"
lastmod: "2026-11-12"
weight: 1
aliases: ["/helpsupport/knowledge-base/"]
keywords: ["help", "support", "documentation", "docs", "manual", "faq", "tutorial", "tutorials", "learn", "getting started", "question", "forum", "contact"]
# the picture shown when the page is shared (head.html)
share: "images/renders/head-about.jpg"
# a hub page: its sections use the full width, no sidebar
# the rows of each section (layouts/_shortcodes/link-rows.html); "Learn" leaves out the manual, which has its own section
learn:
  - {name: "First steps", text: "Installation and electrode localization", url: "/helpsupport/first-steps/"}
  - {name: "Lead Tutor", text: "10 patients with expert localizations", url: "/helpsupport/learn-lead-dbs-yourself/"}
  - {name: "Walkthrough videos", text: "Tutorials and recorded workshops", url: "/helpsupport/knowledge-base/walkthrough-videos/"}
manual:
  - {name: "Installation", url: "https://netstim.gitbook.io/leaddbs/installation"}
  - {name: "One patient, step by step", url: "https://netstim.gitbook.io/leaddbs/lead-dbs/step0-overview"}
  - {name: "Registration and normalization", url: "https://netstim.gitbook.io/leaddbs/lead-dbs/step3-volume-registrations"}
  - {name: "Electrode reconstruction", url: "https://netstim.gitbook.io/leaddbs/lead-dbs/step5-optional-reconstruction-of-electrode-trajectories"}
  - {name: "Group analyses", url: "https://netstim.gitbook.io/leaddbs/lead-group/group-analyses-with-lead-dbs"}
  - {name: "Connectomics", url: "https://netstim.gitbook.io/leaddbs/connectomics/connectomic-analyses"}
help:
  - {name: "User Slack", text: "Ask other users and the developers", url: "/helpsupport/slack-user-channel/"}
  - {name: "Troubleshooting", text: "Known problems and their fixes", url: "https://netstim.gitbook.io/leaddbs/appendix/troubleshooting-specific-help"}
  - {name: "Bug reports", text: "Include your Lead-DBS version, operating system and full error message", url: "https://github.com/netstim/leaddbs/issues"}
  - {name: "Contact", text: "For everything else", url: "/contact/"}
# "Related" at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/events/"}
  - {page: "/develop/"}
layout: "hub"
---

{{% hub-section %}}
## Learn {#learn}

**New to Lead-DBS?** Start with First steps, then practise on the Lead Tutor data.

{{< link-rows key="learn" >}}
{{% /hub-section %}}

{{% hub-section %}}
## Manual {#manual}

**The [manual](https://netstim.gitbook.io/leaddbs)** covers installation and analysis workflows.

{{< link-rows key="manual" >}}
{{% /hub-section %}}

{{% hub-section %}}
## Get help {#get-help}

**Stuck?** Ask in the user Slack, or report a bug.

{{< link-rows key="help" >}}
{{% /hub-section %}}
