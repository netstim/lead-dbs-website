---
title: "Download Lead-DBS"
description: "Download Lead-DBS: requirements, the download servers, installation in four steps, the standalone builds and the release history."
date: "2014-06-17T15:07:00"
lastmod: "2026-11-12"
weight: 7
# /download-lead-dbs/ was the page with the files; the WordPress download items
# (/sdm_downloads/…) were single download buttons. All of them end here now.
aliases:
  - "/download-lead-dbs/"
  - "/sdm_downloads/lead-dbs/"
  - "/sdm_downloads/download-via-pcloud/"
  - "/sdm_downloads/download-via-onedrive/"
  - "/sdm_downloads/download-via-sciebo/"
  - "/sdm_downloads/download-via-baidupan/"
  - "/sdm_downloads/download-via-dropbox/"
  - "/sdm_downloads/download-standalone-linux/"
  - "/sdm_downloads/download-standalone-windows/"
  - "/sdm_downloads/download-standalone-mac-x86_64/"
  - "/sdm_downloads/download-standalone-mac-arm64/"
keywords: ["download", "release history", "changelog", "release notes", "version history", "versions", "install", "installation", "setup", "requirements", "matlab", "standalone", "licence", "license", "windows", "linux", "macos", "mac os", "mac", "apple silicon", "intel", "no matlab", "without matlab", "github"]
# this page has its own template (layouts/download.html): the hero with the download, then the sections
layout: "download"
# the sections that template draws, for the search entries below (the build checks them against this list)
anchors: ["what-you-need", "install", "standalone-version", "lead-dbs-4", "releases"]
# the servers that hold the current release, the recommended one first
mirrors:
  - {name: "pCloud", url: "https://www.lead-dbs.org/release/download.php?id=leaddbs_pcloud"}
  - {name: "OneDrive", url: "https://www.lead-dbs.org/release/download.php?id=leaddbs_onedrive"}
  - {name: "Sciebo", url: "https://www.lead-dbs.org/release/download.php?id=leaddbs_sciebo"}
  - {name: "Lead-DBS.org", url: "https://www.lead-dbs.org/release/download.php?id=latest"}
  - {name: "BaiduPan", url: "https://www.lead-dbs.org/release/download.php?id=leaddbs_baidu"}
size: "11 GB"
# the standalone builds (their version: data/release.yaml, standalone)
standalone:
  - {name: "Linux", url: "https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_linux"}
  - {name: "macOS", note: "Intel", url: "https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_mac_x86_64"}
  - {name: "macOS", note: "Apple silicon", url: "https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_mac_arm64"}
  - {name: "Windows", note: "about 13 GB", url: "https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_windows"}
# the next version, in the black panel
upcoming:
  title: "Lead-DBS 4.0 is coming."
  text: "Rebuilt completely in Python. No MATLAB required."
  link: {page: "/events/hands-on-workshop-2027/", note: "Try the pre-release first, 11–12 February 2027", text: "Hands-on Workshop"}
# the terms of use, in the dialog the "Terms of use" button opens (text: Markdown; id: an anchor
# other pages link to)
terms:
  - label: "Licence"
    value: "GNU GPL v3"
    text: "By downloading Lead-DBS you accept that it and its toolboxes are free but copyrighted software under the [GNU General Public License, version 3](https://github.com/netstim/leaddbs/blob/master/LICENSE.md), as published by the Free Software Foundation, and that it comes with absolutely no warranty."
  - label: "Use"
    value: "For research only"
    id: "research-use"
    text: "Lead-DBS is research software intended for retrospective scientific analysis of neuroimaging data, electrode locations and group-level associations in research studies. It is not intended for diagnosis, treatment planning, surgical targeting, DBS programming, patient management, or any other clinical decision concerning an individual patient. Outputs must not be used as a basis for clinical care."
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - "/helpsupport/first-steps/"
  - "/helpsupport/knowledge-base/walkthrough-videos/"
  - "/about/citing_leaddbs/"
# the picture shown when the page is shared (head.html)
share: "images/renders/cohort-front.jpg"
# found by the site search as results of their own (layouts/home.searchindex.json)
searchEntries:
  - {title: "Standalone version: Windows, macOS, Linux", id: "standalone-version", keywords: "standalone no matlab without matlab compiled windows linux macos mac os mac apple silicon intel", description: "Experimental builds of Lead-DBS that run without MATLAB, for Windows, macOS (Intel and Apple silicon) and Linux."}
  - {title: "Release history", id: "releases", keywords: "release history release notes changelog change log changes what changed versions version history older versions", description: "Every version of Lead-DBS with its date, its announcement and what changed."}
  - {title: "Lead-DBS 4.0", id: "lead-dbs-4", keywords: "4.0 v4 version 4 Python next version no MATLAB pre-release", description: "Lead-DBS 4.0 is coming, rebuilt completely in Python: no MATLAB required."}
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/helpsupport/first-steps/", text: "Installed? Your first electrode localization"}
  - {page: "/helpsupport/knowledge-base/lead-dbs-methods/", text: "What Lead-DBS does, with the manual chapter for each"}
---
