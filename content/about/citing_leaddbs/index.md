---
title: "Cite Lead-DBS"
description: "Which papers to cite when you use Lead-DBS, with a methods paragraph you can copy."
date: "2020-02-13T06:03:01"
lastmod: "2026-11-11"
weight: 1
keywords: ["cite", "citation", "citing", "reference", "references", "rrid", "methods paragraph"]
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - "/about/publications/"
  - "/helpsupport/knowledge-base/lead-dbs-methods/"
  - "/helpsupport/knowledge-base/atlasesresources/distal-atlas/"
# the picture shown when the page is shared (head.html)
share: "images/renders/head-about.jpg"
---
If you use Lead-DBS in a paper, please cite the paper on the current version, Lead-DBS v3:

{{% copybox label="Copy the citation" %}}
{{< paper neudorfer2023 "full" >}}
{{% /copybox %}}

Where they apply, also cite:

- **Lead Group**, for group analyses: {{< paper treu2020 >}}
- **The atlases and connectomes you used**: each entry under [Atlases and data](/helpsupport/knowledge-base/atlasesresources/) names its paper
- **The libraries your analysis used**, such as OSS-DBS, ANTs and SPM: listed under [dependencies](/about/lead-dbs-dependencies/); the file `ea_methods.txt` in each patient folder lists the methods Lead-DBS applied

Lead-DBS v2 or earlier: {{< paper horn2019 >}} and {{< paper horn2015 >}}. Research Resource Identifier:
[RRID:SCR_002915](https://scicrunch.org/scicrunch/Resources/record/nlx_144509-1/5f2345e7-4b61-51f4-8d44-4b9b8cdf8868/search?q=lead%20dbs&l=lead%20dbs).

## A methods paragraph to adapt {#methods-snippet}

<details class="more more--wide">
<summary>Show an example methods paragraph</summary>

From one of our papers: adapt it to the steps and tools you used.

{{% copybox label="Copy the paragraph" %}}
DBS electrodes were localized using the advanced processing pipeline [*(Horn & Li et al. 2019)*](https://doi.org/10.1016/j.neuroimage.2018.08.068) in Lead-DBS v3 ([lead-dbs.org](/); [*Neudorfer et al. 2023*](https://doi.org/10.1016/j.neuroimage.2023.119862); [*Horn & Kühn 2015*](https://doi.org/10.1016/j.neuroimage.2014.12.002); RRID:SCR_002915). In short, postoperative CT or MRI were linearly coregistered to preoperative MRI using advanced normalization tools (ANTs; [stnava.github.io/ANTs/](http://stnava.github.io/ANTs/); [*Avants et al. 2011*](https://doi.org/10.1016/j.neuroimage.2010.09.025)). Coregistrations were inspected and refined if needed. A brain shift correction step was applied as implemented in Lead-DBS. All preoperative volumes were used to estimate a precise multispectral normalization to ICBM 2009b NLIN asymmetric (“MNI”) space [*(Fonov et al. 2009)*](https://doi.org/10.1016/S1053-8119(09)70884-5) applying the ANTs SyN Diffeomorphic Mapping [*(Avants et al. 2008)*](https://doi.org/10.1016/j.media.2007.06.004) using the preset “effective: low variance default + subcortical refinement”. In some patients where this strategy failed, a multispectral implementation of the Unified Segmentation approach [*(Ashburner et al. 2005)*](https://doi.org/10.1016/j.neuroimage.2005.02.018) implemented in Statistical Parametric Mapping software (SPM12; [fil.ion.ucl.ac.uk/spm](https://www.fil.ion.ucl.ac.uk/spm); [*Friston et al. 1994*](https://doi.org/10.1002/hbm.460020402)) was applied. These two methods are available as presets in Lead-DBS and were top-performers to segment the STN with precision comparable to manual expert segmentations in a recent comparative study [*(Ewert et al. 2019)*](https://doi.org/10.1016/j.neuroimage.2018.09.061). DBS contacts were automatically pre-reconstructed using the phantom-validated and fully-automated PaCER method [*(Husch et al. 2018)*](https://doi.org/10.1016/j.nicl.2017.10.004) or the TRAC/CORE approach and manually refined if needed. For segmented leads, the orientation of electrode segments was reconstructed using the Directional Orientation Detection (DiODe) algorithm [*(Dembek et al. 2019)*](https://doi.org/10.1016/j.parkreldis.2019.08.017). Atlas segmentations in this manuscript are defined by the DISTAL atlas [*(Ewert et al. 2018)*](https://doi.org/10.1016/j.neuroimage.2017.05.015). Group visualizations were performed using the Lead Group toolbox [*(Treu et al. 2020)*](https://doi.org/10.1016/j.neuroimage.2020.117018).
{{% /copybox %}}

</details>

## Next

More papers about Lead-DBS, and studies that used it: [Publications](/about/publications/).
