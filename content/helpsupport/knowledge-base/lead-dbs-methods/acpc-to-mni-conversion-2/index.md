---
title: "AC/PC to MNI conversion"
date: "2017-04-19T17:07:12"
lastmod: "2017-04-23T17:23:14"
---

Our methods paper on AC/PC to MNI conversion has been summarized in the following resources:

{{< button href="/dbs-targets-in-mni-space/" >}}Read our blog post explaining AC/PC to MNI conversions in detail here{{< /button >}}

{{< button href="http://www.lead-dbs.org/docs/talks/AAN_presentation_Horn_2017.pdf" >}}A brief talk held at AAN 2017 can be found here{{< /button >}}

Furthermore, the methodology is described in the paper listed below.

> [Horn, A., Kühn, A. A., Merkl, A., Shih, L., Alterman, R., & Fox, M. (2017). Probabilistic conversion of neurosurgical DBS electrode coordinates into MNI space. *NeuroImage*, *150*, 395–404.](http://doi.org/10.1016/j.neuroimage.2017.02.004)

The methodology is implemented in the *AC/PC conversion tool* supplied within Lead-DBS.

![](lead_acpc-1030x884.png)

*Tools menu used to open the AC/PC to MNI conversion tool*

![](acpc_mni_conversion_tool-1030x481.png)

*AC/PC to MNI coordinate conversion tool as implemented in Lead-DBS. The warps are based on selected subjects/patients that must be normalized using Lead-DBS first. Alternatively, the open license [IXI-Dataset](http://brain-development.org/ixi-dataset/) may be used to perform conversions and Lead-DBS will selected subjects matched for age as described in [Horn et al. 2017](http://doi.org/10.1016/j.neuroimage.2017.02.004).*
