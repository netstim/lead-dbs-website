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
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/about/publications/", text: "Papers about Lead-DBS, and studies that used it"}
---
If you use Lead-DBS in a paper, please cite the paper on the current version, Lead-DBS v3:

{{% copybox label="Copy the citation" %}}
{{< paper neudorfer2023 "full" >}}
{{% /copybox %}}

Research Resource Identifier: [RRID:SCR_002915](https://scicrunch.org/scicrunch/Resources/record/nlx_144509-1/5f2345e7-4b61-51f4-8d44-4b9b8cdf8868/search?q=lead%20dbs&l=lead%20dbs)

Where they apply, also cite:

- **Lead Group**, for group analyses: {{< paper treu2020 >}}
- **The atlases and connectomes you used**: each entry under [Atlases and data](/helpsupport/knowledge-base/atlasesresources/) names its paper
- **The libraries your analysis used**, such as OSS-DBS, ANTs and SPM: listed under [dependencies](/about/lead-dbs-dependencies/); the file `ea_methods.txt` in each patient folder lists the methods Lead-DBS applied

Used Lead-DBS v2 or earlier? Cite {{< paper horn2019 >}} and {{< paper horn2015 >}}.

## A methods paragraph to adapt {#methods-snippet}

<details class="more more--wide">
<summary>Show an example methods paragraph</summary>

Based on one of our papers: adapt it to the steps and tools you used.

{{% copybox label="Copy the paragraph" %}}
DBS electrodes were localized with the advanced processing pipeline [*(Horn & Li et al. 2019)*](https://doi.org/10.1016/j.neuroimage.2018.08.068) of Lead-DBS v3 ([lead-dbs.org](/); [*Neudorfer et al. 2023*](https://doi.org/10.1016/j.neuroimage.2023.119862); [*Horn & Kühn 2015*](https://doi.org/10.1016/j.neuroimage.2014.12.002); RRID:SCR_002915). Postoperative CT or MRI were linearly coregistered to preoperative MRI with advanced normalization tools (ANTs; [stnava.github.io/ANTs/](http://stnava.github.io/ANTs/); [*Avants et al. 2011*](https://doi.org/10.1016/j.neuroimage.2010.09.025)), inspected and refined if needed, and corrected for brain shift as implemented in Lead-DBS. All preoperative volumes were used for a multispectral normalization to ICBM 2009b NLIN asymmetric (“MNI”) space [*(Fonov et al. 2009)*](https://doi.org/10.1016/S1053-8119(09)70884-5) with the ANTs SyN Diffeomorphic Mapping [*(Avants et al. 2008)*](https://doi.org/10.1016/j.media.2007.06.004), preset “effective: low variance default + subcortical refinement”; where it failed, with the multispectral Unified Segmentation [*(Ashburner et al. 2005)*](https://doi.org/10.1016/j.neuroimage.2005.02.018) of SPM12 ([fil.ion.ucl.ac.uk/spm](https://www.fil.ion.ucl.ac.uk/spm); [*Friston et al. 1994*](https://doi.org/10.1002/hbm.460020402)). Both presets of Lead-DBS segmented the STN about as precisely as manual experts in a comparative study [*(Ewert et al. 2019)*](https://doi.org/10.1016/j.neuroimage.2018.09.061). Contacts were pre-reconstructed with PaCER [*(Husch et al. 2018)*](https://doi.org/10.1016/j.nicl.2017.10.004) or TRAC/CORE and refined manually if needed; the orientation of segmented leads with DiODe [*(Dembek et al. 2019)*](https://doi.org/10.1016/j.parkreldis.2019.08.017). Atlas structures are from the DISTAL atlas [*(Ewert et al. 2018)*](https://doi.org/10.1016/j.neuroimage.2017.05.015); group visualizations were made with Lead Group [*(Treu et al. 2020)*](https://doi.org/10.1016/j.neuroimage.2020.117018).
{{% /copybox %}}

</details>
