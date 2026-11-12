---
title: "Lead-DBS 2.0 released"
description: "Lead-DBS 2.0: the DISTAL atlas, a FEM-based VTA model, PaCER, microelectrode recordings, the Human Motor Thalamus atlas and new workflows."
date: "2017-09-09T20:19:44"
lastmod: "2026-11-12"
slug: "lead-dbs-v2-0-is-out-now"
# the picture shown when the page is shared (head.html)
share: "images/renders/lead-closeup.jpg"
---

Lead-DBS 2.0 is not a small incremental update. Its new features were a long time in the making, and
with them Lead-DBS is, for the first time, a complete DBS imaging pipeline.

![Lead-DBS 2.0 in a nutshell: overview of the new features around a 3D render](Lead_DBS_2_0_in_a_nutshell-1030x624.png)

## The DISTAL atlas

The [DISTAL atlas](/helpsupport/knowledge-base/atlasesresources/distal-atlas/) is a detailed atlas,
precisely co-registered to the [default working space of Lead-DBS](/helpsupport/knowledge-base/atlasesresources/about-the-mni-spaces/).
It combines three sources of information: MRI, histology (shared by Mallar Chakravarty and Louis
Collins) and structural connectivity. It defines all structures that have so far played a role in deep
brain stimulation, and it was validated for atlas-based segmentation of clinical MRI. The
[paper](https://linkinghub.elsevier.com/retrieve/pii/S1053-8119(17)30407-X) is in *NeuroImage*.

![DISTAL atlas structures in 3D with three DBS electrodes](distal_atlas-1030x1030.png)

The histological data in the atlas ([Chakravarty et al. 2006](https://www.ncbi.nlm.nih.gov/pubmed/16406816))
come in three nomenclatures with their abbreviations: for the thalamus, a rosetta stone of nomenclatures
in MNI space. In the 3D viewer, presets show, for instance, only the structures relevant to DBS, or the
functional parcellations of the STN and GPi.

{{< vimeo id="228993216" title="The DISTAL atlas in the Lead-DBS 3D viewer (2017)" >}}

## A FEM-based VTA model (beta)

Stimulation settings beyond monopolar stimulation need a model that estimates the spatial distribution
of voltage with the finite element method (FEM). Such models have existed for some time but never made
their way into open-source DBS software. Similar methods were published in EEG and MEG toolboxes such
as [FieldTrip](http://www.fieldtriptoolbox.org/) and [SimBio](https://www.mrt.uni-jena.de/simbio/index.php/Main_Page).

The new model is the first open-source FEM-based VTA model. It works for constant voltage and constant
current, models up to four combined sources and multiple cathodes in bipolar and monopolar settings,
and treats grey and white matter as separate compartments, as well as inactive contacts and the
electrode's insulation. Johannes Vorwerk (Utah), Qianqian Fang (Boston), Ningfei Li (Berlin) and
Robert Oostenveld (Nijmegen) built it. Publication:
[*Annals of Neurology* 2017](https://doi.org/10.1002/ana.24974).

![Simulated electric field around a DBS electrode contact (FEM-based VTA model)](abb_3-1030x1013.png)

The model is still in beta and may need troubleshooting. It does not yet work with segmented leads; we
are working on this with Till Dembek (Cologne).

## PaCER: precise automatic DBS reconstruction

Andreas Husch (Hertel lab, Luxembourg) shared his method to detect DBS electrodes automatically on
postoperative CT. PaCER is fast and precise; in most cases no manual refinement is needed. It can also
reconstruct curved electrodes, which Lead-DBS does not support yet. PaCER is also available as a
[standalone tool](https://adhusch.github.io/PaCER/).

![Reconstructed electrode trajectory above a lead (PaCER)](PaCER-388x1030.png)

## Microelectrode recordings mapped onto the brain

Ari Kappel (Richardson lab, University of Pittsburgh) and Chadwick Boulay (Sachs lab, University of
Ottawa) created a tool that maps microelectrode recordings (MER) onto the subcortical anatomy. It shows
how electrophysiological regions overlap with atlas regions, manual segmentations or raw MRI. How to
use it is in the [manual](https://netstim.gitbook.io/leaddbs).

{{< clip src="MER.mp4" poster="MER-poster.jpg" alt="Microelectrode recording trajectories through atlas structures in 3D" >}}

## The Human Motor Thalamus atlas

Igor and Kristy Ilinsky created a detailed histological atlas of the human motor thalamus. It
separates the termination areas of three subcortical afferent systems to the thalamus: nigral (VAn),
pallidal (VAp) and cerebellar (VL). The nuclear outlines were drawn from cytoarchitecture and the
staining pattern of GAD65, an enzyme that synthesizes GABA. The atlas was co-registered to MRI with the
pseudo-MRI approach of [Chakravarty and colleagues](http://www.sciencedirect.com/science/article/pii/S1361841508000443),
refined as for the DISTAL atlas. How its nuclei correspond to other nomenclatures (Walker, Hassler,
Jones) is on [humanmotorthalamus.com](http://www.humanmotorthalamus.com), with the
[pre-print](http://www.humanmotorthalamus.com/wp-content/uploads/2015/11/Ilinskyetal15last.pdf).

![Human Motor Thalamus atlas: thalamic nuclei in 3D](hmt-1030x937.png)

## Workflows for large datasets

Many workflows were rebuilt. Lead-DBS now records which co-registrations and normalizations you
approved or disapproved, in a faster viewer. You can run co-registration and normalization for 100
patients overnight, check the results the next morning and rerun only the ones that failed, with other
presets.

## New atlases and minor changes

The authors of the [nigral organization atlas](https://elifesciences.org/articles/26653) (Zhang 2017)
and the [histological PPN atlas](https://link.springer.com/article/10.1007%2Fs00429-016-1356-0)
(Alho 2017) contributed them to Lead-DBS. In total, Lead-DBS 2.0 comes with 23
[subcortical atlases](/helpsupport/knowledge-base/atlasesresources/atlases-2/) and 14
[whole-brain parcellations](/helpsupport/knowledge-base/atlasesresources/cortical-atlas-parcellations-mni-space/).

![Nigral organization atlas: substantia nigra subregions in 3D](nigral-1030x880.png)

- Group VTAs in lead_group, optionally weighted by a variable such as clinical improvement
- The ea_roi object shows the isosurface of any NIfTI file in a MATLAB figure or the 3D viewer
- Updated "effective" ANTs presets
- 2D export shows correctly when the atlas covers a larger area than the exported slice
- Automatic detection of MR or CT when processing several patients, locally or on a cluster
- [Many minor fixes](https://github.com/netstim/leaddbs/commits/)

{{< button href="/download/" >}}Download Lead-DBS{{< /button >}}
