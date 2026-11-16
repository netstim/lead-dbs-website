---
title: "Cite Lead-DBS"
description: "Which papers to cite when you use Lead-DBS, and a methods template to adapt."
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

{{< paper neudorfer2023 "full" >}}

RRID: [SCR_002915](https://scicrunch.org/scicrunch/Resources/record/nlx_144509-1/5f2345e7-4b61-51f4-8d44-4b9b8cdf8868/search?q=lead%20dbs&l=lead%20dbs) · Lead-DBS v2 or earlier: {{< paper horn2019 >}} and {{< paper horn2015 >}}
{.fine-print}

## Also cite {#also-cite}

{{< cells key="also" label="Also cite" >}}

## Report the methods you used {#methods-snippet}

Start with `ea_methods.txt` in each patient folder. Check the software version, registration settings, reconstruction method and atlases before adding this text to your paper.

{{% copybox label="Copy the template" %}}
DBS electrodes were localized with Lead-DBS [version] ([*Neudorfer et al. 2023*](https://doi.org/10.1016/j.neuroimage.2023.119862); RRID:SCR_002915). Postoperative [CT/MRI] was coregistered to preoperative MRI using [method and settings]. [Describe brain shift correction, normalization and manual checks used in this study.] Electrodes were reconstructed using [method] and checked manually. [Add the stimulation model, atlas, connectivity and group-analysis methods used, with their citations.]
{{% /copybox %}}

<details class="more"><summary>Papers for common methods</summary>

- Processing pipeline: [Horn & Li et al. 2019](https://doi.org/10.1016/j.neuroimage.2018.08.068); Lead-DBS v1: [Horn & Kühn 2015](https://doi.org/10.1016/j.neuroimage.2014.12.002)
- Coregistration with ANTs: [Avants et al. 2011](https://doi.org/10.1016/j.neuroimage.2010.09.025); SyN normalization: [Avants et al. 2008](https://doi.org/10.1016/j.media.2007.06.004)
- Unified Segmentation in SPM12: [Ashburner et al. 2005](https://doi.org/10.1016/j.neuroimage.2005.02.018); SPM: [Friston et al. 1994](https://doi.org/10.1002/hbm.460020402)
- ICBM 2009b NLIN asymmetric (“MNI”) space: [Fonov et al. 2009](https://doi.org/10.1016/S1053-8119(09)70884-5)
- Normalization accuracy for the STN: [Ewert et al. 2019](https://doi.org/10.1016/j.neuroimage.2018.09.061)
- PaCER reconstruction: [Husch et al. 2018](https://doi.org/10.1016/j.nicl.2017.10.004)
- DiODe orientation of directional leads: [Dembek et al. 2019](https://doi.org/10.1016/j.parkreldis.2019.08.017)
- DISTAL atlas: [Ewert et al. 2018](https://doi.org/10.1016/j.neuroimage.2017.05.015)
- Lead Group: [Treu et al. 2020](https://doi.org/10.1016/j.neuroimage.2020.117018)

</details>
