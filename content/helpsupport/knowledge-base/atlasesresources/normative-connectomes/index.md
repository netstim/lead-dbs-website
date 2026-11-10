---
title: "Normative Connectomes"
date: "2017-12-29T11:56:26"
lastmod: "2025-08-07T10:11:51"
weight: 4
---

# Normative Connectomes

Since 2014, we worked on estimating “**average wiring diagrams**” of the human brain. Based on diffusion-weighted or resting-state functional MRI data of large cohorts of subjects/patients, this line of work focused on running whole-brain tractography or functional connectivity analyses, warping individual connectomes into standard space and then **averaging the results** across the group of subjects.

In **2014**, we published a [first article](https://doi.org/10.1016/j.neuroimage.2013.09.069) under the lead of [Felix Blankenburg](https://scholar.google.de/citations?user=-QOB8EoAAAAJ) describing the effort of a **first structural-functional MNI connectome**. There is a small [additional article](https://doi.org/10.1016/j.dib.2015.08.035) associated with the data release of this first connectome. In **2016**, we [**replicated results**](https://doi.org/10.1016/j.neuroimage.2015.08.048) based on a much larger cohort of healthy subjects and [**validated**](https://doi.org/10.1016/j.neuroimage.2015.08.048) the use of such normative connectomes by replicating multiple connectomic studies directly within template space and based on the group connectome only.

In **2017**, a [first article](https://doi.org/10.1002/hbm.23594) under the lead of [Andrea A Kühn](https://scholar.google.de/citations?user=3sSXEQwAAAAJ) **made use** of such normative connectomes by combining connectivity measures with **electrophysiological recordings** of the subcortex. This novel connectome in use here was based on [high-quality multishell diffusion data](https://www.humanconnectome.org/study/hcp-young-adult/document/mgh-adult-diffusion-data-acquisition-details) acquired within the [human connectome project](https://www.humanconnectome.org/)([Setsompop 2013](https://doi.org/10.1016/j.neuroimage.2013.05.078)).

A [second article](https://doi.org/10.1016/j.neuroimage.2017.02.004) published under the lead of [Michael D Fox](https://scholar.google.co.uk/citations?user=d9kqMj0AAAAJ) explored **connectivity profiles** of literature based **deep brain stimulation targets** using normative connectomes. This made use of a 1000-healthy subject **functional connectome** based on data of the Harvard [Brain Genomic Superstruct Project](https://www.neuroinfo.org/gsp/) that is also used on [neurosynth.org](https://neurosynth.org/) and was both preprocessed and provided by [Thomas Yeo](https://scholar.google.com/citations?user=BOUzsU8AAAAJ) ([Yeo 2011](https://doi.org/10.1152/jn.00338.2011)).

Finally, within work of a [third article](https://doi.org/10.1002/ana.24974), both functional and structural average connectomes from **patients** suffering from **Parkinson’s Disease** were created (using data of the [PPMI](https://www.ppmi-info.org/)).

Most normative connectomes are available for direct download within the Lead-DBS.

###

![](http://andreas-horn.de/wp-content/uploads/2017/12/Bildschirmfoto-2017-12-29-um-13.12.18-1030x760.png)

## List of currently available connectomes

- **Structural normative connectomes**
  - Structural group connectome of **19 subjects** [Gibbs-tracker] ([Horn 2013](https://www.ncbi.nlm.nih.gov/pubmed/24099851))  
    [[Direct download current version v1.0](http://www.lead-dbs.org/release/download.php?id=group2013)]
  - Structural group connectome of **169 NKI-RS subjects** [Gibbs-tracker] ([Horn 2016](https://www.ncbi.nlm.nih.gov/pubmed/26327244))  
    [[Direct download current version v1.0](http://www.lead-dbs.org/release/download.php?id=group2016); [Download via NITRC](https://www.nitrc.org/projects/gibbsconnectome/)]
  - Structural group connectome of **32 Adult Diffusion MGH-USC HCP subjects** [GQI fiber tracking] (Dataset: [Setsompop 2013](http://doi.org/10.1016/j.neuroimage.2013.05.078); processing: [Horn 2017](https://www.ncbi.nlm.nih.gov/pubmed/28163141))  
    [[Direct download current version v1.2](http://www.lead-dbs.org/release/download.php?id=group2017); older versions: [v1.1](https://filedn.com/lsPIJ4ragTWjjmV6PvlDQLu/data/older_versions/groupconnectome_HCP_MGH_32fold_horn_2017_v1.1.zip), [v1.0](https://filedn.com/lsPIJ4ragTWjjmV6PvlDQLu/data/older_versions/groupconnectome_HCP_MGH_30fold_horn_2017_v1.0.zip)]
  - Structural group connectome of **85 PPMI PD-patients** [GQI fiber tracking] (Dataset: [Marek 2011](http://doi.org/10.1016/j.pneurobio.2011.09.005); processing: [Ewert 2017](https://www.ncbi.nlm.nih.gov/pubmed/28536045))  
    [[Direct download current version v1.1](http://www.lead-dbs.org/release/download.php?id=group2017_ppmi); older versions: [v1.0](https://filedn.com/lsPIJ4ragTWjjmV6PvlDQLu/data/older_versions/groupconnectome_ppmi_90_ewert_2017_v1.0.zip)]
  - Structural group connectome of **985 HCP subjects** [GQI fiber tracking]: dTOR-985 ([Elias 2024](https://doi.org/10.1038/s41597-024-03197-0))  
    [Scripts and datasets on [FigShare](https://doi.org/10.6084/m9.figshare.c.6844890.v1); [Quarter version](https://www.lead-dbs.org/release/download.php?id=dTOR985_Quarter); [Half version](https://www.lead-dbs.org/release/download.php?id=dTOR985_Half); [Full version](https://www.lead-dbs.org/release/download.php?id=dTOR985_Full)]

- **Functional normative connectomes**
  - Resting-state functional group connectome of **1000 [GSP](https://www.neuroinfo.org/gsp/) healthy subjects**, can be directly used for network mapping within Lead-DBS (Lead Mapper and NetworkMapping Explorer), preprocessed by Bassam Al-Fatly ([Cohen 2023](https://doi.org/10.7910/DVN/KKTJQC)). Install: download and extract all **\*.tar** files from the [Harvard Dataverse](https://doi.org/10.7910/DVN/KKTJQC) repository, rename the extracted connectome folder to **GSP 1000 v2 (Cohen 2023)**, then download **dataset_info.json**, **dataset_info.mat** and **dataset_volsurf.mat** from the same repository and place them into the renamed connectome folder.
  - Resting-state functional group connectome of **74 PPMI PD-patients, 15 controls** (Dataset: [Marek 2011](http://doi.org/10.1016/j.pneurobio.2011.09.005); processing: [Horn 2017](http://onlinelibrary.wiley.com/doi/10.1002/ana.24974/abstract))  
    [[Direct download current version v1.0](http://www.lead-dbs.org/release/download.php?id=fgroup2017_ppmi)]
  - Resting-state functional group connectome of **75 Toronto PD-patients** (Detailed description: [Zenodo](https://doi.org/10.5281/zenodo.4310182); processing: [Horn 2017](http://onlinelibrary.wiley.com/doi/10.1002/ana.24974/abstract))  
    [[Direct download current version v1.0](https://www.lead-dbs.org/release/download.php?id=TorPD)]
  - Resting-state functional group connectome of **100 typically developing children** (6-18 yrs) assembled from [NYU 2](https://fcon_1000.projects.nitrc.org/indi/CoRR/html/nyu_2.html) sub-cohort of the [Consortium for Reliability and Reproducibility](https://fcon_1000.projects.nitrc.org/indi/CoRR/html/index.html). The raw data was preprocessed using a set of multiple neuroimaging pipelines (SPM, FSL and Lead-DBS). The timeseries were normalized to the [pediatric MNI space](https://nist.mni.mcgill.ca/pediatric-atlases-4-5-18-5y/) and integrated in Lead-DBS as a ready-to-read timeseries matrices using Lead-Connectome Mapper. The connectome is suitable to use with data normalized to the aforementioned pediatric space. For further details, please refer to [Al-Fatly 2023](https://doi.org/10.1016/j.nicl.2023.103449). [[Direct download](https://www.lead-dbs.org/release/download.php?id=PedrsfMRI)]

{{< button href="/download/" >}}Download normative connectomes (via Lead DBS){{< /button >}}

## Applications

Normative connectomes **cannot replace patient/subject-specific connectivity information** but are **useful** in scenarios where subject-specific data is **not available** and cannot be acquired. This often includes **clinical applications** such as:

- **Deep Brain Stimulation**: After surgery, patients cannot be scanned in the MRI without restrictions, acquiring high quality data is difficult if not impossible (e.g. Horn [2017a](http://onlinelibrary.wiley.com/doi/10.1002/ana.24974/abstract),[b](https://www.ncbi.nlm.nih.gov/pubmed/28163141),[c](http://onlinelibrary.wiley.com/doi/10.1002/hbm.23594/abstract)).
- Other forms of Brain Stimulation: Similar concepts may apply to noninvasive brain stimulation such as TMS (e.g. [Weigand 2017](http://doi.org/10.1016/j.biopsych.2017.10.028))
- **Stroke**: After stroke, patients can undergo MRI scans, but their brain structure is modified by the stroke event. If researchers are interested in how connectivity was before the stroke event, normative connectomes may at least give a useful hint (e.g. [Boes 2015](http://doi.org/10.1093/brain/awv228), [Laganiere 2016](http://doi.org/10.1212/WNL.0000000000002741), [Fischer 2016](http://doi.org/10.1212/WNL.0000000000003404), [Darby 2016](http://doi.org/10.1093/brain/aww288) & [2017](http://doi.org/10.1073/pnas.1706587115), [Fasano 2017](http://doi.org/10.1002/ana.24845))
- **Analysing large databases**: It is often difficult if not impossible to acquire connectivity data from large cohorts of patients/subjects that are analysed retrospectively. Still, such databases can sometimes yield highly valuable information and the combination with normative connectomes can yield further information (e.g. [Horn 2017a](http://onlinelibrary.wiley.com/doi/10.1002/ana.24974/abstract)).
