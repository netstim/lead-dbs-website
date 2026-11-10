---
title: "Data & Code inclusion philosophy"
date: "2020-04-10T08:24:14"
lastmod: "2022-03-16T14:45:26"
weight: 5
---

## Data & Code inclusion philosophy

  

In comparison to commercial software [with similar purpose](/about/), we see Lead-DBS as purely academic research software which should fulfill [different criteria](/commercial-vs-academic-software/).

In brief, we see Lead-DBS as a tool that should be

- as inclusive as possible
- as open and transparent as possible
- widely driven by any member of our research community that wants to contribute
  

### Code
For instance, we believe that any user of Lead-DBS that feels a certain feature is missing should be allowed to include this feature her/himself. If features that people need to pursue their research would change the overall purpose of Lead-DBS too dramatically, these could be incorporated in forks of the code-repository.

Still, if anyhow possible, we welcome inclusion of any code that adds a useful feature to Lead-DBS.

  

### Data (e.g. atlases)
Similarly, we aim at including any atlas or dataset that could become helpful for analyses in the general arena of Lead-DBS. For instance, with atlases, these could be derived from any source of information (MRI, histology, connectivity, drawings, synthesized maps, etc.).

  

### The downside
While this open policy will certainly sound friendly, it also comes with downsides & caveats. For instance, (published) atlases that are of poor quality could be included into Lead-DBS. We are a small team and only able to carry out a certain amount of quality control. Moreover, if atlases result from published studies, we see justification for including these in reproducibility purposes, alone. Similar concepts apply to code. We try our best to make code “citable” by referring to the first publication in which a certain feature was used, within our GUI. For instance, the probabilistic AC/PC to MNI conversion routine implemented in Lead-DBS refers to [Horn et al. 2017 NeuroImage](https://www.ncbi.nlm.nih.gov/pubmed/28163141) where the method is described. However, since our development is swift and constant, this is not always possible. New features that have not been used in publications often find their way into Lead-DBS and only later, a first study uses them.

  

### What does this mean for me as a user?
The above has consequences for you in case you use Lead-DBS or included datasets. In brief, they defer to you the responsibility of knowing what you are doing and knowing the origins & limitations of datasets you use, in detail. If you are uncertain about data or code, please don’t blindly use or apply them. Instead, [read up the papers](/about/publications/) that led to those assets and/or [contact the helpline](/helpsupport/) if in doubt.

We try our best to help users in understanding what Lead-DBS does in each step. However, again, we are a small team and our capacities are limited. Moreover, we are researchers ourselves, not software-developers. In our view, Lead-DBS is not much more than code that we use and build for ourselves that is shared with the community for i) reproducibility and transparency reasons and ii) to avoid unnecessary double work funded by the public.

Thus, please see Lead-DBS and included data as “unapproved” assets that you may either find helpful, or not. Inclusion of datasets or code does not mean that these are “foolproof” and may be applied carelessly to any scientific question that should emerge. Some of the code is quite complex and from the outside, it is sometimes not easy to exactly understand what the code does with the data. Thus, please constantly ask yourself: Do I really understand what is happening here? If not, [please ask](/helpsupport/).

  

### Some examples that could lead to problems
*Please find some example scenarios below that could lead to problems. These arise from the inclusive nature of Lead-DBS and may underline that you – as a user – have the responsibility to understand what you are doing.*

  

