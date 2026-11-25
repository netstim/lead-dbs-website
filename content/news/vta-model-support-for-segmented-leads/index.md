---
title: "VTA-model support for segmented Leads"
description: "Till Dembek built a segmented lead mesh, so the FEM-based model of Lead-DBS now computes VTAs for directional electrodes."
date: "2017-09-16T14:15:00"
slug: "vta-model-support-for-segmented-leads"
image: "directional_vta.png"
image_alt: "A segmented DBS electrode with the volume of tissue activated around it in red"
---

[Till Dembek](https://www.researchgate.net/profile/Till_Dembek) created a segmented Lead Mesh that allows
us to run our FEM-calculations (see [Connectivity Predicts deep brain stimulation outcome in Parkinson disease](https://www.researchgate.net/publication/317381045_Connectivity_Predicts_deep_brain_stimulation_outcome_in_Parkinson_disease);
model implemented based on SimBio with great help from [Johannes Vorwerk](https://www.researchgate.net/profile/Johannes_Vorwerk))
to create VTAs for these electrodes.

{{% row %}}
{{% col "1/2" %}}
![Fibre tracts passing through the VTA of a segmented electrode, beside subcortical structures in 3D](directional_fibertracts.png)
{{% /col %}}
{{% col "1/2" %}}
![A segmented DBS electrode with the volume of tissue activated around it in red](directional_vta.png)
{{% /col %}}
{{% /row %}}
