---
title: "DISTAL atlas"
description: "The DISTAL atlas (Ewert et al. 2018): a subcortical atlas in MNI space built from multimodal MRI, histology and structural connectivity."
linkTitle: "DISTAL atlas"
date: "2017-08-09T18:24:26"
lastmod: "2026-11-11"
weight: 4
# the picture shown when the page is shared (head.html)
share: "distal_fig_6-1030x728.png"
# the atlas at a glance (layouts/_shortcodes/cells.html; text: Markdown)
glance:
  - {label: "Targets", value: "STN, GPi, GPe, RN and more"}
  - {label: "Thalamus", value: "Three nomenclatures"}
  - {label: "Space", value: "MNI ICBM 2009b"}
  - {label: "Version", value: "1.1"}
# the three stages it was built in
stages:
  - {label: "Stage 1", value: "Segment the core nuclei", text: "STN, red nucleus, internal and external pallidum, on the four MRI contrasts of the template."}
  - {label: "Stage 2", value: "Warp histology to the template", text: "A histological atlas, with these nuclei as anchor points, fills in the other structures."}
  - {label: "Stage 3", value: "Divide by connectivity", text: "The STN and GPi are divided into functional zones by their structural connectivity."}
# "Related" at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/helpsupport/knowledge-base/atlasesresources/atlases-2/"}
  - {page: "/helpsupport/first-steps/"}
layout: "showcase"
---

<div class="page-intro"><div class="page-intro__text">

**A subcortical atlas made for Lead-DBS,** built from multimodal MRI, histology and structural connectivity.

</div>
<p class="page-intro__actions"><a class="btn btn--primary" href="{{< relref `/download/` >}}">Download Lead-DBS</a><a class="btn btn--secondary btn--ext" href="https://doi.org/10.1016/j.neuroimage.2017.05.015">Read the paper<span class="ext-mark" aria-hidden="true">↗</span><span class="sr-only"> (another site)</span></a></p>
</div>

![The final DISTAL atlas in 3D with labelled structures and a DBS electrode](distal_fig_9-1030x501.png)
{.atlas-hero}

{{< cells key="glance" label="DISTAL at a glance" >}}

{{% hub-section %}}
## What it is

**Every structure relevant to DBS surgery,** precisely on the MNI template.

It is coregistered to the ICBM 2009b nonlinear asymmetric template ([about the MNI spaces](/about-the-mni-spaces/)),
and its thalamic nuclei come in three nomenclatures, with their abbreviations. In the picture above,
structures in red were defined on the multimodal template itself, those in black from histology; blue text
names the functional zones of the STN and GPi, from structural connectivity.
{{% /hub-section %}}

{{% hub-section %}}
## How to get it {#download}

**Installed with Lead-DBS,** as its default atlas set.

Inside the Lead-DBS folder it is under `templates/space/MNI152NLin2009bAsym/atlases/`, in the atlas sets
*DISTAL Minimal (Ewert 2017)*, the default, and *DISTAL Nano (Ewert 2017)*. Choose it from the atlas list
of the 3D viewer, where presets show, for instance, only the structures relevant to DBS, or the functional
zones of the STN and GPi.
{{% /hub-section %}}

{{% hub-section %}}
## How it was built

**In three stages,** directly on the MNI template.

None of the atlases collected since 2012 matched the STN of the MNI template precisely, and in DBS imaging
millimetres matter.

{{< cells key="stages" label="The three stages" >}}

<details class="more more--wide">
<summary>Why an atlas made for Lead-DBS</summary>

