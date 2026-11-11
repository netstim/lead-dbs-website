---
title: "Download Lead-DBS"
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
---

Lead-DBS {{< release version >}}, released on {{< release date >}}, is free and open source. Pick any download server below: no form and no sign-up.

## What you need

- **MATLAB {{< release matlab >}} or later**, with the Image Processing, Signal Processing, and Statistics and Machine Learning Toolboxes. The Curve Fitting and Parallel Computing Toolboxes are optional.
- **[SPM12](https://www.fil.ion.ucl.ac.uk/spm/software/download/)**
- **32 GB of RAM** or more (recommended)
- **Disk space:** the download is a single zip file of about 11 GB. You need room for the zip file and for the unpacked folder.
- **Your data:** postoperative (and, if available, preoperative) structural MRI, or postoperative CT together with preoperative MRI.

## Normal version ({{% release version %}}) {#normal-version}

Lead-DBS with several [subcortical atlases](/helpsupport/knowledge-base/atlasesresources/atlases-2/) included. The five servers hold the same file: pick any one.

{{< downloads >}}
- [pCloud](https://www.lead-dbs.org/release/download.php?id=leaddbs_pcloud)
- [OneDrive](https://www.lead-dbs.org/release/download.php?id=leaddbs_onedrive)
- [Sciebo](https://www.lead-dbs.org/release/download.php?id=leaddbs_sciebo)
- [Lead-DBS.org](https://www.lead-dbs.org/release/download.php?id=latest)
- [BaiduPan](https://www.lead-dbs.org/release/download.php?id=leaddbs_baidu)
{{< /downloads >}}

## Standalone version ({{% release standalone %}}), no MATLAB needed {#standalone-version}

Experimental builds that run without MATLAB, one per system. They are older than the normal version and won't receive regular updates or hotfixes, so we recommend the normal version where possible. The Windows build is about 13 GB.

{{< downloads prefix="Download for" >}}
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
- New to Lead-DBS? Practise on a first dataset with [Lead Tutor](/helpsupport/learn-lead-dbs-yourself/).
- What changed: read the [announcement of this release]({{% release notes %}}); every released version is listed among the [tags on GitHub](https://github.com/netstim/leaddbs/tags).

## Help

Stuck during installation or later? The [manual](https://netstim.gitbook.io/leaddbs), the [walkthrough videos](/helpsupport/knowledge-base/walkthrough-videos/) and the [user Slack](https://inviter.co/lead-dbs) are the places to start; bugs go to [GitHub issues](https://github.com/netstim/leaddbs/issues). More on the [help page](/helpsupport/).

## Newsletter (optional)

You do not need to subscribe to download Lead-DBS. If you like, the newsletter tells you about new releases, critical bug fixes and workshops. It is sent rarely.

{{< newsletter >}}
