---
title: "Develop Lead-DBS"
date: "2026-11-10"
description: "Source code, licence, how to contribute, bug reports and the developer meeting."
---

Lead-DBS is open source, and contributions are welcome: code, fixes, atlases and data, or simply a well-described bug report.

## Source code and licence

- **Source code:** [github.com/netstim/leaddbs](https://github.com/netstim/leaddbs) (MATLAB). The institute's other tools, such as [SlicerNetstim](https://github.com/netstim/SlicerNetstim) with Lead-OR, are under [github.com/netstim](https://github.com/netstim).
- **Licence:** [GNU General Public License, version 3](https://github.com/netstim/leaddbs/blob/master/LICENSE.md).

## How to contribute

The repository's README puts it this way: "We’d love to implement your improvements into Lead-DBS – please contact us for direct push access to Github or feel free to add pull-requests to the Lead-DBS repository."

To work on the code, install Lead-DBS from GitHub instead of the download:

1. Make sure you meet the [prerequisites](/download/#what-you-need).
2. Clone the [repository](https://github.com/netstim/leaddbs) and switch to the `develop` branch.
3. Download the necessary [data](https://www.lead-dbs.org/release/download.php?id=data_pcloud) and unzip it into the cloned repository.
4. Add SPM12 and Lead-DBS to the MATLAB path and run `ea_setpath`.

The manual's [installation via GitHub](https://netstim.gitbook.io/leaddbs/installation#installation-via-github) describes each step.

Before including a dataset or a piece of code, please read our [philosophy on including code and datasets into Lead-DBS](/about/data-code-inclusion-philosophy/). Lead-DBS builds on many shared libraries; they are listed on the [dependencies page](/about/lead-dbs-dependencies/).

## Report a bug

Please open an issue on [GitHub](https://github.com/netstim/leaddbs/issues). Questions about using Lead-DBS are best asked on the [user Slack](https://inviter.co/lead-dbs).

## Developer meeting

The first Lead-DBS Developer Meeting is on **Wednesday, 18 November 2026, at 15:00 Berlin time (CET)**, on Zoom. It is open to anyone who wants to contribute or to learn about the ongoing development. The meetings are planned monthly; further dates are not set yet.

To receive the Zoom link, register through the [events page](/events/): you leave your e-mail address and are sent the link. Until registration opens there, the link is shared on the [user Slack](https://inviter.co/lead-dbs). The link is not published on this website.

## What changed in each release

Every release is a tag in the repository: see the [list of tags](https://github.com/netstim/leaddbs/tags). GitHub shows all changes between two releases, for example [3.2 to 3.2.1](https://github.com/netstim/leaddbs/compare/v3.2...v3.2.1). Each release is also announced in the [news](/news/) and the [newsletter](/subscribe-to-our-newsletter/).

## What comes next

Lead-DBS 4.0 is coming, rebuilt completely in Python. Participants of the [Hands-on Lead-DBS Workshop](/helpsupport/workshops/) on 11–12 February 2027 will be among the first to try the pre-release.
