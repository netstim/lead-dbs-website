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
sidebar: false
toc: false
# the rows under "Get help" (layouts/_shortcodes/link-rows.html)
help:
  - {name: "User Slack", icon: "slack", text: "Ask other users and the developers.", url: "/helpsupport/slack-user-channel/"}
  - {name: "Troubleshooting", icon: "book", text: "Known problems and their fixes, in the manual.", url: "https://netstim.gitbook.io/leaddbs/appendix/troubleshooting-specific-help"}
  - {name: "Bug reports", icon: "github", text: "On GitHub. Include your Lead-DBS version, your system and the full error message.", url: "https://github.com/netstim/leaddbs/issues"}
  - {name: "Contact", icon: "mail", text: "For everything else.", url: "/contact/"}
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - "/download/"
  - "/helpsupport/slack-user-channel/"
  - "/about/citing_leaddbs/"
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/events/", text: "Developer meetings and workshops"}
  - {page: "/develop/", text: "Code, atlases and bug reports"}
---

{{% hub-section %}}
## Learn {#learn}

**New to Lead-DBS?** Start with First steps, then practise on the Lead Tutor data.

{{< resource-index menu="docs" >}}
{{% /hub-section %}}

{{% hub-section %}}
## Manual {#manual}

**Every step of an analysis,** chapter by chapter, in the [manual](https://netstim.gitbook.io/leaddbs).

- [Installation](https://netstim.gitbook.io/leaddbs/installation)
- [One patient, step by step](https://netstim.gitbook.io/leaddbs/lead-dbs/step0-overview)
- [Registration and normalization](https://netstim.gitbook.io/leaddbs/lead-dbs/step3-volume-registrations)
- [Electrode reconstruction](https://netstim.gitbook.io/leaddbs/lead-dbs/step5-optional-reconstruction-of-electrode-trajectories)
- [Group analyses](https://netstim.gitbook.io/leaddbs/lead-group/group-analyses-with-lead-dbs)
- [Connectomics](https://netstim.gitbook.io/leaddbs/connectomics/connectomic-analyses)
{.manual-links}
{{% /hub-section %}}

{{% hub-section %}}
## Get help {#get-help}

**Stuck?** Ask in the user Slack, or report a bug.

{{< link-rows key="help" style="cells" >}}

The support forum is closed. Its old posts are not available on this site.
{.fine-print}
{{% /hub-section %}}
