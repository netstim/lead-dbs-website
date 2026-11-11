---
title: "Download Lead-DBS"
# the browser title (head.html adds " – Lead-DBS")
htmlTitle: "Download"
description: "Download Lead-DBS: requirements, the download servers, installation in four steps, the standalone builds and the release history."
date: "2014-06-17T15:07:00"
lastmod: "2026-11-11"
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
keywords: ["download", "release history", "changelog", "release notes", "version history", "versions", "install", "installation", "setup", "requirements", "matlab", "standalone", "licence", "license"]
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - "/helpsupport/first-steps/"
  - "/helpsupport/knowledge-base/walkthrough-videos/"
  - "/about/citing_leaddbs/"
# the picture shown when the page is shared (head.html)
share: "images/renders/cohort-front.jpg"
# found by the site search as results of their own (layouts/home.searchindex.json)
searchEntries:
  - {title: "Lead-DBS 4.0", id: "lead-dbs-4", keywords: "4.0 v4 version 4 Python next version no MATLAB pre-release", description: "Lead-DBS 4.0 is coming, rebuilt completely in Python: no MATLAB required."}
---

## Lead-DBS {{% release version %}} {#normal-version}

{{< download-release >}}
- [pCloud](https://www.lead-dbs.org/release/download.php?id=leaddbs_pcloud)
- [OneDrive](https://www.lead-dbs.org/release/download.php?id=leaddbs_onedrive)
- [Sciebo](https://www.lead-dbs.org/release/download.php?id=leaddbs_sciebo)
- [Lead-DBS.org](https://www.lead-dbs.org/release/download.php?id=latest)
- [BaiduPan](https://www.lead-dbs.org/release/download.php?id=leaddbs_baidu)
{{< /download-release >}}

It includes several [subcortical atlases](/helpsupport/knowledge-base/atlasesresources/atlases-2/). What
changed: the [announcement of this release]({{% release notes %}}) and the [release history](#releases).

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
[Hands-on Lead-DBS Workshop](/hands-on-lead-dbs-workshop-cologne-2027/) on 11–12 February 2027 will be
among the first to try the pre-release.

## Licence and terms of use

By downloading Lead-DBS, you accept the following:

- Lead-DBS and its toolboxes are free but copyright software, distributed under the terms of the [GNU General Public License, version 3](https://github.com/netstim/leaddbs/blob/master/LICENSE.md), as published by the Free Software Foundation.
- Lead-DBS comes with absolutely no warranty whatsoever.

Lead-DBS is research software intended for retrospective scientific analysis of neuroimaging data, electrode locations and group-level associations in research studies. It is not intended for diagnosis, treatment planning, surgical targeting, DBS programming, patient management, or any other clinical decision concerning an individual patient. Outputs must not be used as a basis for clinical care.
{#research-use .fine-print}

## Release history {#releases}

{{< release-history >}}

## Help

Stuck during installation or later? The manual's [installation guide](https://netstim.gitbook.io/leaddbs/installation) covers most problems; where to ask about the rest is under [Get help](/helpsupport/#get-help). News of releases and critical fixes: the [newsletter](/subscribe-to-our-newsletter/).

## Next

Installed? Take the [first steps](/helpsupport/first-steps/): localize the electrodes of the open Lead Tutor patients and let Lead Tutor score your result.
