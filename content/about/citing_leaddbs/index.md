---
title: "Citing Lead-DBS"
date: "2020-02-13T06:03:01"
lastmod: "2022-03-16T14:45:12"
weight: 4
---

## Citing LEAD-DBS
If you use the toolbox for research purposes, please cite the following publication:

- [Andreas Horn, Andrea Kühn. Lead-DBS: A toolbox for deep brain stimulation electrode localizations and visualizations. NeuroImage, 2014.](http://www.sciencedirect.com/science/article/pii/S1053811914009938)
- A SciRes-ID for the toolbox can be supplied additionally and is as follows: [SciRes_000188](https://scicrunch.org/scicrunch/Resources/record/nlx_144509-1/5f2345e7-4b61-51f4-8d44-4b9b8cdf8868/search?q=lead%20dbs&l=lead%20dbs) / [SCR_002915](https://scicrunch.org/scicrunch/Resources/record/nlx_144509-1/5f2345e7-4b61-51f4-8d44-4b9b8cdf8868/search?q=lead%20dbs&l=lead%20dbs)

Alternatively or additionally, you could cite the paper about the updated pipeline, Lead-DBS v2:

- [Horn, A., Li, N., Dembek, T. A., Kappel, A., Boulay, C., Ewert, S., et al. (2018). Lead-DBS v2: Towards a comprehensive pipeline for deep brain stimulation imaging. NeuroImage.](http://doi.org/10.1016/j.neuroimage.2018.08.068)

It is also crucial to think about which other work (such as coregistration, normalization or electrode reconstruction methods) you used and which of them to cite. Please look at the “ea_methods.txt” files inside your patient folders to get some inspiration.

A specific citation for use of Lead group is this one:

- [Treu, S., Strange, B., Oxenford, S., Kuehn, A., & Horn, A. (2020). Deep Brain Stimulation: Imaging on a group level, 142, 3086.](http://doi.org/10.1101/2020.01.14.904615)

Please also make sure to cite [subcortical atlases](/helpsupport/knowledge-base/atlasesresources/atlases-2/ "Atlases") and [brain parcellations](/helpsupport/knowledge-base/atlasesresources/cortical-atlas-parcellations-mni-space/) that you use with LEAD-DBS.

Lead-DBS depends on a lot of shared libraries, a [list can be found here](/about/lead-dbs-dependencies/). Depending on your specific analysis, please cite the core contributors to it accordingly following general rules of good scientific practice. This is important to assure your work is reproducible to others.

**Find an example snippet that we used and could be adapted for your methods section here:**

> DBS electrodes were localized using the advanced processing pipeline [*(Horn & Li et al. 2018)*](http://doi.org/10.1016/j.neuroimage.2018.08.068) in Lead-DBS ([lead-dbs.org](/); *[Horn & Kühn. 2017](http://doi.org/10.1016/j.neuroimage.2014.12.002);* RRID:SCR_002915). In short, postoperative CT or MRI were linearly coregistered to preoperative MRI using advanced normalization tools (ANTs; [stnava.github.io/ANTs/](http://stnava.github.io/ANTs/); [*Avants et al. 2011*](http://doi.org/10.1016/j.neuroimage.2010.09.025)). Coregistrations were inspected and refined if needed. A brain shift correction step was applied as implemented in Lead-DBS. All preoperative volumes were used to estimate a precise multispectral normalization to ICBM 2009b NLIN asymmetric (“MNI”) space [*(Fonov et al. 2009)*](https://www.sciencedirect.com/science/article/abs/pii/S1053811910010062?via%3Dihub) applying the ANTs SyN Diffeomorphic Mapping *[*(Avants et al. 2008)*](http://doi.org/10.1016/j.media.2007.06.004)*using the preset “effective: low variance default + subcortical refinement”. In some patients where this strategy failed, a multispectral implementation of the Unified Segmentation approach [*(Ashburner et al. 2005)*](http://doi.org/10.1016/j.neuroimage.2005.02.018) implemented in Statistical Parametric Mapping software (SPM12; [fil.ion.ucl.ac.uk/spm](https://www.fil.ion.ucl.ac.uk/spm); [*Friston et al. 2004*](http://doi.org/10.1002/hbm.460020402)) was applied. These two methods are available as presets in Lead-DBS and were top-performers to segment the STN with precision comparable to manual expert segmentations in a recent comparative study [*(Ewert et al. 2018)*](http://doi.org/10.1016/j.neuroimage.2018.09.061). DBS contacts were automatically pre-reconstructed using the phantom-validated and fully-automated PaCER method [*(Husch et al. 2017)*](http://doi.org/10.1016/j.nicl.2017.10.004) or the TRAC/CORE approach and manually refined if needed. For segmented leads, the orientation of electrode segments was reconstructed using the Directional Orientation Detection (DiODe) algorithm [*(Dembek et al. 2019)*](http://doi.org/10.1016/j.parkreldis.2019.08.017). Atlas segmentations in this manuscript are defined by the DISTAL atlas [*(Ewert et al. 2017)*](http://doi.org/10.1016/j.neuroimage.2017.05.015). Group visualizations were performed using the Lead group toolbox [*(Treu et al. 2020)*](http://doi.org/10.1101/2020.01.14.904615).
