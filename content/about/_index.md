---
title: "About Lead-DBS"
description: "What Lead-DBS is and does, its history, recognition and funding, the Lead tools, and where to find its papers, figures and contributors."
linkTitle: "About"
date: "2014-06-17T15:06:49"
lastmod: "2026-11-11"
# the long list of people moved to /about/team/ (Contributors); the section #development-team here links to it
# /hallo-welt/ was the old site's "Welcome to Lead-DBS" post
aliases: ["/hallo-welt/"]
keywords: ["about", "deep brain stimulation", "DBS", "team", "history", "funding", "Lead-OR", "Lead Connectome", "Lead Group", "OSS-DBS"]
---

Lead-DBS is an open-source MATLAB toolbox for deep brain stimulation (DBS) imaging. It is developed
by researchers from several institutions and coordinated by the [Institute for Network Stimulation](https://www.netstim.org)
at the University Hospital Cologne. It is free software under the GNU General Public Licence, with its
code on [GitHub](https://github.com/netstim/leaddbs). The current release is Lead-DBS {{< release version >}}, released on {{< release date >}}.

{{< notice id="research-use" >}}**For research use only.** Lead-DBS is research software for retrospective scientific analysis; it is not intended for diagnosis, treatment planning or any other clinical decision about an individual patient. The full statement is on the [download page](/download/#research-use).{{< /notice >}}

{{< childpages menu="true" >}}

## What Lead-DBS does

- **Localizes DBS electrodes** in the brain from postoperative MRI or CT, together with preoperative MRI.
- **Shows the result** in 2D and 3D, together with [atlases of the brain](/helpsupport/knowledge-base/atlasesresources/).
- **Compares patients**: electrode placement across a group and its relation to clinical outcome (Lead Group).
- **Simulates the stimulation**: the volume of tissue activated, electric fields and pathway activation (with OSS-DBS).
- **Maps networks**: the connectivity of a stimulation site to the rest of the brain, using [normative connectomes](/helpsupport/knowledge-base/atlasesresources/normative-connectomes/) or the patient's own data.

How each step works is described in the [manual](https://netstim.gitbook.io/leaddbs); what you need to run it is on the [download page](/download/).

![Atlas structures and a DBS electrode in 3D over a histological section](LEAD_Scene-1030x541.jpg)

## Deep brain stimulation {#deep-brain-stimulation}

In deep brain stimulation, electrodes are **surgically implanted** into deep (subcortical) areas of the
brain, and an implanted impulse generator **stimulates** these structures chronically. It is used
predominantly in movement disorders such as Parkinson’s disease, essential tremor and dystonia, and more
rarely in other disorders such as depression or Alzheimer’s disease. Where exactly an electrode sits, and
which brain networks it reaches, matters for its effect: this is what Lead-DBS helps researchers study.

## History

- **2012**: work on a toolbox to reconstruct DBS electrode placement from postoperative imaging begins, at the Movement Disorders Unit of Andrea Kühn, Department of Neurology, Charité – Universitätsmedizin Berlin.
- **2015**: the first paper ([Horn & Kühn, NeuroImage 2015](https://doi.org/10.1016/j.neuroimage.2014.12.002)).
- **2016**: researchers from several institutions join the development.
- **2019**: the Network Stimulation Laboratory led by Andreas Horn coordinates it; Lead-DBS v2 is published ([Horn, Li et al., NeuroImage 2019](https://doi.org/10.1016/j.neuroimage.2018.08.068)).
- **2023**: Lead-DBS v3.0 ([Neudorfer et al., NeuroImage 2023](https://doi.org/10.1016/j.neuroimage.2023.119862)).
- **2025**: the lab becomes the Institute for Network Stimulation at the University Hospital Cologne.

## Recognition and funding

In January 2015, Lead-DBS was awarded the **Max Rubner Prize** for Innovation and Technology of [Stiftung Charité](https://www.stiftung-charite.de/); the prize money went into the further development of the toolbox. In 2016 it received a **Harvard Radcliffe Exploratory Ventures Grant** from the [Harvard Radcliffe Institute for Advanced Study](https://www.radcliffe.harvard.edu/), and in 2017 the **Robert Koch Prize** of Charité, Berlin. Further development was [funded by a six-year grant of the German Research Foundation (DFG)](https://gepris.dfg.de/gepris/projekt/410169619?context=projekt&task=showDetail&id=410169619&).

Lead-DBS has been supported by the Berlin Institute of Health, KFO 247, the German Research Foundation (DFG), Stiftung Charité and the Prof. Dr. Klaus Thiemann Foundation.

### What others write

{{< quote source="Husch, Petersen, Gemmar, Goncalves & Hertel (2018), PaCER – A fully automated method for electrode trajectory and contact reconstruction in deep brain stimulation. *NeuroImage: Clinical* 17, 80–89" doi="10.1016/j.nicl.2017.10.004" >}}The MATLAB™-based LeadDBS is arguably the most established toolbox providing a semi-automatic framework for electrode localization based on automatic pre-processing and a manual refinement step.{{< /quote >}}

{{< quote source="Nowacki, Nguyen, Tinkhauser, Petermann, Debove, Wiest & Pollo (2018), Accuracy of different three-dimensional subcortical human brain atlases for DBS-lead localisation. *NeuroImage: Clinical* 20, 868–874" doi="10.1016/j.nicl.2018.09.030" >}}Lead reconstruction after normalisation into the MNI template space and application of four different atlases led to different results in terms of the DBS lead position relative to the STN. Based on electrophysiological and imaging data, the DISTAL atlas led to the most accurate display of the reconstructed DBS lead relative to the DISTAL-based STN.{{< /quote >}}

{{< quote source="Alkemade, Groot & Forstmann (2018), Do We Need a Human post mortem Whole-Brain Anatomical Ground Truth in in vivo Magnetic Resonance Imaging? *Frontiers in Neuroanatomy* 12, 110" doi="10.3389/fnana.2018.00110" >}}Two elegant examples were published by Horn et al. (2017) in which a method was described to warp DBS electrode coordinates, and histological data to MNI-space (Ewert et al., 2017).{{< /quote >}}

{{< quote source="Latorre, Rocchi & Sadnicka (2021), The Expanding Horizon of Neural Stimulation for Hyperkinetic Movement Disorders. *Frontiers in Neurology*" url="https://www.researchgate.net/publication/351579677_The_Expanding_Horizon_of_Neural_Stimulation_for_Hyperkinetic_Movement_Disorders" label="The paper on ResearchGate" >}}A commitment of the community to open science will also democratize and increase the speed of advances with high uptake of currently available initiatives such as LEAD-DBS (61). This freely available toolbox can be downloaded to allow electrode reconstructions and computer simulations based on post-operative MRI and CT imaging.{{< /quote >}}

{{< quote source="Milchenko, Snyder, Campbell, Dowling, Rich, Brier, et al. (2018), ESM-CT: a precise method for localization of DBS electrodes in CT images. *Journal of Neuroscience Methods*" doi="10.1016/j.jneumeth.2018.09.009" >}}… (method 2) available via the LEAD-DBS MATLAB package, which is widely used{{< /quote >}}

<span id="related-tools"></span>

## Lead tools {#lead-tools}

Lead-DBS comes with tools of its own (Lead Group, Lead Connectome, OSS-DBS for stimulation modelling) and
has sister tools from the same team (Lead-OR in the operating theatre, Lead Tutor for training). Each is
described, with its manual and paper, on [Lead tools](/about/tools/).

## People {#development-team}

Who built Lead-DBS is listed on [Contributors](/about/team/); everyone who has contributed
code is in the [contributors graph on GitHub](https://github.com/netstim/leaddbs/graphs/contributors).
To join, see [Develop Lead-DBS](/develop/).

## Next

- Use it in a paper: [Cite Lead-DBS](/about/citing_leaddbs/), then the [publications](/about/publications/) and figures [made with Lead-DBS](/gallery/).
- Try it: [download Lead-DBS](/download/) and take the [first steps](/helpsupport/first-steps/).
- Ask a question: the [user Slack](/helpsupport/slack-user-channel/) or [contact us](/contact/).
