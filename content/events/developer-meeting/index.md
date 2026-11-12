---
title: "Lead-DBS Developer Meeting"
# its place in the Events list of the sidebar: in date order, as /events/ lists them
weight: 1
linkTitle: "Lead-DBS Developer Meeting"
description: "The Lead-DBS Developer Meeting: monthly on Zoom, open to anyone who wants to contribute or follow the development. How to register, and the flyer."
keywords: ["zoom", "register", "registration", "developer meeting", "flyer"]
# this page has its own template (layouts/event.html): a black head with the registration, the facts of
# the event (data/events.yaml, by its id), who it is for, and the flyer. The text below is the line
# under the title.
layout: "event"
event: "lead-dbs-developer-meeting-2026-11-18"
# the label of the date ("First meeting", "Next meeting")
label: "First meeting"
# three words under the title
tagline: ["Monthly", "Online on Zoom", "Open to anyone"]
host: {name: "Institute for Network Stimulation", url: "https://www.netstim.org/"}
# who it is for, a cell each (text: Markdown)
audience:
  - {value: "Contributors", text: "Of code and fixes, atlases or datasets, and those who would like to become one: [how to contribute](/develop/)."}
  - {value: "Users", text: "Who want to learn about the ongoing development of Lead-DBS."}
# the flyer: a file next to this page, what it shows, and a line about the file
flyer:
  file: "lead-dbs-developer-meeting-flyer.jpg"
  alt: "Flyer of the 1st Lead-DBS open developer meeting, 18 November 2026, 3:00 PM CET / 9:00 AM EST, with a QR code to the registration"
  text: "Share it with colleagues: its QR code leads to the same registration."
  format: "JPG, A4, 0.6 MB"
# the picture shown when the page is shared (head.html)
share: "lead-dbs-developer-meeting-flyer.jpg"
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - "/develop/"
  - "/helpsupport/slack-user-channel/"
  - "/about/team/"
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/develop/", text: "Source code, how to contribute, bug reports"}
  - {page: "/events/hands-on-workshop-2027/", text: "Two days in Cologne, February 2027"}
---

An open meeting about the ongoing development of Lead-DBS.
