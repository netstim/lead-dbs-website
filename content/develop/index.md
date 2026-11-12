---
title: "Contribute"
date: "2026-11-10"
lastmod: "2026-11-11"
description: "Contribute to Lead-DBS: code and fixes, atlases and datasets, bug reports; the source code, its licence and the developer meeting."
keywords: ["contribute", "code", "github", "developer", "pull request", "bug", "changelog", "release notes", "source", "atlas", "dataset", "method", "inclusion", "data and code inclusion philosophy", "contribute an atlas"]
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

Lead-DBS is open source and grows with its community: code, fixes, atlases and datasets are welcome,
and so is a well-described bug report. Published work stays reproducible when the code and atlases
behind it are part of Lead-DBS.

## Source code and licence

- **Source code:** [github.com/netstim/leaddbs](https://github.com/netstim/leaddbs) (MATLAB). The institute's other tools, such as [SlicerNetstim](https://github.com/netstim/SlicerNetstim) with Lead-OR, are under [github.com/netstim](https://github.com/netstim).
- **Licence:** [GNU General Public License, version 3](https://github.com/netstim/leaddbs/blob/master/LICENSE.md).
- **What changed:** the [release history](/download/#releases) lists every version with its changes on GitHub.

## Add your code {#how-to-contribute}

Open a pull request on [GitHub](https://github.com/netstim/leaddbs), or ask us for push access. To work
on the code, install Lead-DBS from GitHub instead of the download:

1. Make sure you meet the [requirements](/download/#what-you-need).
2. Clone the [repository](https://github.com/netstim/leaddbs) and switch to the `develop` branch.
3. Download the necessary [data](https://www.lead-dbs.org/release/download.php?id=data_pcloud) and unzip it into the cloned repository.
4. Add SPM12 and Lead-DBS to the MATLAB path and run `ea_setpath`.

The manual's [installation via GitHub](https://netstim.gitbook.io/leaddbs/installation#installation-via-github)
describes each step. A feature that would change what Lead-DBS is for can live in a fork. Where possible,
the interface names the paper behind a feature, so that it can be cited: the AC/PC to MNI conversion, for
instance, refers to [Horn et al. 2017, NeuroImage](https://www.ncbi.nlm.nih.gov/pubmed/28163141).

## Add your atlas or dataset {#add-your-atlas-or-dataset}

- **Any source is welcome**: atlases from MRI, histology, connectivity, drawings or synthesized maps,
  and datasets that help DBS imaging analyses. Published atlases are included so that the studies
  behind them can be reproduced.
- **Say which space it is in.** Lead-DBS works in the
  [ICBM 2009b nonlinear asymmetric space](http://nist.mni.mcgill.ca/?p=904) (Fonov 2009), one of
  [several MNI spaces](/about-the-mni-spaces/). An atlas made in another one, such as the
  [ATAG atlas](https://www.nitrc.org/projects/atag/) (FSL's
  [FNIRT](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FNIRT/UserGuide),
  [MNI 6th-generation template](http://nist.mni.mcgill.ca/?p=858)), fits best with data normalized
  the same way, which Lead-DBS can do, though not by
  [default](https://www.sciencedirect.com/science/article/pii/S1053811918318664).
- **Get in touch**: [write to us](/contact/) or [join the user Slack](https://inviter.co/lead-dbs) and ask there.
  Who has contributed atlases and data so far is listed under
  [Contributors](/about/team/#atlases-and-data-contributed-by).

## Report a bug

Please open an issue on [GitHub](https://github.com/netstim/leaddbs/issues). Questions about using
Lead-DBS are best asked on the [user Slack](/helpsupport/slack-user-channel/).

## Developer meeting

[Join the developer meeting](/events/developer-meeting/): what it is, when, and how to register.

## What comes next

[Lead-DBS 4.0](/download/#lead-dbs-4) is coming, rebuilt completely in Python. Participants of the
[Hands-on Lead-DBS Workshop](/events/hands-on-workshop-2027/) on 11–12 February 2027 will be
among the first to try the pre-release.
