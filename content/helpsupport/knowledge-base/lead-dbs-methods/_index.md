---
title: "Methods"
description: "Electrode localization, stimulation modelling, connectivity and group analysis in Lead-DBS."
weight: 3
linkTitle: "Methods"
date: "2017-04-19T16:59:05"
lastmod: "2026-11-12"
keywords: ["what Lead-DBS does", "methods", "tools", "methods and tools", "capabilities", "overview", "Lead tools", "features", "what it does", "electrode localization", "reconstruction", "normalization", "registration", "WarpDrive", "VTA", "volume of tissue activated", "electric field", "OSS-DBS", "sweet spot", "fibre filtering", "fiber filtering", "network mapping", "Lead Group", "group analysis", "Lead Connectome", "Lead Connectome Mapper", "Lead-OR", "Lead Tutor", "SlicerNetstim", "connectome"]
# the picture shown when the page is shared (head.html)
share: "images/renders/head-features.jpg"
# the named tools of the Tools table, found by the site search as results of their own
# (layouts/home.searchindex.json); Lead-OR and Lead Tutor have pages of their own
searchEntries:
  - {title: "Lead Group", id: "lead-group", keywords: "Lead Group LeadGroup group analysis cohort tool", description: "Relate electrode placement, stimulation volumes, sweetspots and brain networks to clinical outcomes across patients."}
  - {title: "Lead Connectome", id: "lead-connectome", keywords: "Lead Connectome Mapper connectome tractography diffusion resting-state fMRI tool", description: "Build connectomes from diffusion MRI and resting-state fMRI. Use Lead Connectome Mapper to estimate connectivity from a seed region."}
  - {title: "OSS-DBS", id: "oss-dbs", keywords: "OSS-DBS OSSDBS stimulation modelling electric field VTA pathway activation tool", description: "OSS-DBS v2, developed with the University of Rostock, supports stimulation modelling in Lead-DBS 3.1 onwards; installs on first use."}
# "Related" at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/helpsupport/first-steps/"}
  - {page: "/helpsupport/knowledge-base/atlasesresources/"}
  - {page: "/about/citing_leaddbs/"}
# the named tools, as picture cells at the end of the page (layouts/_shortcodes/tools.html)
tools:
  - {id: "lead-group", img: "images/renders/cohort-hero.jpg", name: "Lead Group", text: "Compare outcomes across patients.", manual: "Group analyses|/manual/lead-group/group-analyses-with-lead-dbs/", papers: "treu2020"}
  - {id: "lead-connectome", img: "images/renders/fiber-filtering-wide.jpg", name: "Lead Connectome", text: "Build connectomes from diffusion MRI and resting-state fMRI, and estimate connectivity from seed regions.", manual: "Lead Connectome Mapper|/manual/connectomics/lead-mapper/", papers: "horn2014"}
  - {id: "oss-dbs", img: "images/renders/pathway-activation-2.jpg", name: "OSS-DBS", text: "Stimulation modelling developed with the University of Rostock; installs automatically on first use.", manual: "Calculate VTA and stats|/manual/lead-group/calculate-vta-and-stats/", code: "https://github.com/SFB-ELAINE/OSS-DBSv2", papers: "butenko2020 zimmermann2026"}
  - {id: "lead-tutor", img: "images/renders/cohort-black.jpg", name: "Lead Tutor", text: "Practise electrode localization and receive feedback against expert localizations.", link: "/helpsupport/learn-lead-dbs-yourself/", manual: "Self-tutoring|/manual/lead-dbs/self-tutoring-with-lead-tutor/", papers: "madan2025"}
layout: "showcase"
---

{{< jumps "Single patients|#single-patients; Groups of patients|#groups-of-patients; In the operating theatre|#operating-theatre; Tools|#tools" >}}
{{< /jumps >}}

{{% chapter n="1" %}}
## Single patients {#single-patients}

**Where the electrodes sit,** and what they stimulate.
{{% /chapter %}}

{{< capabilities >}}
{{< capability title="Registration and normalization" id="normalization" img="images/renders/cohort-top.jpg"
    manual="Volume registrations|/manual/lead-dbs/step3-volume-registrations/"
    papers="ewert2019 oxenford2024" >}}
Normalize patient images to [MNI space](/about-the-mni-spaces/) and refine the normalization manually with WarpDrive.
{{< /capability >}}

{{< capability title="Electrode localization" id="localization" img="images/renders/lead-closeup.jpg"
    manual="Reconstruction of electrode trajectories|/manual/lead-dbs/step5-optional-reconstruction-of-electrode-trajectories/"
    papers="horn2015 husch2018" >}}
