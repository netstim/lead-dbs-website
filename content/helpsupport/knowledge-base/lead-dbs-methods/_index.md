---
title: "Features"
description: "What Lead-DBS does: electrode localization, stimulation modelling, connectivity and group analysis, each with its chapter in the manual and its paper."
weight: 3
linkTitle: "Features"
date: "2017-04-19T16:59:05"
lastmod: "2026-11-11"
keywords: ["what Lead-DBS does", "methods", "tools", "methods and tools", "capabilities", "overview", "Lead tools", "features", "what it does", "electrode localization", "reconstruction", "normalization", "registration", "WarpDrive", "VTA", "volume of tissue activated", "electric field", "OSS-DBS", "sweet spot", "fibre filtering", "fiber filtering", "network mapping", "Lead Group", "group analysis", "Lead Connectome", "Lead Connectome Mapper", "Lead-OR", "Lead Tutor", "SlicerNetstim", "connectome"]
# the picture shown when the page is shared (head.html)
share: "images/renders/head-features.jpg"
# a showcase page: the chapters, their pictures and cards use the full width, no sidebar
sidebar: false
toc: false
# the named tools of the Tools table, found by the site search as results of their own
# (layouts/home.searchindex.json); Lead-OR and Lead Tutor have pages of their own
searchEntries:
  - {title: "Lead Group", id: "lead-group", keywords: "Lead Group LeadGroup group analysis cohort tool", description: "The tool for group analyses: electrode placement, stimulation volumes, sweet spots and networks against clinical outcome."}
  - {title: "Lead Connectome", id: "lead-connectome", keywords: "Lead Connectome Mapper connectome tractography diffusion resting-state fMRI tool", description: "Connectomes from diffusion MRI and resting-state fMRI; its Mapper gives the connectivity of any seed."}
  - {title: "OSS-DBS", id: "oss-dbs", keywords: "OSS-DBS OSSDBS stimulation modelling electric field VTA pathway activation tool", description: "The stimulation modelling of Lead-DBS since 3.1, developed with the University of Rostock; installs with Lead-DBS."}
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/helpsupport/first-steps/", text: "New to Lead-DBS? Start here"}
  - {page: "/helpsupport/knowledge-base/atlasesresources/", text: "The atlases and connectomes these methods use"}
---

