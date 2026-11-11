---
title: "Download Lead-DBS"
description: "Download Lead-DBS: requirements, the download servers, installation and what to do next."
date: "2014-06-17T15:07:00"
lastmod: "2026-11-10"
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
toc: false
keywords: ["download", "release history", "changelog", "release notes", "version history", "versions", "install", "installation", "setup", "requirements", "matlab", "standalone", "licence", "license"]
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

- **MATLAB {{< release matlab >}} or later**, with the Image Processing, Signal Processing, and Statistics and Machine Learning Toolboxes. The Curve Fitting and Parallel Computing Toolboxes are optional.
- **[SPM12](https://www.fil.ion.ucl.ac.uk/spm/software/download/)**
- **32 GB of RAM** or more (recommended)
- **Disk space:** room for the zip file of about 11 GB and for the unpacked folder.
- **Your data:** postoperative (and, if available, preoperative) structural MRI, or postoperative CT together with preoperative MRI.

## Standalone version ({{% release standalone %}}), no MATLAB needed {#standalone-version}

Experimental builds that run without MATLAB, one per system. They are older than the version above and won't receive regular updates or hotfixes, so we recommend the MATLAB version where possible. The Windows build is about 13 GB.
Lead-DBS 4.0, rebuilt completely in Python, will not need MATLAB at all; it is not released yet.

{{< downloads prefix="Download for" variant="secondary" >}}
- [Linux](https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_linux)
- [macOS (Intel)](https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_mac_x86_64)
- [macOS (Apple silicon)](https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_mac_arm64)
- [Windows](https://www.lead-dbs.org/release/download.php?id=leaddbs_standalone_windows)
{{< /downloads >}}

## Licence and terms of use

By downloading Lead-DBS, you accept the following:

- Lead-DBS and its toolboxes are free but copyright software, distributed under the terms of the [GNU General Public License, version 3](https://github.com/netstim/leaddbs/blob/master/LICENSE.md), as published by the Free Software Foundation.
- Lead-DBS comes with absolutely no warranty whatsoever.

{{< notice id="research-use" >}}Lead-DBS is research software intended for retrospective scientific analysis of neuroimaging data, electrode locations and group-level associations in research studies. It is not intended for diagnosis, treatment planning, surgical targeting, DBS programming, patient management, or any other clinical decision concerning an individual patient. Outputs must not be used as a basis for clinical care.{{< /notice >}}

## After downloading

Unzip Lead-DBS into your MATLAB toolbox folder, add SPM12 and Lead-DBS to the MATLAB path, and start it by typing `lead dbs` in the MATLAB Command Window. The [installation guide in the manual](https://netstim.gitbook.io/leaddbs/installation#normal-installation) explains each step.

- Want daily fixes, or to change the code? [Install from GitHub](https://netstim.gitbook.io/leaddbs/installation#installation-via-github) instead; see also [Develop Lead-DBS](/develop/).
- New to Lead-DBS? The [first steps](/helpsupport/first-steps/) take you from here to your first localization; [Lead Tutor](/helpsupport/learn-lead-dbs-yourself/) gives you a first dataset to practise on.

## Release history {#releases}

{{< release-history >}}

## Help

Stuck during installation or later? The manual's [installation guide](https://netstim.gitbook.io/leaddbs/installation) covers most problems; where to ask about the rest is under [Get help](/helpsupport/#get-help).

## Newsletter (optional)

The newsletter tells you about new releases, critical bug fixes and workshops. It is sent rarely.

{{< newsletter >}}
