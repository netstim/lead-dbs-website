---
title: "Atlases and data"
description: "Brain atlases, parcellations and normative connectomes in MNI space that work with Lead-DBS, and where to get them."
date: "2017-04-08T22:50:27"
lastmod: "2026-11-11"
weight: 6
keywords: ["atlas", "atlases", "connectome", "connectomes", "parcellation", "data", "resources"]
# the picture shown when the page is shared (head.html)
share: "images/renders/cohort-black.jpg"
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - "/helpsupport/knowledge-base/lead-dbs-methods/"
  - {name: "Add your atlas or dataset", url: "/develop/#add-your-atlas-or-dataset"}
  - "/about/citing_leaddbs/"
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/develop/#add-your-atlas-or-dataset", name: "Add your atlas or dataset", text: "Missing an atlas, or want yours in Lead-DBS?"}
---
All are in standard (MNI) space, and many come with Lead-DBS. Each page says what an atlas holds, how to get it and which paper to cite.

{{< childpages menu="true" >}}

<span id="built-for-lead-dbs"></span>DISTAL and FOCUS, made by the Lead-DBS team, are also listed among the [subcortical atlases](/helpsupport/knowledge-base/atlasesresources/atlases-2/).

## Choosing and using an atlas or connectome {#choosing}

- **Read the paper** behind an atlas or connectome before you rely on it: every entry names it.
- **Unsure about the space?** Use an atlas made for Lead-DBS, such as
  [DISTAL](/helpsupport/knowledge-base/atlasesresources/distal-atlas/) or the
  [Human Motor Thalamus atlas](/helpsupport/knowledge-base/atlasesresources/atlases-2/#human-motor-thalamus-atlas-ilinsky-2018).
- **Know your connectome.** Normative connectomes are averages, not a patient's own wiring.
  Tractography is
  [prone to false-positive connections](https://www.nature.com/articles/s41467-017-01285-x) and
  [cannot resolve small subcortical bundles](https://www.sciencedirect.com/science/article/abs/pii/S0896627319308323);
  resting-state fMRI connectivity
  [includes many indirect connections](https://www.ncbi.nlm.nih.gov/pubmed/23583357) and misses fast
  signals such as those from MER, ECoG, LFP, EEG or MEG.
- **Check your results** with control analyses, or with a different atlas, connectome or pathway.
- **Not sure what a step does?** [Ask](/helpsupport/#get-help).

## Other data

The **IXI dataset**, an age-matched reference for converting AC/PC coordinates into MNI space, comes with the [AC/PC to MNI conversion](/helpsupport/knowledge-base/lead-dbs-methods/acpc-to-mni-conversion-2/#ixi); the **Lead Tutor** dataset, for practising electrode localization, has a [page of its own](/helpsupport/learn-lead-dbs-yourself/).
