---
title: "Cite Lead-DBS"
description: "Which papers to cite when you use Lead-DBS, with a methods paragraph you can copy."
date: "2020-02-13T06:03:01"
lastmod: "2026-11-11"
weight: 1
keywords: ["cite", "citation", "citing", "reference", "references", "rrid", "methods paragraph"]
# the picture shown when the page is shared (head.html)
share: "images/renders/head-about.jpg"
# what else to cite, a cell each (layouts/_shortcodes/cells.html; text: Markdown)
also:
  - {label: "Group analyses", value: "Lead Group", text: "[Treu et al. 2020](https://doi.org/10.1016/j.neuroimage.2020.117018), NeuroImage."}
  - {label: "Atlases and connectomes", value: "The ones you used", text: "Each entry under [Atlases and data](/helpsupport/knowledge-base/atlasesresources/) names its paper."}
  - {label: "Libraries", value: "OSS-DBS, ANTs and SPM", text: "Listed under [Dependencies](/about/lead-dbs-dependencies/); `ea_methods.txt` in each patient folder names the methods used."}
# "Related" at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/about/publications/"}
---
**Cite the Lead-DBS v3 paper** in every study that used Lead-DBS.
{.dataset-intro}

{{% copybox label="Copy the citation" %}}
{{< paper neudorfer2023 "full" >}}
{{% /copybox %}}

RRID: [SCR_002915](https://scicrunch.org/scicrunch/Resources/record/nlx_144509-1/5f2345e7-4b61-51f4-8d44-4b9b8cdf8868/search?q=lead%20dbs&l=lead%20dbs) · Lead-DBS v2 or earlier: {{< paper horn2019 >}} and {{< paper horn2015 >}}
{.fine-print}

## Also cite {#also-cite}

{{< cells key="also" label="Also cite" >}}

## A methods paragraph to adapt {#methods-snippet}

{{% copybox label="Copy the paragraph" %}}
DBS electrodes were localized with the processing pipeline [*(Horn & Li et al. 2019)*](https://doi.org/10.1016/j.neuroimage.2018.08.068) of Lead-DBS v3 ([lead-dbs.org](/); [*Neudorfer et al. 2023*](https://doi.org/10.1016/j.neuroimage.2023.119862); [*Horn & Kühn 2015*](https://doi.org/10.1016/j.neuroimage.2014.12.002); RRID:SCR_002915). Postoperative CT or MRI were linearly coregistered to preoperative MRI with advanced normalization tools (ANTs; [stnava.github.io/ANTs/](http://stnava.github.io/ANTs/); [*Avants et al. 2011*](https://doi.org/10.1016/j.neuroimage.2010.09.025)), inspected and refined if needed, and corrected for brain shift as implemented in Lead-DBS. All preoperative volumes were used for a multispectral normalization to ICBM 2009b NLIN asymmetric (“MNI”) space [*(Fonov et al. 2009)*](https://doi.org/10.1016/S1053-8119(09)70884-5) with the ANTs SyN Diffeomorphic Mapping [*(Avants et al. 2008)*](https://doi.org/10.1016/j.media.2007.06.004), preset “effective: low variance default + subcortical refinement”; where it failed, with the multispectral Unified Segmentation [*(Ashburner et al. 2005)*](https://doi.org/10.1016/j.neuroimage.2005.02.018) of SPM12 ([fil.ion.ucl.ac.uk/spm](https://www.fil.ion.ucl.ac.uk/spm); [*Friston et al. 1994*](https://doi.org/10.1002/hbm.460020402)). Both presets of Lead-DBS segmented the STN about as precisely as manual experts in a comparative study [*(Ewert et al. 2019)*](https://doi.org/10.1016/j.neuroimage.2018.09.061). Contacts were pre-reconstructed with PaCER [*(Husch et al. 2018)*](https://doi.org/10.1016/j.nicl.2017.10.004) or TRAC/CORE and refined manually if needed. The orientation of segmented leads was estimated with DiODe [*(Dembek et al. 2019)*](https://doi.org/10.1016/j.parkreldis.2019.08.017). Atlas structures are from the DISTAL atlas [*(Ewert et al. 2018)*](https://doi.org/10.1016/j.neuroimage.2017.05.015); group visualizations were made with Lead Group [*(Treu et al. 2020)*](https://doi.org/10.1016/j.neuroimage.2020.117018).
{{% /copybox %}}
