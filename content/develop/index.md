---
title: "Develop Lead-DBS"
date: "2026-11-10"
description: "Source code, licence, how to contribute, bug reports and the developer meeting."
keywords: ["contribute", "code", "github", "developer", "pull request", "bug", "changelog", "release notes", "source"]
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

Bringing an atlas, a dataset or a method? [How to get it into Lead-DBS](/about/data-code-inclusion-philosophy/) is a short read. Why Lead-DBS is built as academic research software: [Commercial vs. academic software](/commercial-vs-academic-software/). The libraries it builds on: the [dependencies page](/about/lead-dbs-dependencies/).

## Report a bug

Please open an issue on [GitHub](https://github.com/netstim/leaddbs/issues). Questions about using Lead-DBS are best asked on the [user Slack](https://inviter.co/lead-dbs).

## Developer meeting

Held online and planned monthly, open to anyone who wants to contribute or follow the development: see [Join the developer meeting](/events/developer-meeting/).

## What changed in each release

The [release history](/download/#releases) on the download page lists every version with its date, its announcement and the changes on GitHub.

## What comes next

Lead-DBS 4.0 is coming, rebuilt completely in Python. Participants of the [Hands-on Lead-DBS Workshop](/hands-on-lead-dbs-workshop-cologne-2027/) on 11–12 February 2027 will be among the first to try the pre-release.

## Next

Join the [user Slack](/helpsupport/slack-user-channel/) to talk to other developers, or see who [contributed atlases and data](/about/team/#atlases-and-data-contributed-by).