#### Atlases not “made for Lead-DBS”
By default, Lead-DBS works inside the [ICBM 2009b nonlinear asymmetric space (Fonov 2009)](http://nist.mni.mcgill.ca/?p=904). This is one of the most modern versions of the MNI space, but it is one specific version that is [slightly different from other versions](/about-the-mni-spaces/). This means that if you normalize your patient data into MNI space with Lead-DBS, it will be warped to these templates ([2009b Asym section](http://nist.mni.mcgill.ca/?p=904)). Instead, some published MNI atlases were created with FSL or SPM which use [older or alternative versions of the MNI space](/about-the-mni-spaces/). For instance, the [ATAG atlas](https://www.nitrc.org/projects/atag/) was created using [FSL’s FNIRT](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FNIRT/UserGuide) routine e.g. to show [age-dependent probabilistic deviations of the subthalamic nucleus](https://www.ncbi.nlm.nih.gov/pubmed/23486960). Hence, it would be best applicable if you also use FNIRT to normalize patient data AND use the [MNI 6th-generation nonlinear template](http://nist.mni.mcgill.ca/?p=858) that was used by the authors and is the default in FSL. Both is possible within Lead-DBS but neither of the two options are defaults for [good reasons](https://www.sciencedirect.com/science/article/pii/S1053811918318664).

This is confusing, we know. But if in doubt, solutions are simple:

- The DISTAL and Human Motor Thalamus Atlases were created for Lead-DBS and are inside the correct space. Use such atlases that were “made for Lead-DBS” if in doubt.
- If you need to use a particular atlas, read the original publication that led to its creation. [Read this page](/about-the-mni-spaces/) for more information about the MNI space.
- As always in scientific work: Be critical about results. Confirm them with control analyses and/or using different analyses pathways that may include different atlases or assets.
  

#### Connectomes not made for the analyses you have in mind
Lead-DBS comes with some normative connectomes that could be used to estimate relationships between e.g. clinical outcome following DBS and structural connectivity seeding from electrodes.

While these assets bear great potential and are even more or less easy to use, the underlying concepts are quite complex. Unfortunately, results from these analyses are easy to misinterpret. Before starting “connectomic-DBS” analyses, maybe you should ask yourself the following questions:

**When using a structural connectome**

- Do you understand how these datasets were made?
- How does diffusion MRI work and how does tractography work.
- What are the different concepts that exist?
- How patient-specific (or unspecific) would these results be (answer: absolutely unspecific)?
- Who acquired the underlying data?
- Which scanners were used, which parameters?
- What could be special about the applied MRI hardware?
- Who processed the connectomes and how were they aggregated into template space?
- What are the limitations of these approaches?
- Is the way these data were processed even the best approach for my analysis?
- Tractography data is extremely [susceptible to false-positive connections](https://www.nature.com/articles/s41467-017-01285-x) and will [not be able to resolve small subcortical bundles](https://www.sciencedirect.com/science/article/abs/pii/S0896627319308323). Is this important for my analysis?

*If answers to these and similar questions are not clear to you, we believe that you should not yet apply a structural connectome but instead learn a bit more about diffusion MRI & tractography. There are great resources available to do so – just google.*

**When using a functional connectome**

- Do you understand how these datasets were made?
- How does functional MRI work and why are subjects scanned at rest.
- What is the difference between task- and resting-state fMRI and what could this imply for these connectomes?
- What is the BOLD signal and how should we interpret it?
- How is connectivity calculated between brain regions? Would there be other or better ways to do so (probably)? If so, why do we use this method within the community (convention)?
- What would it mean if functional connectivity is calculated voxel-wise and does it matter to what I am doing?
- How patient-specific (or unspecific) would these results be (answer: absolutely unspecific)?
- Who acquired the underlying data?
- Which scanners were used, which parameters?
- What could be special about the applied MRI hardware?
- Who processed the connectomes and how were they aggregated into template space?
- Is the way these data were processed even the best approach for my analysis?
- What are the limitations of these approaches?
- Functional MRI data is an extremely derived method and does not directly measure neural activity. Connectivity estimates [include a high number of indirect connections](https://www.ncbi.nlm.nih.gov/pubmed/23583357) and are not available for faster signals (as could be estimated using MER, EcOG, LFP, EEG or MEG). Is this important for my analysis? Is fMRI even the best method to answer my question?

*If answers to these and similar questions are not clear to you, we believe that you should not yet apply a functional connectome but instead learn a bit more about functional MRI & related preprocessing. There are great resources available to do so – just google.*
