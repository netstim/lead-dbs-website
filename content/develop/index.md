---
title: "Contribute"
date: "2026-11-10"
lastmod: "2026-11-11"
description: "Contribute to Lead-DBS: code and fixes, atlases and datasets, bug reports; the source code, its licence and the developer meeting."
keywords: ["contribute", "code", "github", "developer", "pull request", "bug", "changelog", "release notes", "source", "atlas", "dataset", "method", "inclusion", "data and code inclusion philosophy", "contribute an atlas"]
# this page has its own template (layouts/contribute.html): the text below as the opening line, then
# the three ways to contribute, the set-up for development, what an atlas needs, and the facts
layout: "contribute"
# the buttons under the opening line (page: a site path, url: another site; the first is the black pill)
actions:
  - {text: "Lead-DBS on GitHub", url: "https://github.com/netstim/leaddbs"}
  - {text: "Developer meeting", page: "/events/developer-meeting/"}
# The three ways: a title, a sentence (Markdown), up to two actions, and a small picture (show):
#   terminal  the lines of "lines" in a terminal
#   chips     the words of "chips" as pills
#   issue     the fields of "fields" as a bug report to fill in
ways:
  - id: "how-to-contribute"
    title: "Add your code"
    text: "Open a pull request on GitHub, or ask us for push access."
    show: terminal
    lines: ["git clone netstim/leaddbs", "git checkout develop"]
    actions:
      - {text: "Repository", url: "https://github.com/netstim/leaddbs"}
      - {text: "Set-up", page: "/develop/#setup"}
  - id: "add-your-atlas-or-dataset"
    title: "Add your atlas or dataset"
    text: "From MRI, histology, connectivity, drawings or synthesized maps. Published atlases are included so that the studies behind them can be reproduced."
    show: chips
    chips: ["MRI", "Histology", "Connectivity", "Drawings", "Synthesized maps"]
    actions:
      - {text: "Write to us", page: "/contact/"}
      - {text: "Who has contributed", page: "/about/team/#atlases-and-data-contributed-by"}
  - id: "report-a-bug"
    title: "Report a bug"
    text: "Open an issue on GitHub. Questions about using Lead-DBS are best asked on the [user Slack](/helpsupport/slack-user-channel/)."
    show: issue
    fields: ["Lead-DBS version", "Operating system", "Full error message"]
    actions:
      - {text: "Open an issue", url: "https://github.com/netstim/leaddbs/issues"}
# Working on the code: install Lead-DBS from GitHub instead of the download. A step is a line of text
# (Markdown) and either a command to copy or a link.
setup:
  - {text: "Check the requirements", link: {text: "What you need", page: "/download/#what-you-need"}}
  - {text: "Clone the repository", command: "git clone https://github.com/netstim/leaddbs.git"}
  - {text: "Switch to the develop branch", command: "git checkout develop"}
  - {text: "Download the data and unzip it into the repository", link: {text: "Download the data", url: "https://www.lead-dbs.org/release/download.php?id=data_pcloud"}}
  - {text: "Add SPM12 and Lead-DBS to the MATLAB path, then run", command: "ea_setpath"}
setup_note: "The manual's [installation via GitHub](https://netstim.gitbook.io/leaddbs/installation#installation-via-github) describes each step. A feature that would change what Lead-DBS is for can live in a fork. Where possible, the interface names the paper behind a feature, so that it can be cited: the AC/PC to MNI conversion, for instance, refers to [Horn et al. 2017, NeuroImage](https://www.ncbi.nlm.nih.gov/pubmed/28163141)."
# what an atlas or dataset needs, a cell each (text: Markdown)
atlas:
  - label: "Source"
    value: "Any source is welcome"
    text: "Atlases from MRI, histology, connectivity, drawings or synthesized maps, and datasets that help DBS imaging analyses."
  - label: "Space"
    value: "Say which space it is in"
    text: "Lead-DBS works in the [ICBM 2009b nonlinear asymmetric space](http://nist.mni.mcgill.ca/?p=904) (Fonov 2009), one of [several MNI spaces](/about-the-mni-spaces/). An atlas made in another one, such as the [ATAG atlas](https://www.nitrc.org/projects/atag/) (FSL's [FNIRT](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FNIRT/UserGuide), [MNI 6th-generation template](http://nist.mni.mcgill.ca/?p=858)), fits best with data normalized the same way, which Lead-DBS can do, though not by [default](https://www.sciencedirect.com/science/article/pii/S1053811918318664)."
  - label: "Contact"
    value: "Get in touch"
    text: "[Write to us](/contact/) or [join the user Slack](https://inviter.co/lead-dbs) and ask there."
# the facts, as link cells
facts:
  - {name: "Source code", text: "github.com/netstim/leaddbs, in MATLAB.", url: "https://github.com/netstim/leaddbs"}
  - {name: "Other tools", text: "SlicerNetstim with Lead-OR, and more, under github.com/netstim.", url: "https://github.com/netstim"}
  - {name: "Licence", text: "GNU General Public License, version 3.", url: "https://github.com/netstim/leaddbs/blob/master/LICENSE.md"}
  - {name: "What changed", text: "Every version with its changes on GitHub.", url: "/download/#releases"}
# the next version, in the black panel
upcoming:
  title: "Lead-DBS 4.0 is coming."
  text: "Rebuilt completely in Python."
  link: {page: "/events/hands-on-workshop-2027/", note: "Try the pre-release first, 11–12 February 2027", text: "Hands-on Workshop"}
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - "/events/developer-meeting/"
  - "/about/lead-dbs-dependencies/"
  - "/helpsupport/knowledge-base/atlasesresources/"
# the picture shown when the page is shared (head.html)
share: "images/renders/head-community.jpg"
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/events/developer-meeting/", text: "Monthly, online, open to anyone"}
  - {page: "/helpsupport/slack-user-channel/", text: "Ask other users and the developers"}
  - {page: "/about/lead-dbs-dependencies/", text: "The software Lead-DBS builds on"}
---

Lead-DBS is open source and grows with its community.