When work on Lead-DBS was started in 2012, we began [collecting subcortical atlases](/helpsupport/knowledge-base/atlasesresources/atlases-2/) of the brain to best define anatomy. For instance, the ATAG atlas [was made freely available](https://www.nitrc.org/projects/atag) by the Forstmann group in Amsterdam.

Over the years, with growing experience, we noticed that none of the available atlases was precisely suited for use in Lead-DBS, none of them was explicitly built for our toolbox.

One limitation of most available atlases (when used in Lead-DBS) is shown in this figure:

{{% row %}}
{{% col "2/3" %}}
![Panels of the STN region on the MNI template, each overlaid with a different published STN atlas](distal_fig_1-768x1030.png)

{{% /col %}}
{{% col "1/3" %}}
*In the left upper panel you see the hypointense region of the subthalamic nucleus as defined by the [most modern MNI template available](/about-the-mni-spaces/). The region of the STN is further magnified in the next panel. Subsequent panels overlay available atlases of the STN to this region. As you can see, neither of them precisely matches the STN of the template. The reasons for this are manifold but since in DBS imaging, millimeters matter, such discrepancy really does matter.*

{{% /col %}}
{{% /row %}}
Your patient data will (if quality allows) show a similar hypointense region that defines (part) of the STN.

- If you use a nonlinear deformation algorithm (like the Advanced Normalization Tools, FSL- or SPM-based implementations in Lead-DBS) to register the hypointense region of your patient’s brain to the MNI template AND
- If data & algorithms were perfect => this would lead to the hypointense region of your patient’s brain exactly matching the STN of the template.

> If you now combine this image with an atlas that doesn’t exactly fit the MNI template, a systematic mismatch will result!

![Diagram of how a misregistered atlas leads to a wrong electrode placement model, in four steps](misplacement-1030x366.png)

*This figure further illustrates the systematic error introduced by a misplaced atlas (i.e. an atlas not precisely matching the template that is used for normalization).*

> These conclusions led us to create an atlas that is “made for Lead-DBS”

</details>

<details class="more more--wide">
<summary>The three stages, with the figures of the paper</summary>

We wanted to create an atlas that is i) very precisely aligned to the ICBM 2009b MNI template and ii) accurate enough to visualize all structures relevant for DBS surgery. This resulted in three separate stages.

### Stage 1: A multimodal region-growing algorithm applied to MNI templates
In this stage, the T1-, T2-, PD- and T2rlx weighted templates were segmented simultaneously, incorporating all information in parallel. First, a multimodel region-growing-like algorithm was applied that produced probability maps. These maps were then used to manually segment subthalamic nucleus, red nucleus, internal and external pallidum directly within the space of the template series.

{{% row %}}
{{% col "1/3" %}}
*The final result of manual segmentations that were performed directly on the MNI template using its four spectra simultaneously. These four structures i) align perfectly with the template and ii) were used as anchorpoints to warp histology to the template.*

{{% /col %}}
{{% col "2/3" %}}
![Manual segmentations of pallidum, STN and red nucleus on the MNI template, in 3D and on T1 and T2 slices](distal_fig_3-1030x624.png)

{{% /col %}}
{{% /row %}}
### Stage 2: Precise co-registration of histology, using Stage 1 as additional anchor points
To “fill the gaps” between the regions defined on the template itself, a precise histological atlas was graciously provided by Mallar Chakravarty (Douglas Institute) and Louis Collins (MNI). To align this data as precisely as possible to the MNI space, manual structures were used as additional anchorpoints in a nonlinear pseudo-MRI to template warp.

{{% row %}}
{{% col "2/3" %}}
![Comparison of histology-to-template warps without and with template-based anchor structures](distal_fig_4-1030x804.png)

{{% /col %}}
{{% col "1/3" %}}
*Conventional (left panel) and additional anchor point warp (right panel). Both warps apply multiple spectra to align histology to the template. The right warp includes an additional high signal-to-noise (binary) manual segmentation of the same structures (STN, RN, GPi/GPe) defined on histology and the template (manual anchorpoints). This leads to a very precise alignment of i) these structures and ii) structures ultimately neighboring them. Notably, these structures are the most important ones in DBS imaging.*

{{% /col %}}
{{% /row %}}

{{% row %}}
{{% col "1/3" %}}
*Comparisons of results when warping the STN as defined by histology onto the template. Top panels show the conventional approach (without additional anchor points), bottom panels the approach with additional anchorpoints, showing a clearly superior alignment to the hypointense STN region defined by the template.*

{{% /col %}}
{{% col "2/3" %}}
![STN warped from histology onto the template in three views, without (top) and with (bottom) anchor points](distal_fig_5-1023x1030.png)

