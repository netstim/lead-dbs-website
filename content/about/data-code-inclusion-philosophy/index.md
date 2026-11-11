---
title: "Data and code inclusion philosophy"
description: "How to get your atlas, dataset, method or code into Lead-DBS, and how to make good use of what is already included."
date: "2020-04-10T08:24:14"
lastmod: "2026-11-11"
weight: 6
menuParent: "/develop"
keywords: ["contribute", "atlas", "dataset", "code", "inclusion", "philosophy", "pull request"]
---

Lead-DBS grows with its community. We include as much useful code and as many useful atlases and
datasets as we can, so that published work stays reproducible and nobody has to build the same tool
twice. Lead-DBS aims to be:

- **inclusive**: any useful feature, atlas or dataset is welcome;
- **open and transparent**: everything that goes in can be read, checked and cited;
- **driven by its users**: anyone in the research community who wants to contribute can.

## Add your code

- **A feature is missing?** Add it yourself: open a pull request on
  [GitHub](https://github.com/netstim/leaddbs), or ask for push access.
  [Develop Lead-DBS](/develop/#how-to-contribute) shows how to set up a development copy.
- **A feature would change what Lead-DBS is for?** It can live in a fork of the repository.
- **Make it citable.** Where possible, the interface names the first paper that used a feature; the
  AC/PC to MNI conversion, for instance, refers to
  [Horn et al. 2017, NeuroImage](https://www.ncbi.nlm.nih.gov/pubmed/28163141). Development is fast,
  so some features reach Lead-DBS before a study has used them.

## Add your atlas or dataset

- **Any source is welcome**: atlases from MRI, histology, connectivity, drawings or synthesized maps,
  and datasets that help analyses in the field of Lead-DBS.
- **Published atlases** are included so that the studies behind them can be reproduced.
- **Say which space it is in.** Lead-DBS works in the
  [ICBM 2009b nonlinear asymmetric space](http://nist.mni.mcgill.ca/?p=904) (Fonov 2009), one of
  [several MNI spaces](/about-the-mni-spaces/). An atlas made in another one, such as the
  [ATAG atlas](https://www.nitrc.org/projects/atag/) (FSL's
  [FNIRT](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FNIRT/UserGuide),
  [MNI 6th-generation template](http://nist.mni.mcgill.ca/?p=858)), fits best with data normalized
  the same way, which Lead-DBS can do, though not by
  [default](https://www.sciencedirect.com/science/article/pii/S1053811918318664).
- **Get in touch**: [write to us](/contact/) or ask on the [user Slack](/helpsupport/slack-user-channel/).

## Use what is included well

No atlas or connectome fits every question. These habits help:

- **Read the original paper** of an atlas or connectome before you rely on it; the
  [atlas catalogue](/helpsupport/knowledge-base/atlasesresources/atlases-2/) and the
  [publications](/about/publications/) list them.
- **Unsure about the space?** Use an atlas made for Lead-DBS, such as
  [DISTAL](/helpsupport/knowledge-base/atlasesresources/distal-atlas/) or the
  [Human Motor Thalamus atlas](/helpsupport/knowledge-base/atlasesresources/atlases-2/#human-motor-thalamus-atlas-ilinsky-2018).
- **Know your connectome.** Normative connectomes are not patient-specific; know how they were made.
  Tractography is
  [prone to false-positive connections](https://www.nature.com/articles/s41467-017-01285-x) and
  [cannot resolve small subcortical bundles](https://www.sciencedirect.com/science/article/abs/pii/S0896627319308323);
  functional connectivity from resting-state fMRI
  [includes many indirect connections](https://www.ncbi.nlm.nih.gov/pubmed/23583357) and does not see
  fast signals such as those from MER, ECoG, LFP, EEG or MEG.
- **Check your results** with control analyses, or with a different atlas, connectome or pathway.
- **Not sure what a step does?** [Ask](/helpsupport/#get-help): we are glad to help.

## Next

Browse what is included under [Atlases and data](/helpsupport/knowledge-base/atlasesresources/), or
read why Lead-DBS is built as [academic research software](/commercial-vs-academic-software/).
