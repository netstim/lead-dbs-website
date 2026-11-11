---
title: "Normative connectomes"
description: "Normative connectomes: average structural and functional wiring diagrams of the human brain in MNI space, for use with Lead-DBS."
date: "2017-12-29T11:56:26"
lastmod: "2026-11-11"
weight: 3
aliases: ["/sdm_downloads/groupconnectome-horn-2013/"]
# the picture shown when the page is shared (head.html)
share: "images/renders/fiber-filtering.jpg"
---
Normative connectomes are average structural (tractography) and functional (resting-state fMRI)
wiring diagrams of the human brain in MNI space, for estimating the connectivity of a stimulation
site when a patient's own diffusion or fMRI data are missing. **To get one**, download it from within
Lead-DBS, or use the direct downloads in the [tables below](#list-of-currently-available-connectomes).

**What to cite:** the paper in the *Paper* column of the connectome you used.

## List of currently available connectomes

### Structural

| Connectome | Subjects | Method | Paper | Download |
|---|---|---|---|---|
| Group connectome 2013 | 19 healthy subjects | Gibbs tracker | [Horn 2013](https://www.ncbi.nlm.nih.gov/pubmed/24099851) | [v1.0](http://www.lead-dbs.org/release/download.php?id=group2013) |
| NKI-RS group connectome | 169 NKI-RS subjects | Gibbs tracker | [Horn 2016](https://www.ncbi.nlm.nih.gov/pubmed/26327244) | [v1.0](http://www.lead-dbs.org/release/download.php?id=group2016) · [NITRC](https://www.nitrc.org/projects/gibbsconnectome/) |
| HCP MGH-USC group connectome | 32 adult diffusion subjects of the MGH-USC HCP ([Setsompop 2013](https://doi.org/10.1016/j.neuroimage.2013.05.078)) | GQI fibre tracking | [Horn 2017](https://www.ncbi.nlm.nih.gov/pubmed/28163141) | [v1.2](http://www.lead-dbs.org/release/download.php?id=group2017) · older: [v1.1](https://filedn.com/lsPIJ4ragTWjjmV6PvlDQLu/data/older_versions/groupconnectome_HCP_MGH_32fold_horn_2017_v1.1.zip), [v1.0](https://filedn.com/lsPIJ4ragTWjjmV6PvlDQLu/data/older_versions/groupconnectome_HCP_MGH_30fold_horn_2017_v1.0.zip) |
| PPMI group connectome | 85 PPMI patients with Parkinson's disease ([Marek 2011](https://doi.org/10.1016/j.pneurobio.2011.09.005)) | GQI fibre tracking | [Ewert 2017](https://www.ncbi.nlm.nih.gov/pubmed/28536045) | [v1.1](http://www.lead-dbs.org/release/download.php?id=group2017_ppmi) · older: [v1.0](https://filedn.com/lsPIJ4ragTWjjmV6PvlDQLu/data/older_versions/groupconnectome_ppmi_90_ewert_2017_v1.0.zip) |
| dTOR-985 | 985 HCP subjects | GQI fibre tracking | [Elias 2024](https://doi.org/10.1038/s41597-024-03197-0) | [Quarter](https://www.lead-dbs.org/release/download.php?id=dTOR985_Quarter) · [half](https://www.lead-dbs.org/release/download.php?id=dTOR985_Half) · [full](https://www.lead-dbs.org/release/download.php?id=dTOR985_Full) version; scripts and data on [FigShare](https://doi.org/10.6084/m9.figshare.c.6844890.v1) |
{.table--stack caption="Structural normative connectomes"}

### Functional

| Connectome | Subjects | Method | Paper | Download |
|---|---|---|---|---|
| GSP 1000 v2 | 1000 healthy subjects of the [GSP](https://www.neuroinfo.org/gsp/) | Resting-state fMRI, preprocessed by Bassam Al-Fatly | [Cohen 2023](https://doi.org/10.7910/DVN/KKTJQC) | [Harvard Dataverse](https://doi.org/10.7910/DVN/KKTJQC) (see [installing GSP 1000](#gsp-1000)) |
| PPMI functional connectome | 74 PPMI patients with Parkinson's disease, 15 controls ([Marek 2011](https://doi.org/10.1016/j.pneurobio.2011.09.005)) | Resting-state fMRI | [Horn 2017](https://doi.org/10.1002/ana.24974) | [v1.0](http://www.lead-dbs.org/release/download.php?id=fgroup2017_ppmi) |
| Toronto PD connectome | 75 patients with Parkinson's disease, Toronto ([description on Zenodo](https://doi.org/10.5281/zenodo.4310182)) | Resting-state fMRI | [Horn 2017](https://doi.org/10.1002/ana.24974) | [v1.0](https://www.lead-dbs.org/release/download.php?id=TorPD) |
| Paediatric connectome | 100 typically developing children, 6–18 years ([CoRR NYU 2](http://fcon_1000.projects.nitrc.org/indi/CoRR/html/nyu_2.html)) | Resting-state fMRI, in the paediatric MNI space | [Al-Fatly 2023](https://doi.org/10.1016/j.nicl.2023.103449) | [Download](https://www.lead-dbs.org/release/download.php?id=PedrsfMRI) |
{.table--stack caption="Functional normative connectomes"}

The GSP 1000 connectome can be used directly for network mapping within Lead-DBS (Lead Mapper and the
NetworkMapping Explorer).

**Installing GSP 1000:** download and extract all **\*.tar** files from the [Harvard Dataverse](https://doi.org/10.7910/DVN/KKTJQC) repository, rename the extracted connectome folder to **GSP 1000 v2 (Cohen 2023)**, then download **dataset_info.json**, **dataset_info.mat** and **dataset_volsurf.mat** from the same repository and place them into the renamed connectome folder.
{#gsp-1000}

The paediatric connectome was assembled from the [NYU 2](http://fcon_1000.projects.nitrc.org/indi/CoRR/html/nyu_2.html) sub-cohort of the [Consortium for Reliability and Reproducibility](http://fcon_1000.projects.nitrc.org/indi/CoRR/html/index.html). The raw data was preprocessed with several neuroimaging pipelines (SPM, FSL and Lead-DBS), and the time series were normalized to the [paediatric MNI space](https://nist.mni.mcgill.ca/pediatric-atlases-4-5-18-5y/) and integrated in Lead-DBS as ready-to-read time-series matrices using the Lead Connectome Mapper. It is suitable for data normalized to that paediatric space.

{{< button href="/download/" >}}Download Lead-DBS, with the normative connectomes{{< /button >}}

## How they came about

Since 2014, we worked on estimating “**average wiring diagrams**” of the human brain. Based on diffusion-weighted or resting-state functional MRI data of large cohorts of subjects/patients, this line of work focused on running whole-brain tractography or functional connectivity analyses, warping individual connectomes into standard space and then **averaging the results** across the group of subjects.

In **2014**, we published a [first article](https://doi.org/10.1016/j.neuroimage.2013.09.069) under the lead of [Felix Blankenburg](https://scholar.google.de/citations?user=-QOB8EoAAAAJ) describing the effort of a **first structural-functional MNI connectome**. There is a small [additional article](https://doi.org/10.1016/j.dib.2015.08.035) associated with the data release of this first connectome. In **2016**, we [**replicated results**](https://doi.org/10.1016/j.neuroimage.2015.08.048) based on a much larger cohort of healthy subjects and [**validated**](https://doi.org/10.1016/j.neuroimage.2015.08.048) the use of such normative connectomes by replicating multiple connectomic studies directly within template space and based on the group connectome only.

In **2017**, a [first article](https://doi.org/10.1002/hbm.23594) under the lead of [Andrea A Kühn](https://scholar.google.de/citations?user=3sSXEQwAAAAJ) **made use** of such normative connectomes by combining connectivity measures with **electrophysiological recordings** of the subcortex. This novel connectome in use here was based on [high-quality multishell diffusion data](https://www.humanconnectome.org/study/hcp-young-adult/document/mgh-adult-diffusion-data-acquisition-details) acquired within the [human connectome project](https://www.humanconnectome.org/)([Setsompop 2013](https://doi.org/10.1016/j.neuroimage.2013.05.078)).

A [second article](https://doi.org/10.1016/j.neuroimage.2017.02.004) published under the lead of [Michael D Fox](https://scholar.google.co.uk/citations?user=d9kqMj0AAAAJ) explored **connectivity profiles** of literature based **deep brain stimulation targets** using normative connectomes. This made use of a 1000-healthy subject **functional connectome** based on data of the Harvard [Brain Genomic Superstruct Project](https://www.neuroinfo.org/gsp/) that is also used on [neurosynth.org](https://neurosynth.org/) and was both preprocessed and provided by [Thomas Yeo](https://scholar.google.com/citations?user=BOUzsU8AAAAJ) ([Yeo 2011](https://doi.org/10.1152/jn.00338.2011)).

Finally, within work of a [third article](https://doi.org/10.1002/ana.24974), both functional and structural average connectomes from **patients** suffering from **Parkinson’s Disease** were created (using data of the [PPMI](https://www.ppmi-info.org/)).

## Applications

Normative connectomes **cannot replace patient/subject-specific connectivity information** but are **useful** in scenarios where subject-specific data is **not available** and cannot be acquired. This often includes **clinical applications** such as:

- **Deep Brain Stimulation**: After surgery, patients cannot be scanned in the MRI without restrictions, acquiring high quality data is difficult if not impossible (e.g. Horn [2017a](http://onlinelibrary.wiley.com/doi/10.1002/ana.24974/abstract),[b](https://www.ncbi.nlm.nih.gov/pubmed/28163141),[c](http://onlinelibrary.wiley.com/doi/10.1002/hbm.23594/abstract)).
- Other forms of Brain Stimulation: Similar concepts may apply to noninvasive brain stimulation such as TMS (e.g. [Weigand 2017](https://doi.org/10.1016/j.biopsych.2017.10.028))
- **Stroke**: After stroke, patients can undergo MRI scans, but their brain structure is modified by the stroke event. If researchers are interested in how connectivity was before the stroke event, normative connectomes may at least give a useful hint (e.g. [Boes 2015](https://doi.org/10.1093/brain/awv228), [Laganiere 2016](https://doi.org/10.1212/WNL.0000000000002741), [Fischer 2016](https://doi.org/10.1212/WNL.0000000000003404), [Darby 2016](https://doi.org/10.1093/brain/aww288) & [2017](https://doi.org/10.1073/pnas.1706587115), [Fasano 2017](https://doi.org/10.1002/ana.24845))
- **Analysing large databases**: It is often difficult if not impossible to acquire connectivity data from large cohorts of patients/subjects that are analysed retrospectively. Still, such databases can sometimes yield highly valuable information and the combination with normative connectomes can yield further information (e.g. [Horn 2017a](http://onlinelibrary.wiley.com/doi/10.1002/ana.24974/abstract)).

## Next

Connectomes are combined with [cortical parcellations](/helpsupport/knowledge-base/atlasesresources/cortical-atlas-parcellations-mni-space/)
and used by methods such as [DBS network mapping](/helpsupport/knowledge-base/lead-dbs-methods/connectivity-benefit-mapping/).
How to run a connectivity analysis is described in the [manual](https://netstim.gitbook.io/leaddbs).