{{% /col %}}
{{% /row %}}
### Stage 3: Further parcellation of core DBS targets by means of structural connectivity
The final stage was to further subdivide the primary DBS targets, namely the STN and the GPi by means of structural connectivity. This has been done in multiple studies for the STN, subdividing it into sensorimotor, associative and limbic subregions. It has not been done for the GPi, potentially given its closeness to efferent and afferent structures. We used the efferent connectivity of the GPi that projects to thalamic functional zones as they were defined in the famous [Behrens 2003](https://www.ncbi.nlm.nih.gov/pubmed/12808459) study.

{{% row %}}
{{% col "2/3" %}}
![Connectivity-based parcellation of the STN into sensorimotor, associative and limbic zones](distal_fig_6-1030x728.png)

{{% /col %}}
{{% col "1/3" %}}
*Afferent connectivity to different cortical regions defines a sensorimotor, associative prefrontal and limbic functional zone of the subthalamic nucleus. Of note, in our study, this was done with both connectivity data from healthy subjects and patients suffering from Parkinson’s disease. Results were highly similar and replicate findings published by [Accolla et al.](https://onlinelibrary.wiley.com/doi/10.1002/hbm.22533/full) and [Lambert et al.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3315017/) in humans and various studies published based on animal models (e.g. see this study by [Haynes & Haber](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3755746/))*

{{% /col %}}
{{% /row %}}

{{% row %}}
{{% col "1/3" %}}
*A similar approach was used to parcellate the GPi into seven functional zones using the Oxford thalamic connectivity atlas as seed-regions. Of note, the postero-ventral third of the nucleus corresponds to its sensorimotor functional zone, as previously published (e.g. [Cif et al.](https://www.ncbi.nlm.nih.gov/pubmed/22339165), [Tisch et al.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2095629/))*

{{% /col %}}
{{% col "2/3" %}}
![Connectivity-based parcellation of the GPi into functional zones, in 3D and on a slice](distal_fig_7-1030x343.png)

{{% /col %}}
{{% /row %}}
### Summary

{{% row %}}
{{% col "2/3" %}}
![Methods summary: the three stages of building the DISTAL atlas, with axial, coronal and sagittal results](distal_fig_8-996x1030.png)

{{% /col %}}
{{% col "1/3" %}}
*Summary of methods. The figure shows the three stages described above. First, core nuclei were manually segmented based on multimodal probability maps created directly on the MNI template. Then, these nuclei served as anchor points to register histological data that was used to fill the gaps. Finally, two core structures were further subdivided using structural connectivity.*

{{% /col %}}
{{% /row %}}

</details>

<details class="more more--wide">
<summary>Results, and DISTAL in the 3D viewer of Lead-DBS (video, 2017)</summary>

{{% row %}}
{{% col "1/3" %}}
![Lead-DBS atlas control window listing DISTAL structures and nomenclature options](Screen-Shot-2017-08-09-at-4.35.26-PM-643x1030.png)

{{% /col %}}
{{% col "3/5" %}}
*Based on the highly unique histology dataset graciously provided by our colleagues in Montreal (see above), the DISTAL atlas comes in three nomenclatures as well as their abbreviations. For people that are interested in the thalamus, this represents a rosetta stone of thalamic nomenclatures in MNI space.*

*Structures can be easily explored in the 3D viewer built into Lead-DBS and several presets are available.*

*For instance, you can choose to show “DBS relevant structures” only. Another example is to quickly turn on functional parcellations of the STN/GPi or rather show them as solid structures.*

The video below shows these features (recorded in 2017):

{{% /col %}}
{{% /row %}}
{{< vimeo id="228993216" title="The DISTAL atlas in the Lead-DBS 3D viewer (2017)" >}}

{{% row %}}
{{% col "2/3" %}}
*The DISTAL atlas significantly outperforms other published atlases when performing atlas-based segmentation within Lead-DBS.*

{{% /col %}}
{{% col "1/3" %}}
![Atlas-based STN and GPi segmentations from DISTAL, BGHAT and ATAG compared with manual segmentations](distal_fig_10-531x1030.png)

{{% /col %}}
{{% /row %}}

</details>
{{% /hub-section %}}

{{% hub-section %}}
## What to cite

**Ewert et al. 2018,** NeuroImage.

{{% copybox label="Copy the citation" %}}
{{< paper ewert2018 "full" >}}
{{% /copybox %}}
{{% /hub-section %}}

{{% hub-section %}}
## Versions {#change-log}

**The version in Lead-DBS differs slightly from the paper.**

- **1.1**, 5 February 2018: improved registration of left-hemispheric histology, symmetrized functional parcellations of the STN and GPi subregions.
- **1.0**, 9 September 2017: first release.

<details class="more">
<summary>How the atlas in Lead-DBS differs from the paper</summary>

- The core structures that serve as anchor points were segmented again by the paper's first author, with a
  deeper knowledge of the anatomy, and the connectivity-based parcellations were re-run on them (with very
  similar results).
- Histology was registered to the templates iteratively, generating new pseudo-MRIs from each warp until it
  settled, and with the PD-weighted template as a fourth spectrum.
- This was done for the left hemisphere; the right one was warped from it with the nonlinear left-to-right
  warp that Lead-DBS provides.

</details>

The version described in the paper is available on request: [write to us](/contact/).
{{% /hub-section %}}
