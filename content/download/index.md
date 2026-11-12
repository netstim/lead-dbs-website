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

## Lead-DBS {{% release version %}} {#normal-version}

{{< download-release >}}
- [pCloud](https://www.lead-dbs.org/release/download.php?id=leaddbs_pcloud)
- [OneDrive](https://www.lead-dbs.org/release/download.php?id=leaddbs_onedrive)
- [Sciebo](https://www.lead-dbs.org/release/download.php?id=leaddbs_sciebo)
- [Lead-DBS.org](https://www.lead-dbs.org/release/download.php?id=latest)
- [BaiduPan](https://www.lead-dbs.org/release/download.php?id=leaddbs_baidu)
{{< /download-release >}}

## What you need

{{< install "requirements" >}}

## Install {#install}

{{< install "steps" >}}

The manual's [installation guide](https://netstim.gitbook.io/leaddbs/installation#normal-installation) explains each step; to change the code or get daily fixes, [install from GitHub](https://netstim.gitbook.io/leaddbs/installation#installation-via-github) instead.

## Standalone version ({{% release standalone %}}), no MATLAB needed {#standalone-version}

Experimental builds of Lead-DBS {{% release standalone %}} (released {{% release standalone_date %}}) that run without MATLAB, one per system. They won't receive regular updates or hotfixes, so we recommend the MATLAB version where possible. The Windows build is about 13 GB.

{{< downloads prefix="Download for" variant="secondary" >}}
- [Linux](https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_linux)
- [macOS (Intel)](https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_mac_x86_64)
- [macOS (Apple silicon)](https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_mac_arm64)
- [Windows](https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_windows)
{{< /downloads >}}

## Lead-DBS 4.0 {#lead-dbs-4}

Lead-DBS 4.0 is coming, rebuilt completely in Python: no MATLAB required. Participants of the
[Hands-on Lead-DBS Workshop](/events/hands-on-workshop-2027/) on 11–12 February 2027 will be
among the first to try the pre-release.

## Licence and terms of use

Free and open source under the [GNU General Public License, version 3](https://github.com/netstim/leaddbs/blob/master/LICENSE.md), with no warranty; for research use only.

<details class="more">
<summary>The full terms</summary>

By downloading Lead-DBS you accept that it and its toolboxes are free but copyrighted software under the [GNU General Public License, version 3](https://github.com/netstim/leaddbs/blob/master/LICENSE.md), as published by the Free Software Foundation, and that it comes with absolutely no warranty.

Lead-DBS is research software intended for retrospective scientific analysis of neuroimaging data, electrode locations and group-level associations in research studies. It is not intended for diagnosis, treatment planning, surgical targeting, DBS programming, patient management, or any other clinical decision concerning an individual patient. Outputs must not be used as a basis for clinical care.
{#research-use .fine-print}

</details>

## Release history {#releases}

<details class="more more--wide">
<summary>All versions, with what changed</summary>

{{< release-history >}}

</details>

## Help

Stuck during installation or later? The manual's [installation guide](https://netstim.gitbook.io/leaddbs/installation) covers most problems; where to ask about the rest is under [Get help](/helpsupport/#get-help). News of releases and critical fixes: the [newsletter](/subscribe-to-our-newsletter/).
