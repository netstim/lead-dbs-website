---
headRender: false
title: "Atlases and data"
description: "Brain atlases, parcellations and normative connectomes in MNI space that work with Lead-DBS, and where to get them."
date: "2017-04-08T22:50:27"
lastmod: "2026-11-12"
weight: 6
keywords: ["atlas", "atlases", "connectome", "connectomes", "parcellation", "data", "resources"]
# the picture shown when the page is shared (head.html)
share: "images/renders/cohort-black.jpg"
# a hub page: its tiles use the full width, no sidebar
# "Related" at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/develop/#add-your-atlas-or-dataset", name: "Add your atlas or dataset"}
# the rows under "Templates and practice data" (layouts/_shortcodes/link-rows.html)
other:
  - {name: "About the MNI spaces", text: "Template versions and coordinate spaces", url: "/about-the-mni-spaces/"}
  - {name: "IXI dataset", text: "Age-matched reference for AC/PC to MNI conversion", url: "/helpsupport/knowledge-base/lead-dbs-methods/acpc-to-mni-conversion-2/#ixi"}
  - {name: "Lead Tutor", text: "Practice electrode localization", url: "/helpsupport/learn-lead-dbs-yourself/"}
layout: "hub"
---
<div class="page-intro"><div class="page-intro__text">

**Brain atlases and connectivity datasets** in MNI space.

</div></div>

<div class="notice" role="note">

**Included for reproducibility.** Lead-DBS includes published atlases and datasets so that the studies
behind them can be reproduced. Inclusion is not an endorsement, and the team cannot vet every resource.
Read the original paper before using an atlas or connectome, and check which template space it was built
for ([About the MNI spaces](/about-the-mni-spaces/)).

</div>

{{< atlas-hub >}}

{{% hub-section %}}
## Templates and practice data {#other-data}

{{< link-rows key="other" >}}
{{% /hub-section %}}
