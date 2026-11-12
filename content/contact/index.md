---
title: "Contact"
description: "How to reach the Lead-DBS team: questions, bug reports, and a contact form."
date: "2014-06-24T16:48:44"
lastmod: "2022-03-15T20:30:21"
weight: 10
keywords: ["contact", "email", "e-mail"]
# In the menu hierarchy the contact page is the last step of "Get help" (breadcrumb Docs and help / Contact).
menuParent: "/helpsupport"
# the page uses the full width: the faster ways on the left, the form on the right; no sidebar
sidebar: false
toc: false
# the faster ways, as cells (layouts/_shortcodes/link-rows.html)
faster:
  - {name: "User Slack", icon: "slack", text: "Questions about using Lead-DBS.", url: "/helpsupport/slack-user-channel/"}
  - {name: "Bug reports", icon: "github", text: "On GitHub, with your version and the error message.", url: "https://github.com/netstim/leaddbs/issues"}
  - {name: "Troubleshooting", icon: "book", text: "Known problems and their fixes, in the manual.", url: "https://netstim.gitbook.io/leaddbs/appendix/troubleshooting-specific-help"}
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - "/helpsupport/slack-user-channel/"
  - {name: "Report a bug on GitHub", url: "https://github.com/netstim/leaddbs/issues"}
  - "/helpsupport/first-steps/"
# the picture shown when the page is shared (head.html)
share: "images/renders/head-docs.jpg"
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/about/", text: "The team and the institute behind Lead-DBS"}
  - {page: "/subscribe-to-our-newsletter/", text: "Release and workshop news by e-mail"}
---

<div class="contact-split">
<div class="contact-split__ways">

**A question or a bug?** These are answered fastest where users and developers already are.
{.contact-lead}

{{< link-rows key="faster" style="cells" >}}

</div>
<div class="contact-split__form">

## Anything else {#form}

{{< form "contact" >}}

</div>
</div>
