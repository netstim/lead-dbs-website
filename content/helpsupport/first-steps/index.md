---
title: "First steps with Lead-DBS"
linkTitle: "First steps"
description: "From download to your first electrode localization: install Lead-DBS, practise on the open Lead Tutor dataset, and where to get help."
date: "2026-11-11"
weight: 1
keywords: ["getting started", "first steps", "install", "installation", "tutorial", "quick start", "documentation", "docs"]
# the picture shown when the page is shared (head.html)
share: "images/renders/insertion-final.png"
---

Install Lead-DBS, then localize the electrodes of the open Lead Tutor patients and let Lead Tutor score
your result against experts. The [manual](https://netstim.gitbook.io/leaddbs) has the details of each step.

## 1. Check what you need

- A computer with **32 GB of RAM** or more.
- **MATLAB {{< release matlab >}}** or later, with these toolboxes, as the manual's
  [installation guide](https://netstim.gitbook.io/leaddbs/installation) lists them:
  - required: Image Processing, Signal Processing, and Statistics and Machine Learning Toolbox;
  - optional: Curve Fitting and Parallel Computing Toolbox.
- **[SPM12](https://www.fil.ion.ucl.ac.uk/spm/software/spm12/)**.

No MATLAB? The [standalone builds](/download/#standalone-version) run without it. They are experimental, are
Lead-DBS {{< release standalone >}} rather than the current version, and do not receive regular updates or fixes.

## 2. Install Lead-DBS

1. [Download Lead-DBS](/download/) (about 11 GB).
2. Unzip it into your MATLAB toolbox folder, for example `Documents/MATLAB/toolbox` in your home folder.
   Avoid the MATLAB installation folder, folders that need administrator rights, and paths with spaces.
3. In MATLAB, add SPM12 to the search path: right-click the SPM12 folder and choose
   *Add to Path → Selected Folders* (not *and Subfolders*).
4. Add Lead-DBS to the search path: right-click the Lead-DBS folder and choose
   *Add to Path → Selected Folders and Subfolders*.
5. Type `lead dbs` in the MATLAB Command Window: the Lead-DBS window opens.

The manual's [installation guide](https://netstim.gitbook.io/leaddbs/installation) also covers the
installation from GitHub, the stimulation modelling (OSS-DBS) and updates.

## 3. Localize your first electrodes with Lead Tutor

[Lead Tutor](/helpsupport/learn-lead-dbs-yourself/) is an open dataset of ten DBS patients with expert
localizations.

1. Download the dataset (linked on the [Lead Tutor page](/helpsupport/learn-lead-dbs-yourself/)).
2. Load it in Lead-DBS and localize the electrodes.
3. Press *Submit Results…* (top right in Lead-DBS): Lead Tutor compares your localizations with the
   experts' and shows how close you came. Repeat as often as you like.

The manual walks through it in [Self-tutoring with Lead Tutor](https://netstim.gitbook.io/leaddbs/lead-dbs/self-tutoring-with-lead-tutor).

## 4. If something goes wrong

- After updating from an older version, errors can come from old settings: run `ea_restoreprefs(1,1)`
  in the MATLAB Command Window and try again.
- *Unrecognized function or variable*: run `ea_setpath` to add all Lead-DBS folders to the search path.
- Still stuck? Ask on the [user Slack](/helpsupport/slack-user-channel/); report bugs on
  [GitHub](https://github.com/netstim/leaddbs/issues).

## Next

Your own patients: the [manual](https://netstim.gitbook.io/leaddbs) describes each step of a full
analysis, and the [walkthrough videos](/helpsupport/knowledge-base/walkthrough-videos/) show them on
screen. [Methods](/helpsupport/knowledge-base/lead-dbs-methods/) lists everything Lead-DBS does, with the
manual chapter and paper for each, and
[Atlases and data](/helpsupport/knowledge-base/atlasesresources/) lists the atlases and connectomes you can use.
Before you publish, see [Cite Lead-DBS](/about/citing_leaddbs/).
