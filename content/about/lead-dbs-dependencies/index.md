---
title: "Lead-DBS dependencies"
# the browser title (head.html adds " – Lead-DBS")
htmlTitle: "Dependencies"
description: "The open-source tools Lead-DBS builds on, from SPM and ANTs to OSS-DBS v1 and v2, and the papers to cite for them."
date: "2016-06-13T16:26:54"
lastmod: "2026-11-11"
weight: 7
menuParent: "/about/citing_leaddbs"
# the old "portfolio" of software Lead-DBS works with
aliases: ["/portfolio-item/spm/", "/portfolio-item/dtifibertools/", "/portfolio-item/132/", "/portfolio_entries/interfaces/"]
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - "/develop/"
  - {name: "OSS-DBS in Lead-DBS", url: "/helpsupport/knowledge-base/lead-dbs-methods/#oss-dbs"}
  - "/about/publications/"
# the picture shown when the page is shared (head.html)
share: "images/renders/head-about.jpg"
---

Lead-DBS brings together some of the best open-source neuroimaging tools and adds code of its own
where none existed. **If you use Lead-DBS in a study, please cite the tools you used**, along with
[Lead-DBS itself](/about/citing_leaddbs/).

## Why these tools

- **Written for Lead-DBS**: the 3D visualization and the electrode reconstruction algorithms
  ([TRAC/CORE](http://www.sciencedirect.com/science/article/pii/S1053811914009938)).
- **Normalization into MNI space**: [DARTEL](https://www.fil.ion.ucl.ac.uk/spm/software/spm12/) or
  [ANTs](http://stnava.github.io/ANTs/), both of which outperformed all 12 other algorithms in
  [Klein 2009](http://www.ncbi.nlm.nih.gov/pubmed/19195496).
- **Fibre tracking**, among other routines: the
  [Gibbs' tracking algorithm](https://www.uniklinik-freiburg.de/mr-en/research-groups/diffperf/fibertools.html),
  which outperformed all 9 other algorithms in [Fillard 2011](http://www.ncbi.nlm.nih.gov/pubmed/21256221).
- **Stimulation modelling**: [OSS-DBS](#stimulation-modelling-oss-dbs), integrated in its version 2 since Lead-DBS 3.1.

## Stimulation modelling: OSS-DBS {#stimulation-modelling-oss-dbs}

OSS-DBS computes the electric field around the electrode with heterogeneous, anisotropic and
dispersive volume conductor models, and from the field the activation of pathways with biophysical
axon models. It is developed around the team of Ursula van Rienen at the University of Rostock.
Version 2 installs automatically with Lead-DBS 3.1 and later. Please cite both papers, on version 2
and on the original method (in the table below).

## All tools and their papers

| Used for | Software | Link | Publication or author |
| --- | --- | --- | --- |
| Appearance | Icons in the GUI | [fontawesome.io](http://fontawesome.io/) | Icons in the GUI are generated using the fontawesome typography |
| Visualization / Figure Export | Myaa – My Anti-Alias for Matlab | [mathworks.com](http://www.mathworks.com/matlabcentral/fileexchange/20979-myaa-my-anti-alias-for-matlab) | Anders Brun |
|  | Create Video of Rotating 3D Plot | [mathworks.com](http://www.mathworks.com/matlabcentral/fileexchange/41093-create-video-of-rotating-3d-plot/content/CaptureFigVid/CaptureFigVid.m) | Alan Jennings |
| General file handling | Tools for NIfTI and ANALYZE image | [mathworks.com](http://www.mathworks.com/matlabcentral/fileexchange/8797-tools-for-nifti-and-analyze-image) | Jimmy Shen |
|  | stlwrite() | [mathworks.com](https://www.mathworks.com/matlabcentral/fileexchange/20922-stlwrite-filename--varargin-) | Sven (ML Fileexchange user) |
|  | patch2ply | [robots.princeton.edu](http://robots.princeton.edu/code.html) | J. Xiao, 2013. Princeton Vision and Robotics Toolkit. Available from: [robots.princeton.edu](http://robots.princeton.edu/code.html) |
| DICOM import | dcm2nii | [nitrc.org](https://www.nitrc.org/projects/dcm2nii/) | Chris Rorden |
| Normalization into MNI space based on preoperative MR images | SPM12 / DARTEL / New Segment | [fil.ion.ucl.ac.uk](http://www.fil.ion.ucl.ac.uk/spm/software/spm12/) | Several papers, for example Ashburner, J. (2007). A fast diffeomorphic image registration algorithm, 38(1), 95–113. [doi:10.1016/j.neuroimage.2007.07.007](https://doi.org/10.1016/j.neuroimage.2007.07.007)  Ashburner, J. (2012). SPM: a history. |
|  | Advanced Normalization Tools (ANTs) / SyN Registration | [stnava.github.io](http://stnava.github.io/ANTs/) | Avants, B. B., Epstein, C. L., Grossman, M., & Gee, J. C. (2008). Symmetric diffeomorphic image registration with cross-correlation: evaluating automated labeling of elderly and neurodegenerative brain. Medical Image Analysis, 12(1), 26–41. [doi:10.1016/j.media.2007.06.004](https://doi.org/10.1016/j.media.2007.06.004)  Avants, B. B., Tustison, N. J., Song, G., Cook, P. A., Klein, A., & Gee, J. C. (2011). A reproducible evaluation of ANTs similarity metric performance in brain image registration. NeuroImage, 54(3), 2033–2044. [doi:10.1016/j.neuroimage.2010.09.025](https://doi.org/10.1016/j.neuroimage.2010.09.025)  Zhang, H., Avants, B. B., Yushkevich, P. A., Woo, J. H., Wang, S., McCluskey, L. F., et al. (2007). High-dimensional spatial normalization of diffusion tensor images improves the detection of white matter differences: an example study using amyotrophic lateral sclerosis. IEEE Transactions on Medical Imaging, 26(11), 1585–1597. [doi:10.1109/TMI.2007.906784](https://doi.org/10.1109/TMI.2007.906784) |
|  | BRAINSFit registration | [nitrc.org](https://www.nitrc.org/projects/multimodereg/) |  |
| Rangesearching / DTI / VAT-Connectivity | Fast Range Search through JIT (ver 2) | [mathworks.com](https://www.mathworks.com/matlabcentral/fileexchange/19480-fast-range-search-through-jit--ver-2-) | Yi Cao |
|  | Inhull | [mathworks.com](http://www.mathworks.com/matlabcentral/fileexchange/10226-inhull) | John D’Errico |
|  | Intriangulation – which points are inside a 3d watertight triangulation? | [mathworks.com](http://www.mathworks.com/matlabcentral/fileexchange/43381-intriangulation-which-points-are-inside-a-3d-watertight-triangulation-) | Johannes Korsawe |
| dMRI (“DTI”) processing & fiber tracking | Unring – tool for removal of the Gibbs ringing artefact | [bitbucket.org](https://bitbucket.org/reisert/unring) | [onlinelibrary.wiley.com](http://onlinelibrary.wiley.com/doi/10.1002/mrm.26054/abstract) |
|  | Gibbstracker / DTI & Fibertools for SPM | [uniklinik-freiburg.de](https://www.uniklinik-freiburg.de/mr-en/research-groups/diffperf/fibertools.html) | Reisert, M., Mader, I., Anastasopoulos, C., Weigel, M., Schnell, S., & Kiselev, V. (2011). Global fiber reconstruction becomes practical., 54(2), 955–962. [doi:10.1016/j.neuroimage.2010.09.016](https://doi.org/10.1016/j.neuroimage.2010.09.016) |
|  | Mesotracker / MesoFT | [bitbucket.org](https://bitbucket.org/reisert/mesoft_v1) | Reisert, M., Kiselev, V. G., Dihtal, B., Kellner, E., & Novikov, D. S. (2014). MesoFT: Unifying Diffusion Modelling and Fiber Tracking. In Medical Image Computing and Computer-Assisted Intervention – MICCAI 2014 (Vol. 8675, pp. 201–208). Cham: Springer International Publishing. [doi:10.1007/978-3-319-10443-0_26](https://doi.org/10.1007/978-3-319-10443-0_26) |
|  | DSI Studio / Generalized Q-Ball Imaging (GQI) | [dsi-studio.labsolver.org](http://dsi-studio.labsolver.org/) | Yeh, F.-C., Wedeen, V. J., & Tseng, W.-Y. I. (2010). Generalized q-Sampling Imaging. IEEE Transactions on Medical Imaging, 29(9), 1626–1635. [doi:10.1109/TMI.2010.2045126](https://doi.org/10.1109/TMI.2010.2045126) |
|  | Classical Tensor-Based DTI-Tractography | [mathworks.com](http://www.mathworks.com/matlabcentral/fileexchange/21130-dti-and-fiber-tracking) | Dirk-Jan Kroon |
|  | trk_read.m and trk_write.m (Part of along tract stats) | [github.com](https://github.com/johncolby/along-tract-stats) | John Colby |
| fMRI processing | Resting-State fMRI Data Analysis Toolkit  (used for band-pass filtering) | [restfmri.net](http://restfmri.net/forum/index.php?q=rest) | Song, X.-W., Dong, Z.-Y., Long, X.-Y., Li, S.-F., Zuo, X.-N., Zhu, C.-Z., et al. (2011). REST: A Toolkit for Resting-State Functional Magnetic Resonance Imaging Data Processing. PLoS ONE, 6(9), e25031. [doi:10.1371/journal.pone.0025031](https://doi.org/10.1371/journal.pone.0025031) |
| Coordinate transposition | map_coords.m, resize_img.m |  | Ged Ridgway |
| Normalizing Values / Generalized Linear Modeling | normal.m | [scholar.google.com](https://scholar.google.com/citations?user=pdpt9EMAAAAJ) | van Albada, S. J., & Robinson, P. A. (2007). Transformation of arbitrary distributions to the normal distribution with application to EEG test-retest reliability. Journal of Neuroscience Methods, 161(2), 205–211. [doi:10.1016/j.jneumeth.2006.11.004](https://doi.org/10.1016/j.jneumeth.2006.11.004) |
| Stimulation modelling: electric field, volume of tissue activated, pathway activation (Lead-DBS 3.1 and later) | OSS-DBS v2 | [github.com/SFB-ELAINE/OSS-DBSv2](https://github.com/SFB-ELAINE/OSS-DBSv2) | {{< paper zimmermann2026 "full" >}} |
|  | OSS-DBS (v1) | [github.com/SFB-ELAINE/OSS-DBS](https://github.com/SFB-ELAINE/OSS-DBS) | {{< paper butenko2020 "full" >}} |
| Estimating the Volume of Activated Tissue (VAT) | SimBio (FEM-based field modeling) and FieldTrip (Mesh generation) toolboxes | [fieldtriptoolbox.org](http://fieldtriptoolbox.org/)  [mrt.uni-jena.de](https://www.mrt.uni-jena.de/simbio/index.php/Main_Page) | Oostenveld, R., Fries, P., Maris, E., & Schoffelen, J.-M. (2010). FieldTrip: Open Source Software for Advanced Analysis of MEG, EEG, and Invasive Electrophysiological Data. Computational Intelligence and Neuroscience, 2011(1), 1–9. [doi:10.1155/2011/156869](https://doi.org/10.1155/2011/156869)  Wolters, C. H., Anwander, A., & Tricoche, X. (2005). Influence of local and remote white matter conductivity anisotropy for a thalamic source on EEG/MEG field and return current computation. |
| Network stats | Network based statistics (NBS) | [sites.google.com](https://sites.google.com/site/bctnet/comparison/nbs)  [nitrc.org](https://www.nitrc.org/projects/nbs/) | Zalesky, A., Fornito, A., & Bullmore, E. T. (2010). Network-based statistic: identifying differences in brain networks., 53(4), 1197–1207. [doi:10.1016/j.neuroimage.2010.06.041](https://doi.org/10.1016/j.neuroimage.2010.06.041) |
{.table--stack caption="Software that Lead-DBS uses, with its papers"}

## Next

How to cite Lead-DBS itself is on [Cite Lead-DBS](/about/citing_leaddbs/); how to get your own code or data into Lead-DBS is on [Develop Lead-DBS](/develop/#add-your-atlas-or-dataset).
