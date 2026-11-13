---
title: "First steps"
linkTitle: "First steps"
description: "From download to your first electrode localization: install Lead-DBS, practise on the open Lead Tutor dataset, and fix common errors."
date: "2026-11-11"
weight: 1
keywords: ["getting started", "first steps", "install", "installation", "tutorial", "quick start", "documentation", "docs", "troubleshooting", "error", "errors", "problem", "not working", "FAQ", "frequently asked questions", "ea_restoreprefs", "ea_setpath", "Lead Tutor dataset", "exercise"]
# the picture shown when the page is shared (head.html)
share: "images/renders/insertion-final.png"
# this page has its own template (layouts/first-steps.html): the text below as the opening line, then
# the steps in one frame, then the fixes
layout: "first-steps"
# the sections that template draws, for the search entries below (the build checks them against this list)
anchors: ["install", "lead-tutor", "compare", "troubleshooting"]
# The steps: a title, one or two sentences (Markdown) and up to two actions (page: a site path, or url:
# another site; the first is drawn as the button). show: the small picture of the step:
#   release   the current release as a file (data/release.yaml, the size from the download page)
#   dataset   the practice dataset as a file ("name", "facts")
#   report    a small drawing of the Lead Tutor report: distance from the experts, patient by patient
steps:
  - id: "install"
    title: "Install Lead-DBS"
    text: "You need MATLAB {matlab} or later with SPM12. The [standalone build](/download/#standalone-version) runs without MATLAB."
    show: release
    actions:
      - {text: "Download Lead-DBS", page: "/download/"}
      - {text: "Installation instructions", page: "/download/#install"}
  - id: "lead-tutor"
    title: "Get the practice data"
    text: "[Lead Tutor](/helpsupport/learn-lead-dbs-yourself/) is an open dataset of ten real patients, with their electrodes already localized by experts."
    show: dataset
    name: "Lead Tutor"
    facts: "10 patients · MRI and CT"
    actions:
      - {text: "Download Lead Tutor", url: "https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c"}
      - {text: "Guide", page: "/manual/lead-dbs/self-tutoring-with-lead-tutor/"}
  - id: "compare"
    title: "Localize, then get your report"
    text: "Localize each patient’s electrodes and press *Submit Results…* to receive a report of their distances from expert localizations."
    show: report
    actions:
      - {text: "See a report", page: "/helpsupport/learn-lead-dbs-yourself/#your-report"}
      - {text: "Walkthrough videos", page: "/helpsupport/knowledge-base/walkthrough-videos/"}
# If something goes wrong: the problem and the command to type in MATLAB
fixes:
  - {problem: "Errors after an update", command: "ea_restoreprefs(1,1)"}
  - {problem: "Unrecognized function or variable", command: "ea_setpath"}
# found by the site search as a result of its own (layouts/home.searchindex.json)
searchEntries:
  - {title: "Troubleshooting: if something goes wrong", id: "troubleshooting", keywords: "troubleshooting FAQ frequently asked questions error errors problem not working ea_restoreprefs ea_setpath unrecognized function", description: "Errors after an update, unrecognized functions, and where to ask when you are stuck."}
# "Related" at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/manual/", name: "Manual"}
  - {page: "/helpsupport/knowledge-base/lead-dbs-methods/"}
  - {page: "/about/citing_leaddbs/"}
---

