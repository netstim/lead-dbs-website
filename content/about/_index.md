---
title: "About"
date: "2014-06-17T15:06:49"
lastmod: "2023-08-22T09:53:56"
---

Lead-DBS is an open-source MATLAB toolbox for deep brain stimulation (DBS) imaging: it reconstructs DBS electrodes from postoperative MRI and CT, visualizes them in 2D and 3D, analyses electrode placement across patient groups, simulates stimulation and estimates its connectivity to other brain regions.

It was started at the Movement Disorders Unit of Andrea Kühn, Department of Neurology, Charité – Universitätsmedizin Berlin. Since 2016 it has been developed by researchers from several institutions, and since 2019 the work has been coordinated by the Network Stimulation Laboratory led by Andreas Horn, which in May 2025 became the [Institute for Network Stimulation](https://www.netstim.org) at the University Hospital Cologne.

The current release is Lead-DBS {{< release version >}}, released on {{< release date >}}. Developer meetings are planned monthly and listed on the [events page](/events/); to take part, see [Develop Lead-DBS](/develop/).

{{< notice id="research-use" >}}**For research use only.** Lead-DBS is research software for retrospective scientific analysis; it is not intended for diagnosis, treatment planning or any other clinical decision about an individual patient. The full statement is on the [download page](/download/#research-use).{{< /notice >}}

## Prerequisites

To work with Lead-DBS you need postoperative (and if available preoperative) structural MRI, or postoperative CT and preoperative MRI. It runs in MATLAB {{< release matlab >}} or later with a few MATLAB toolboxes and SPM12; the [download page](/download/) lists everything, and the [installation guide in the manual](https://netstim.gitbook.io/leaddbs/installation) explains the setup.

## Development Team

This list is being updated. Names and affiliations below date from 2023 or earlier and may be out of date. Everyone who has contributed code is shown in the [contributors graph on GitHub](https://github.com/netstim/leaddbs/graphs/contributors).

### Core Development

- [Ningfei Li](https://www.netstim.org/about-us/about-us/), Charité Berlin
- [Simón Oxenford](https://www.netstim.org/about-us/about-us/), Charité Berlin
- Till Dembek, University of Cologne
- Nanditha Rajamani, Charité Berlin
- Konstantin Butenko, Harvard Medical School
- Garance Meyer, Harvard Medical School
- Enrico Opri, Emory University, Atlanta
- Johannes Achtzehn, Charité Berlin
- Andreas Husch, University of Luxembourg
- Lauren Hart, Harvard Medical School
- Khoa Nguyen, University of Bern
- Kavisha Fernando, University of Melbourne
- [Andreas Horn](https://www.netstim.org/about-us/about-us/andreashorn/), Institute for Network Stimulation, University Hospital Cologne

### Feature Development

- Andrea Kühn, Charité, Germany
- Harald Treuer, University of Cologne
- Veerle Visser-Vandewalle, University of Cologne
- Todd Herrington, Mark Richardson, Massachusetts General Hospital, Boston
- Frank Hertel, Centre Hospitalier de Luxembourg

### Contributors (Code)

- Wolf-Julian Neumann, Charité Berlin
- Jan Roediger, Charité Berlin
- Johannes Vorwerk, University of Münster
- Ari Kappel, University of Pittsburgh
- Chadwick Boulay, University of Ottawa
- Qianqian Fang, Northeastern University, Boston

### Contributions of Atlases / Data from following authors

- Siobhán Ewert, Charité, Germany
- Ettore Accolla, University of Fribourg
- Erik Middlebrooks, Mayo Clinic, Jacksonville
- Bogdan Draganski, University of Lausanne
- Brian Edlow, Martinos Center / MGH, Boston
- Lingzhong Fan, Chinese Academy of Sciences
- Birte Forstmann / Max Keuken, University of Amsterdam
- Alexander Hammers, Imperial College London
- Marc Joliot / Natalie Tzourio-Mazoyer, University of Bordeaux
- Antonio Meola, Brigham and Women’s Hospital, Boston
- Janey Prodoehl, Midwestern University
- Anqi Qiu, National University of Singapore
- Verena Rozanski, University of Munich
- Thomas Yeo, National University of Singapore
- Dongyang Zhang, Washington University, St. Louis
- Eduardo Alho, University of Sao Paulo

### Testing

- Pierre Deman, Astrid Kibleur, Grenoble Institut des Neurosciences
- Juan Carlos Baldermann, University Hospital Cologne
- Kristen Kanoff, Massachusetts General Hospital, USA
- Konrad Schumacher, University Hospital Freiburg

**Please feel free to join the team!** See [Develop Lead-DBS](/develop/) for how to contribute, or [fork us on GitHub](https://github.com/netstim/leaddbs).

---

## Lead-DBS Downloads Across the Globe

[![Map of the world with the countries Lead-DBS was downloaded from marked in blue (opens the map on ipinfo.io)](image-1536x614.png "Historical snapshot of a download map from the old website. It is undated and no longer updated.")](https://ipinfo.io/tools/map/a5760510-a7df-4fc0-b9b4-996b85965ff4)

---

## Alternatives

DBS imaging involves a complex pipeline spanning several disciplines such as precise co-registration, multimodal image fusion, 3D image processing & localization, spatial statistics, surface & volumetric meshing as well as physical modeling using the finite element approach.

If incorporating connectivity measures, it expands to functional magnetic resonance imaging and diffusion-weighted imaging based tractography. Finally, electrophysiological measures such as local field potentials and electro-/magnetoencephalographic data may be incorporated to better understand DBS and enhance DBS modeling.

Thus, creating a “one-step solution” for DBS imaging is a non-trivial task. Although we aim at incorporating the best tools that are openly available for each sub-task into the Lead-DBS pipeline and constantly work hard to improve our tool, alternatives exist (with slight differences in focus) that may be better suited to specific subtasks of the whole collection. Below is a non-exhaustive list of alternatives we are aware of. It has not been reviewed for some years, so some of these tools may have changed or been discontinued. Also see our [blog post on academic vs. commercial software tools](/commercial-vs-academic-software/) or the discussion of our [Lead-DBS v.2 paper](https://www.researchgate.net/publication/327380509_Lead-DBS_v2_Towards_a_comprehensive_pipeline_for_deep_brain_stimulation_imaging).

- **Academic endeavors / Open source tools**
  - DBSproc ([Lauro 2016](http://onlinelibrary.wiley.com/doi/10.1002/hbm.23039/abstract)), openly available, part of the [AFNI imaging suite](https://afni.nimh.nih.gov/afni/)
  - ELMA ([Johansson 2019](https://pubmed.ncbi.nlm.nih.gov/31947033/)), openly available [here](https://liu.se/en/research/dbs)
  - PyDBS ([D’Albis ‎2015](https://www.ncbi.nlm.nih.gov/pubmed/24799270)), available to the ACouStiC community
  - [PaCER](https://adhusch.github.io/PaCER/), developed in Luxembourg (also a part of Lead-DBS)
  - StimVision ([Noecker 2021](https://onlinelibrary.wiley.com/doi/abs/10.1111/ner.13350)), developed at Case Western University
  - DBSmapping ([Moreira da Silva 2015](https://ieeexplore.ieee.org/document/7146617/?tp=&arnumber=7146617&openedRefinements%3D*%26filter%3DAND(NOT(4283010803))%26pageNumber%3D11%26rowsPerPage%3D100%26queryText%3D(3d%20user%20interfaces)metadata)), developed by a group in Porto
  - There is a similar software at MGH, described in [Bonmassar 2014](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4334388/)
  - The CiceroneDBS ([Miocinovic 2007](https://www.ncbi.nlm.nih.gov/pubmed/17691348), discont.) software which had similar aims made its way into the Boston Scientific GUIDE software (see below)
- **Commercial products**
  - [Boston Scientific GUIDE XT](https://news.bostonscientific.com/2013-05-27-Boston-Scientific-Receives-CE-Mark-Approval-For-GUIDE-DBS-System) software, now a commercial alternative
  - Commercial tools under the name [Optivise](http://www.trademarkia.com/optivise-85498999.html) (discont.) and [SureTune](https://neuronewsinternational.com/ce-mark-granted-to-medtronic-for-suretune2-deep-brain-stimulation-therapy/) are/were available at Medtronic
  - CranialCloud, developed by the spinoff Neurotargeting LLC out of Vanderbilt University

## Citing Lead-DBS
Please find out how to [best cite Lead-DBS if you use it on this page](/about/citing_leaddbs/).
