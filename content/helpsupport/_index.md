---
title: "Docs"
description: "The Lead-DBS documentation and where to get help: first steps, the manual, Lead Tutor, walkthrough videos, the user Slack and bug reports."
linkTitle: "Docs"
date: "2017-01-04T21:27:30"
lastmod: "2026-11-12"
weight: 1
aliases: ["/helpsupport/knowledge-base/"]
keywords: ["help", "support", "documentation", "docs", "manual", "faq", "tutorial", "tutorials", "learn", "getting started", "question", "forum", "contact"]
# the picture shown when the page is shared (head.html)
share: "images/renders/head-about.jpg"
# a hub page: its sections use the full width, no sidebar
# the rows of each section (layouts/_shortcodes/link-rows.html); "Start here" leaves out the manual, which has its own section.
# A row's text only where it tells the rows apart (Lead Tutor's ten patients); a name that explains itself stands alone.
learn:
  - {name: "First steps", url: "/helpsupport/first-steps/"}
  - {name: "Lead Tutor", text: "10 patients with expert localizations", url: "/helpsupport/learn-lead-dbs-yourself/"}
  - {name: "Walkthrough videos", url: "/helpsupport/knowledge-base/walkthrough-videos/"}
manual:
  - {name: "Installation", url: "/manual/installation/"}
  - {name: "One patient, step by step", url: "/manual/lead-dbs/step0-overview/"}
  - {name: "Registration and normalization", url: "/manual/lead-dbs/step3-volume-registrations/"}
  - {name: "Electrode reconstruction", url: "/manual/lead-dbs/step5-optional-reconstruction-of-electrode-trajectories/"}
  - {name: "Group analyses", url: "/manual/lead-group/group-analyses-with-lead-dbs/"}
  - {name: "Connectomics", url: "/manual/connectomics/connectomic-analyses/"}
help:
  - {name: "User Slack", text: "Ask other users and the developers", url: "/helpsupport/slack-user-channel/"}
  - {name: "Troubleshooting", text: "Known problems and their fixes", url: "/manual/appendix/troubleshooting-specific-help/"}
  - {name: "Bug reports", text: "Include your Lead-DBS version, operating system and full error message", url: "https://github.com/netstim/leaddbs/issues"}
  - {name: "Contact", url: "/contact/"}
# "Related" at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/events/"}
  - {page: "/develop/"}
layout: "hub"
# the documentation entry opens with its title and the task, without the group's render
headRender: false
---

<div class="page-intro"><div class="page-intro__text">

Install Lead-DBS and follow your first analysis.

</div>
<p class="page-intro__actions"><a class="btn btn--primary" href="{{< relref "/manual/" >}}">Open the manual</a><a class="btn btn--secondary" href="{{< relref "/helpsupport/first-steps/" >}}">First steps</a></p>
</div>

{{% hub-section %}}
## Start here {#learn}

{{< link-rows key="learn" >}}
{{% /hub-section %}}

{{% hub-section %}}
## Manual {#manual}

{{< link-rows key="manual" >}}
{{% /hub-section %}}

{{% hub-section %}}
## Get help {#get-help}

{{< link-rows key="help" >}}
{{% /hub-section %}}