Electrodes on postoperative MRI or CT, detected automatically or placed by hand.
{{< /capability >}}

{{< capability title="Stimulation modelling" id="stimulation" img="images/renders/pathway-activation.jpg"
    manual="Calculate VTA and stats|/manual/lead-group/calculate-vta-and-stats/"
    papers="butenko2020 zimmermann2026" >}}
Models the electric field, activated tissue and pathways for a stimulation setting, with [OSS-DBS](#oss-dbs).
{{< /capability >}}

{{< capability title="Visualization" id="visualization" img="gallery/edlow2019_fig7_panela.png" fit="contain"
    manual="Visualization|/manual/lead-dbs/step7-visualization/"
    papers="horn2015" >}}
Electrodes, atlases, fibre tracts and stimulation volumes in 2D and 3D.
{{< /capability >}}

{{< capability title="Connectivity" id="connectivity" img="/helpsupport/knowledge-base/lead-dbs-methods/connectivity-benefit-mapping/cbm1-1030x676.png" fit="contain"
    alt="Functional connectivity profiles of the DBS sites of 12 patients on cortical surfaces"
    manual="Connectomics|/manual/connectomics/connectomic-analyses/"
    papers="horn2016" >}}
A stimulation site's connections, from the patient's own or a [normative connectome](/helpsupport/knowledge-base/atlasesresources/normative-connectomes/).
{{< /capability >}}

{{< capability title="AC/PC to MNI conversion" id="acpc" link="/helpsupport/knowledge-base/lead-dbs-methods/acpc-to-mni-conversion-2/"
    img="/helpsupport/knowledge-base/lead-dbs-methods/acpc-to-mni-conversion-2/fig_3.png" fit="contain"
    alt="DBS targets of nine indications, from Parkinson’s disease to addiction, as heat maps on slices of the MNI template with the surrounding structures labelled"
    papers="horn2017acpc" >}}
Surgical AC/PC coordinates to MNI space and back.
{{< /capability >}}
{{< /capabilities >}}

{{% chapter n="2" %}}
## Groups of patients {#groups-of-patients}

**Relate electrode placement and stimulation** to clinical outcomes across patients in a common space.
{{% /chapter %}}

{{< capabilities >}}
{{< capability title="Group analysis and sweet spots" id="group" img="gallery/li2020_fig1.png" fit="contain"
    manual="Group analyses|/manual/lead-group/group-analyses-with-lead-dbs/; Sweetspot Explorer|/manual/lead-group/sweetspot-explorer/"
    papers="treu2020 neudorfer2023" >}}
Maps which stimulation sites go with better or worse outcomes.
{{< /capability >}}

{{< capability title="Network mapping and fibre filtering" id="network-mapping" link="/helpsupport/knowledge-base/lead-dbs-methods/connectivity-benefit-mapping/"
    img="gallery/li2020_fig4_top.png" fit="contain"
    manual="Connectomics|/manual/connectomics/connectomic-analyses/"
    papers="horn2017ana neudorfer2023" >}}
Identify connections associated with clinical outcomes and build models to predict outcomes in new patients.
{{< /capability >}}

{{< capability title="Electrophysiology mapping" id="sem" link="/helpsupport/knowledge-base/lead-dbs-methods/subcortical-electrophysiology-mapping-sem/"
    img="/helpsupport/knowledge-base/lead-dbs-methods/subcortical-electrophysiology-mapping-sem/betaalpha3d.png" fit="contain"
    alt="Beta and alpha peaks within the STN in 3D, with electrode trajectories"
    manual="Group analyses|/manual/lead-group/group-analyses-with-lead-dbs/"
    papers="horn2017hbm" >}}
Recordings from many patients, pooled into one 3D map.
{{< /capability >}}
{{< /capabilities >}}

{{% chapter n="3" %}}
## In the operating theatre {#operating-theatre}

**Map recordings and model test stimulation** on patient images in real time.
{{% /chapter %}}

{{< capabilities >}}
{{< capability title="Lead-OR" id="lead-or" link="/about/lead-or/" img="gallery/oxenford2022_fig1.jpg" fit="contain"
    manual="Lead-OR: imaging setup|/manual/lead-or/imaging-setup/"
    papers="oxenford2022" >}}
A sister tool for research during surgery, in [3D Slicer](https://www.slicer.org/) ([SlicerNetstim](https://github.com/netstim/SlicerNetstim)).
{{< /capability >}}
{{< /capabilities >}}

{{% chapter n="4" %}}
## Tools {#tools}

{{% /chapter %}}

{{< tools >}}