{{< jumps "Single patients|#single-patients; Groups of patients|#groups-of-patients; In the operating theatre|#operating-theatre; Tools and modules|#tools" >}}
Lead-DBS takes a patient's MRI or CT from before and after surgery and shows where the DBS electrodes
are, what they stimulate and which brain networks they reach, for one patient or a whole cohort. The
[Lead-DBS v3 paper](https://doi.org/10.1016/j.neuroimage.2023.119862) (Neudorfer et al. 2023) describes
it all.
{{< /jumps >}}

{{% chapter n="1" img="images/renders/cohort-hero.jpg" focus="58% 46%" %}}
## Single patients {#single-patients}

Where the electrodes sit and what they stimulate.
{{% /chapter %}}

{{< capabilities >}}
{{< capability title="Registration and normalization" id="normalization" img="images/renders/cohort-top.jpg"
    manual="Volume registrations|https://netstim.gitbook.io/leaddbs/lead-dbs/step3-volume-registrations"
    papers="ewert2019 oxenford2024" >}}
Aligns the images from before and after surgery and warps them into a shared template space,
[MNI space](/about-the-mni-spaces/) (the ICBM 2009b template), so that electrodes of many patients can be
compared. Where the warp is off, the WarpDrive tool corrects it by hand.
{{< /capability >}}

{{< capability title="Electrode localization" id="localization" img="images/renders/lead-closeup.jpg"
    manual="Reconstruction of electrode trajectories|https://netstim.gitbook.io/leaddbs/lead-dbs/step5-optional-reconstruction-of-electrode-trajectories"
    papers="horn2015 husch2018" >}}
Reconstructs the electrodes from postoperative MRI or CT, including the orientation of directional
leads, with automatic methods you can refine by hand: TRAC/CORE, from the first Lead-DBS paper, and PaCER.
{{< /capability >}}

{{< capability title="Stimulation modelling" id="stimulation" img="images/renders/pathway-activation.jpg"
    manual="Calculate VTA and stats|https://netstim.gitbook.io/leaddbs/lead-group/calculate-vta-and-stats"
    papers="butenko2020 zimmermann2026" >}}
Models the volume of tissue activated, the electric field and the fibre pathways a setting activates,
with [OSS-DBS](#oss-dbs), the stimulation model built into Lead-DBS.
{{< /capability >}}

{{< capability title="Visualization" id="visualization" img="gallery/edlow2019_fig7_panela.png" fit="contain"
    manual="Visualization|https://netstim.gitbook.io/leaddbs/lead-dbs/step7-visualization"
    papers="horn2015" >}}
Shows electrodes in 2D and 3D among the structures of an atlas, with fibre tracts and stimulation
volumes, on templates such as the 100 µm 7 tesla brain.
{{< /capability >}}

{{< capability title="Connectivity" id="connectivity" img="/helpsupport/knowledge-base/lead-dbs-methods/connectivity-benefit-mapping/cbm1-1030x676.png" fit="contain"
    alt="Functional connectivity profiles of the DBS sites of 12 patients on cortical surfaces"
    caption="Connectivity of the stimulation sites of 12 patients, from DBS network mapping"
    manual="Connectomics|https://netstim.gitbook.io/leaddbs/connectomics/connectomic-analyses"
    papers="horn2016" >}}
Estimates the structural and functional connectivity of a stimulation site, from the patient's own
connectome or a [normative connectome](/helpsupport/knowledge-base/atlasesresources/normative-connectomes/),
an average wiring diagram of many human brains, with [Lead Connectome](#lead-connectome).
{{< /capability >}}
{{< /capabilities >}}

{{< capability title="AC/PC to MNI conversion" id="acpc" link="/helpsupport/knowledge-base/lead-dbs-methods/acpc-to-mni-conversion-2/"
    img="/helpsupport/knowledge-base/lead-dbs-methods/acpc-to-mni-conversion-2/fig_3.png" fit="contain"
    alt="DBS targets of nine indications, from Parkinson’s disease to addiction, as heat maps on slices of the MNI template with the surrounding structures labelled"
    caption="DBS targets from the surgical literature, defined in MNI space (Horn 2017)"
    papers="horn2017acpc" >}}
Converts surgical AC/PC coordinates into MNI space and back, with age-matched reference brains. In the
Tools menu of Lead-DBS.
{{< /capability >}}

{{% chapter n="2" img="images/renders/fiber-filtering-wide.jpg" focus="50% 38%" %}}
## Groups of patients {#groups-of-patients}

A whole cohort in one space, against clinical outcome.
{{% /chapter %}}

{{< capabilities >}}
{{< capability title="Group analysis and sweet spots" id="group" img="gallery/li2020_fig1.png" fit="contain"
    manual="Group analyses|https://netstim.gitbook.io/leaddbs/lead-group/group-analyses-with-lead-dbs; Sweetspot Explorer|https://netstim.gitbook.io/leaddbs/lead-group/sweetspot-explorer"
    papers="treu2020 neudorfer2023" >}}
Electrode placement across a cohort and its relation to clinical outcome, in [Lead Group](#lead-group);
sweet-spot mapping finds where in the target region stimulation went along with better or worse outcomes.
{{< /capability >}}

{{< capability title="DBS network mapping and fibre filtering" id="network-mapping" link="/helpsupport/knowledge-base/lead-dbs-methods/connectivity-benefit-mapping/"
    img="gallery/li2020_fig4_top.png" fit="contain"
    manual="Connectomics|https://netstim.gitbook.io/leaddbs/connectomics/connectomic-analyses"
    papers="horn2017ana neudorfer2023" >}}
Relates the connections of stimulation sites, as whole-brain maps or single fibre tracts, to clinical
outcome, and predicts the outcome of new patients.
{{< /capability >}}
{{< /capabilities >}}

{{< capability title="Subcortical electrophysiology mapping" id="sem" link="/helpsupport/knowledge-base/lead-dbs-methods/subcortical-electrophysiology-mapping-sem/"
    img="/helpsupport/knowledge-base/lead-dbs-methods/subcortical-electrophysiology-mapping-sem/betaalpha3d.png" fit="contain"
    alt="Beta and alpha peaks within the STN in 3D, with electrode trajectories"
    caption="Where beta and alpha activity peak within the subthalamic nucleus"
    manual="Group analyses|https://netstim.gitbook.io/leaddbs/lead-group/group-analyses-with-lead-dbs"
    papers="horn2017hbm" >}}
Pools recordings from DBS electrodes across patients into a 3D map of where an activity is strongest.
{{< /capability >}}

{{% chapter n="3" %}}
## In the operating theatre {#operating-theatre}

Recordings and test stimulation, shown on the images in real time.
{{% /chapter %}}

{{< capability title="Lead-OR" id="lead-or" link="/about/lead-or/" img="gallery/oxenford2022_fig1.jpg" fit="contain"
    manual="Lead-OR: imaging setup|https://netstim.gitbook.io/leaddbs/lead-or/imaging-setup"
    papers="oxenford2022" >}}
A sister tool for research during surgery: it shows recordings and test stimulation in real time on the
coregistrations of Lead-DBS. It runs in [3D Slicer](https://www.slicer.org/), in the
[SlicerNetstim](https://github.com/netstim/SlicerNetstim) extension.
{{< /capability >}}

{{% chapter n="4" %}}
## Tools and modules {#tools}

The named parts of Lead-DBS and its practice dataset.
{{% /chapter %}}

| Tool | What it is for | Manual | Paper |
| --- | --- | --- | --- |
| <span id="lead-group"></span>Lead Group | Group analyses: placement, stimulation volumes, sweet spots and networks against outcome | [Group analyses](https://netstim.gitbook.io/leaddbs/lead-group/group-analyses-with-lead-dbs) | {{< paper treu2020 >}} |
| <span id="lead-connectome"></span>Lead Connectome | Connectomes from diffusion MRI and resting-state fMRI; its Mapper gives the connectivity of any seed (tractography: see the [dependencies](/about/lead-dbs-dependencies/)) | [Lead Connectome Mapper](https://netstim.gitbook.io/leaddbs/connectomics/lead-mapper) | {{< paper horn2014 >}} |
| <span id="oss-dbs"></span>OSS-DBS | Stimulation modelling since Lead-DBS 3.1, developed with Ursula van Rienen's team at the University of Rostock; installs with Lead-DBS ([code](https://github.com/SFB-ELAINE/OSS-DBSv2)) | [Calculate VTA and stats](https://netstim.gitbook.io/leaddbs/lead-group/calculate-vta-and-stats) | {{< paper butenko2020 >}}, {{< paper zimmermann2026 >}} |
| <span id="lead-tutor"></span>[Lead Tutor](/helpsupport/learn-lead-dbs-yourself/) | Practise electrode localization on open data, scored against experts | [Self-tutoring](https://netstim.gitbook.io/leaddbs/lead-dbs/self-tutoring-with-lead-tutor) | {{< paper madan2025 >}} |
{.table--stack caption="Tools of Lead-DBS"}

All tools of the institute are on [GitHub](https://github.com/netstim). All these papers are listed in full
under [Publications](/about/publications/#methodological-publications); which ones to cite is on [Cite Lead-DBS](/about/citing_leaddbs/).
The renders on this page are by the Lead-DBS team, from the open Lead Tutor data; more of them, and
figures from published papers, are in [Made with Lead-DBS](/gallery/).
