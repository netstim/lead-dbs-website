---
title: "List of Lead-DBS dependencies"
date: "2016-06-13T16:26:54"
lastmod: "2022-03-16T14:45:31"
weight: 6
---

The list below is giving credit to various open source software libraries or packages that are used within Lead-DBS. If you use Lead-DBS for your research, please cite the according libraries that you use properly.

##### About dependencies

*Lead-DBS* can be seen as a collection of useful tools that have been gathered together for the purpose of DBS electrode reconstructions and related processing. The core job of our development team is to find and plug in the best neuroimaging tools available within the open-source community and write bits of pieces of own code where no good code can be found. 3D-visualizations and electrode reconstruction algorithms ([TRAC/CORE](http://www.sciencedirect.com/science/article/pii/S1053811914009938)) have been built by ourselves. As for other parts of the toolbox, we aim at incorporating the best tools available. For instance, normalizations into MNI space can be done from within *Lead-DBS* by either [DARTEL](http://www.fil.ion.ucl.ac.uk/spm/software/spm12/) or [ANTs](http://stnava.github.io/ANTs/), both of which have shown superior to all 12 competing algorithms in [Klein 2009](http://www.ncbi.nlm.nih.gov/pubmed/19195496). As for Fibertracking, *Lead-DBS* among other routines uses the [Gibbs’ tracking algorithm](https://www.uniklinik-freiburg.de/mr-en/research-groups/diffperf/fibertools.html), which showed superior to all 9 competing algorithms in [Fillard 2011](http://www.ncbi.nlm.nih.gov/pubmed/21256221). Thus, *Lead-DBS* heavily depends on shared libraries and other tools that should be referenced properly if used for research projects.

| Part of processing pipeline of Lead-DBS in which the software is used | Software name | Reference Link | Publication / Author |
| --- | --- | --- | --- |
| Appearance | Icons in the GUI | http://bit.ly/1il2Itw | Icons in the GUI are generated using the fontawesome typography |
| Visualization / Figure Export | Myaa – My Anti-Alias for Matlab | http://bit.ly/1UqerKY | Anders Brun |
|  | Create Video of Rotating 3D Plot | http://bit.ly/24LSOWW | Alan Jennings |
| General file handling | Tools for NIfTI and ANALYZE image | http://bit.ly/1ULDxTb | Jimmy Shen |
|  | stlwrite() | http://bit.ly/1UUapt0 | Sven (ML Fileexchange user) |
|  | patch2ply | http://bit.ly/29vPLBf | J. Xiao, 2013. Princeton Vision and Robotics Toolkit. Available from: http://bit.ly/29vPLBf |
| DICOM import | dcm2nii | http://bit.ly/1U44FKF | Chris Rorden |
| Normalization into MNI space based on preoperative MR images | SPM12 / DARTEL / New Segment | http://bit.ly/1YlReLe | A manifold of them. E.g. see Ashburner, J. (2007). A fast diffeomorphic image registration algorithm, 38(1), 95–113. http://bit.ly/1WLv85y  Ashburner, J. (2012). SPM: a history. |
|  | Advanced Normalization Tools (ANTs) / SyN Registration | http://bit.ly/21i5B2v | Avants, B. B., Epstein, C. L., Grossman, M., & Gee, J. C. (2008). Symmetric diffeomorphic image registration with cross-correlation: evaluating automated labeling of elderly and neurodegenerative brain. Medical Image Analysis, 12(1), 26–41. http://bit.ly/1YnjEov  Avants, B. B., Tustison, N. J., Song, G., Cook, P. A., Klein, A., & Gee, J. C. (2011). A reproducible evaluation of ANTs similarity metric performance in brain image registration. NeuroImage, 54(3), 2033–2044. http://bit.ly/1YlRY2T  Zhang, H., Avants, B. B., Yushkevich, P. A., Woo, J. H., Wang, S., McCluskey, L. F., et al. (2007). High-dimensional spatial normalization of diffusion tensor images improves the detection of white matter differences: an example study using amyotrophic lateral sclerosis. IEEE Transactions on Medical Imaging, 26(11), 1585–1597. http://bit.ly/25Tbbio |
|  | BRAINSFit registration | http://bit.ly/1UNSukA |  |
| Rangesearching / DTI / VAT-Connectivity | Fast Range Search through JIT (ver 2) | http://bit.ly/1tmbSPE | Yi Cao |
|  | Inhull | http://bit.ly/1VUWIwi | John D’Errico |
|  | Intriangulation – which points are inside a 3d watertight triangulation? | http://bit.ly/1ULDIxC | Johannes Korsawe |
| dMRI (“DTI”) processing & fiber tracking | Unring – tool for removal of the Gibbs ringing artefact | http://bit.ly/1ULDGFX | http://bit.ly/1U43HOO |
|  | Gibbstracker / DTI & Fibertools for SPM | http://bit.ly/1U448IK | Reisert, M., Mader, I., Anastasopoulos, C., Weigel, M., Schnell, S., & Kiselev, V. (2011). Global fiber reconstruction becomes practical., 54(2), 955–962. http://bit.ly/1U44teA |
|  | Mesotracker / MesoFT | http://bit.ly/1Ynjcqm | Reisert, M., Kiselev, V. G., Dihtal, B., Kellner, E., & Novikov, D. S. (2014). MesoFT: Unifying Diffusion Modelling and Fiber Tracking. In Medical Image Computing and Computer-Assisted Intervention – MICCAI 2014 (Vol. 8675, pp. 201–208). Cham: Springer International Publishing. http://bit.ly/1XS5UDt |
|  | DSI Studio / Generalized Q-Ball Imaging (GQI) | http://bit.ly/25TaPs5 | Yeh, F.-C., Wedeen, V. J., & Tseng, W.-Y. I. (2010). Generalized q-Sampling Imaging. IEEE Transactions on Medical Imaging, 29(9), 1626–1635. http://bit.ly/1rlFJ9r |
|  | Classical Tensor-Based DTI-Tractography | http://bit.ly/1PoN5zd | Dirk-Jan Kroon |
|  | trk_read.m and trk_write.m (Part of along tract stats) | http://bit.ly/1tmbIrs | John Colby |
| fMRI processing | Resting-State fMRI Data Analysis Toolkit  (used for band-pass filtering) | http://bit.ly/290ThiS | Song, X.-W., Dong, Z.-Y., Long, X.-Y., Li, S.-F., Zuo, X.-N., Zhu, C.-Z., et al. (2011). REST: A Toolkit for Resting-State Functional Magnetic Resonance Imaging Data Processing. PLoS ONE, 6(9), e25031. http://bit.ly/290T2on |
| Coordinate transposition | map_coords.m, resize_img.m |  | Ged Ridgway |
| Normalizing Values / Generalized Linear Modeling | normal.m | http://bit.ly/1PXp87A | van Albada, S. J., & Robinson, P. A. (2007). Transformation of arbitrary distributions to the normal distribution with application to EEG test-retest reliability. Journal of Neuroscience Methods, 161(2), 205–211. http://bit.ly/1ZL2u2o |
| Estimating the Volume of Activated Tissue (VAT) | SimBio (FEM-based field modeling) and FieldTrip (Mesh generation) toolboxes | http://bit.ly/1rlJaNi  http://bit.ly/1UNVLjT | Oostenveld, R., Fries, P., Maris, E., & Schoffelen, J.-M. (2010). FieldTrip: Open Source Software for Advanced Analysis of MEG, EEG, and Invasive Electrophysiological Data. Computational Intelligence and Neuroscience, 2011(1), 1–9. http://bit.ly/1rlJeN2  Wolters, C. H., Anwander, A., & Tricoche, X. (2005). Influence of local and remote white matter conductivity anisotropy for a thalamic source on EEG/MEG field and return current computation. |
| Network stats | Network based statistics (NBS) | http://bit.ly/1UUbrVF  http://bit.ly/1tvbPRD | Zalesky, A., Fornito, A., & Bullmore, E. T. (2010). Network-based statistic: identifying differences in brain networks., 53(4), 1197–1207. http://bit.ly/1UoLPAq |
