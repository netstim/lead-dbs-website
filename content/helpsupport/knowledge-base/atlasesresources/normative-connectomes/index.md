---
title: "Normative connectomes"
description: "Normative connectomes: average structural and functional wiring diagrams of the human brain in MNI space, for use with Lead-DBS."
date: "2017-12-29T11:56:26"
lastmod: "2026-11-11"
weight: 3
aliases: ["/sdm_downloads/groupconnectome-horn-2013/"]
# the picture shown when the page is shared (head.html)
share: "images/renders/fiber-filtering.jpg"
# "Related" at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/helpsupport/knowledge-base/atlasesresources/cortical-atlas-parcellations-mni-space/"}
  - {page: "/helpsupport/knowledge-base/lead-dbs-methods/connectivity-benefit-mapping/"}
  - {page: "/manual/connectomics/connectomic-analyses/", name: "Connectivity in the manual"}
---
Average structural (tractography) and functional (resting-state fMRI) wiring of the human brain in MNI space,
for when a patient's own diffusion or fMRI data are missing.

<span id="list-of-currently-available-connectomes"></span>

{{< atlas-index noun="connectomes" >}}

{{% atlas-group "structural" %}}

{{% atlas-group "functional" %}}

<span id="background"></span>

<details class="more">
<summary>From the first connectome in 2014 to the clinical uses</summary>

Since 2014, structural and functional connectomes of large cohorts have been warped into standard space
and averaged across the group.

- **2014:** a [first structural-functional MNI connectome](https://doi.org/10.1016/j.neuroimage.2013.09.069), led by [Felix Blankenburg](https://scholar.google.de/citations?user=-QOB8EoAAAAJ), with a small [data article](https://doi.org/10.1016/j.dib.2015.08.035).
- **2016:** results [replicated](https://doi.org/10.1016/j.neuroimage.2015.08.048) in a much larger cohort, validating normative connectomes by reproducing connectomic studies in template space.
- **2017:** connectivity combined with [electrophysiological recordings](https://doi.org/10.1002/hbm.23594) of the subcortex (led by [Andrea A Kühn](https://scholar.google.de/citations?user=3sSXEQwAAAAJ)), on the high-quality multishell diffusion data of the [Human Connectome Project](https://www.humanconnectome.org/) ([Setsompop 2013](https://doi.org/10.1016/j.neuroimage.2013.05.078)); [connectivity profiles of DBS targets](https://doi.org/10.1016/j.neuroimage.2017.02.004) (led by [Michael D Fox](https://scholar.google.co.uk/citations?user=d9kqMj0AAAAJ)) with the 1000-subject functional connectome of the [Brain Genomics Superstruct Project](https://www.neuroinfo.org/gsp/), preprocessed by [Thomas Yeo](https://scholar.google.com/citations?user=BOUzsU8AAAAJ) ([Yeo 2011](https://doi.org/10.1152/jn.00338.2011)); and structural and functional connectomes of patients with Parkinson's disease from the [PPMI](https://www.ppmi-info.org/) ([Horn 2017](https://doi.org/10.1002/ana.24974)).

Normative connectomes describe cohort-derived connectivity, not an individual patient’s. Tractography can [include false connections](https://www.nature.com/articles/s41467-017-01285-x)
and [miss small bundles](https://www.sciencedirect.com/science/article/abs/pii/S0896627319308323); resting-state fMRI connectivity can
[reflect indirect connections](https://www.ncbi.nlm.nih.gov/pubmed/23583357). So they do not replace a patient's own connectivity, but help where it cannot be measured:
after **DBS surgery**, when MRI is restricted (Horn [2017a](https://onlinelibrary.wiley.com/doi/10.1002/ana.24974/abstract), [b](https://www.ncbi.nlm.nih.gov/pubmed/28163141), [c](https://onlinelibrary.wiley.com/doi/10.1002/hbm.23594/abstract));
for **noninvasive stimulation** such as TMS ([Weigand 2017](https://doi.org/10.1016/j.biopsych.2017.10.028));
after a **stroke**, to estimate the lesion site’s connectivity before the stroke ([Boes 2015](https://doi.org/10.1093/brain/awv228), [Laganiere 2016](https://doi.org/10.1212/WNL.0000000000002741), [Fischer 2016](https://doi.org/10.1212/WNL.0000000000003404), [Darby 2016](https://doi.org/10.1093/brain/aww288) and [2017](https://doi.org/10.1073/pnas.1706587115), [Fasano 2017](https://doi.org/10.1002/ana.24845));
and in **large retrospective databases** ([Horn 2017a](https://onlinelibrary.wiley.com/doi/10.1002/ana.24974/abstract)).

</details>

## Is a connectome missing?

Know a connectome that should be listed here, or want yours to come with Lead-DBS?
[Write to us](/contact/).
