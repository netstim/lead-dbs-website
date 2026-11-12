---
title: "About the MNI spaces"
date: "2016-07-27T19:04:01"
lastmod: "2022-02-04T19:48:23"
# A background article, first published as a news post; it keeps its address.
url: "/about-the-mni-spaces/"
description: "The versions of the “MNI space” since MNI305 and Colin27, how they differ, and why the difference matters for DBS imaging."
showDate: true
keywords: ["MNI", "MNI space", "MNI152", "ICBM 2009b", "template", "coordinates", "normalization"]
# the picture shown when the page is shared (head.html)
share: "MNI6thgenvs2009-poster.jpg"
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - "/helpsupport/knowledge-base/lead-dbs-methods/acpc-to-mni-conversion-2/"
  - {name: "Registration and normalization", url: "/helpsupport/knowledge-base/lead-dbs-methods/#normalization"}
  - "/helpsupport/knowledge-base/atlasesresources/distal-atlas/"
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/helpsupport/knowledge-base/atlasesresources/atlases-2/", text: "The atlases that work with Lead-DBS"}
  - {page: "/helpsupport/knowledge-base/atlasesresources/", text: "Parcellations, connectomes and more"}
---

There is no single “MNI space”: there are several MNI templates, and they differ slightly. In fMRI or
diffusion MRI the differences rarely matter; in DBS imaging, where millimetres matter, they can change
results. Lead-DBS uses the ICBM 2009b nonlinear asymmetric template.

| Template | What it is | Contrasts | Used by |
| --- | --- | --- | --- |
| MNI152 NLIN 6th generation | 152 brains, nonlinearly registered into MNI305 space | T1 | SPM and FSL (FSL in an asymmetric version) |
| MNI152 NLIN 2009b | The same 152 brains registered again in 2009, at 0.5 mm: the most detailed | T1, T2, PD | Lead-DBS (asymmetric version) |
| Colin27 | One brain, scanned 27 times; a high-resolution version followed in 2008 | T1 (2008: T1 and T2) | SPM96 |
{.table--stack caption="Three MNI templates in short"}

{{< notice >}}The [BIDS appendix on coordinate systems](https://bids-specification.readthedocs.io/en/latest/99-appendices/08-coordinate-systems.html), published after this article, is a more complete reference, including which spaces SPM and FSL use.{{< /notice >}}

## Why the template matters {#space-or-template-what-is-the-difference}

The MNI “space” only defines the boundaries around the brain, in millimetres from a set origin. Depending
on the template, one coordinate can end up in a different anatomical structure. With smoothing kernels of
up to 8 × 8 × 8 mm and fMRI voxels of 3 × 3 × 3 mm this rarely matters; in DBS imaging millimetres do,
and Lead-DBS is built to account for that as well as possible (one reason why its output folders can be
large).

{{< clip src="MNI6thgenvs2009.mp4" poster="MNI6thgenvs2009-poster.jpg" alt="Axial slice of the MNI template, comparing the 6th generation and 2009 versions" caption="The clip fades between the 6th generation template (the fuzzier image, used by SPM and FSL) and the 2009b T1 template (the sharper one, used by Lead-DBS)." >}}

Over the whole brain the difference looks small, but
small subcortical structures such as the GPi and STN can move noticeably from one template to the other.

So report the template, not just the “space”. Many papers say “standard space” or “MNI space” only, which
usually means one of the 6th generation 152 templates supplied with SPM or FSL; but even “MNI 152 space”
leaves open which of the three 152 templates was used, and within the 2009 series which of six (2009a,
2009b or 2009c, each symmetric or asymmetric).

## Lead-DBS and the 2009b template

Lead-DBS uses the MNI 2009b NLIN asymmetric T2 template as its primary definition of anatomy. The 6th
generation templates were never an option: they have no T2 version, and the most common DBS target is
the STN, for which most centres acquire T2-weighted images before and after surgery.

Most MNI resources, however, exist only in 6th generation space, because SPM and FSL use it. With the
help of Vladimir Fonov from the MNI we estimated a nonlinear warp from 6th generation MNI T1 to 2009b
NLIN space, [publicly available on figshare (2)](https://figshare.com/articles/MNI_T1_6thGen_NLIN_to_MNI_2009b_NLIN_ANTs_transform/3502238).
It is based on T1 images only (again, there is no T2 version of the 6th generation templates), and it
gives accurate results. Since Lead-DBS v1.4.9.4 it has been applied to the resources listed below.

{{< clip src="bb2mni2009b.mp4" poster="bb2mni2009b-poster.jpg" alt="Axial BigBrain histology slice registered to the MNI 2009b template" caption="The clip fades between subcortical structures of the BigBrain 2015 release at 100 µm and the MNI/ICBM 152 2009b NLIN asymmetric template." >}}

<details class="more">
<summary>The resources transformed into 2009b space</summary>

- Subcortical atlases (found under /lead_dbs/atlases/)
  - ATAG_Linear (Keuken 2014)
  - ATAG_Nonlinear (Keuken 2014)
  - ATAG_STN (Forstmann 2012 & Keuken 2013)
  - Oxford Thalamic Connectivity Atlas (Behrens 2003)
  - BGHAT (Prodoehl 2008)
  - CFA Subcortical Shape Atlas (Qiu 2010)
  - Harvard AAN atlas (Edlow 2012)
- Templates (found under /lead_dbs/templates/)
  - mni_hires_fa.nii (which is the [FMRIB FA58 template](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FMRIB58_FA))

</details>

<details class="more" id="what-is-2009b-safe-in-lead-dbs">
<summary>What is “2009b safe” in Lead-DBS</summary>

- In our view, the transformed atlases mentioned above are in good agreement with the 2009b template
- The DISTAL and Human Motor Thalamus Atlases were created for Lead-DBS and are inside the correct space.
- The Accolla STN subdivision atlas has been defined on the 2009 MNI space
- Nonlinear deformations using Advanced Normalization Tools (ANTs) within Lead-DBS are 100% 2009b conform (they use the template itself)
- SPM New Segment uses a segmentation of the ICBM2009b template performed based on the Lorio 2016 (3) enhanced TPM maps that have been graciously provided for use within Lead-DBS by Bogdan Draganski. Thus, this normalization routine perfectly conforms to the 2009b template.
- Similar to the above, DARTEL & SHOOT implementations within Lead-DBS use this novel TPM automatically built by Lead-DBS.

</details>

<details class="more" id="what-may-not-be-exactly-in-2009b-space">
<summary>What may not be exactly in 2009b space</summary>

- Atlases not mentioned in the above lists or atlases you added yourself to Lead-DBS. In case they had been originally co-registered to 6th generation templates, you may consider [applying the transform (2)](https://figshare.com/articles/MNI_T1_6thGen_NLIN_to_MNI_2009b_NLIN_ANTs_transform/3502238).
- Whole-brain parcellation maps used for connectomic imaging (in lead_dbs/templates/labeling) have not been modified. We argue that the slight differences on cortical structures between 6th gen MNI space and 2009 MNI space will not yield significantly different results in whole-brain connectometric analyses and did not apply any transform to these files. In our view, they are still good to use.

</details>

## A short history of the MNI templates

From MNI305, the first MNI template, to the 2009 series, and the related spaces of SPM, FSL, FreeSurfer
and the Human Connectome Project. Largely after Matthew Brett's
[post](http://www.nil.wustl.edu/labs/kevin/man/answers/mnispace.html) and
[review paper](http://www.nature.com/nrn/journal/v3/n3/abs/nrn756.html) (1), which focused on the
differences between Talairach and MNI space.

<details class="more">
<summary>Show the templates one by one</summary>

- [MNI305](http://nist.mni.mcgill.ca/?p=957): 305 normal MRI brains were linearly coregistered (9-param) to 241 brains that had been coregistered (roughly) to the Talairach atlas. This was the first MNI template. It is T1 only.
- [Colin27 original](http://nist.mni.mcgill.ca/?p=935): Colin Holmes, a lab member of the MNI, was scanned 27 times. This was used as the standard template in SPM96. This template was matched to the MNI305. In the original release, only a T1 template was available.
- [MNI152 linear](http://nist.mni.mcgill.ca/?p=798): 152 normal images were linearly coregistered (9-param) to the 305 space. This was adopted to define standard anatomy by the International Consortium of Brain Mapping (ICBM) and is used by SPM from version 99 on. Only a T1 template is available.
  - **SPM:** Note that in later iterations, SPM defined its own “space” based on scans acquired within the [IXI dataset](https://brain-development.org/ixi-dataset/), leveraging on the concept of segmentation-based normalizations (as applied in the [Unified Segmentation](http://cslras.pbworks.com/f/Unified%20Segmentation.pdf), [DARTEL](https://pubmed.ncbi.nlm.nih.gov/17761438/) and [SHOOT](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3221052/) approaches). This space, [referred to as the IXI549Space](https://bids-specification.readthedocs.io/en/latest/99-appendices/08-coordinate-systems.html) is largely similar to MNI152 and of similar resolution (where it’s likely safe to say that differences do not matter as much for most applications). Along the same lines, both spaces are unsuitable for use in DBS imaging, in our opinion. More in the [BIDS coordinate systems appendix](https://bids-specification.readthedocs.io/en/latest/99-appendices/08-coordinate-systems.html).
- [MNI152 NLIN 6th generation](http://nist.mni.mcgill.ca/?p=858): Here, the 152 brains were nonlinearly registered into 305 space. Again, only a T1 template is available.
  - **FSL:** The FSLR is an adapted version of this space but in its asymmetric flavor (MNI152NLIN6Asym, hence different to the official [one provided here](http://nist.mni.mcgill.ca/?p=858)). The template also provides surface coordinates references. More in the [BIDS coordinate systems appendix](https://bids-specification.readthedocs.io/en/latest/99-appendices/08-coordinate-systems.html).
- [Colin27 hires T1/T2 version (2008)](http://nist.mni.mcgill.ca/?p=947): The MNI also released a high-resolution version of the Colin27 space.
- [MNI152 NLIN 2009](http://nist.mni.mcgill.ca/?p=904): Finally, in 2009, the MNI released an updated version after again nonlinearly co-registering the 152 acquisitions. This template exhibits the best resolution and detail to date and is available in T1, T2, PD and T2-relaxometry versions. It has not (yet) been adopted by SPM or FSL though and its anatomy is slightly different in direct comparison to the 6th generation templates. Moreover, it comes in three versions (two of which are explicitly mentioned here) that each have a symmetric and asymmetric subversion:
  - MNI152 NLIN 2009a: Probably the official new template in 1 × 1 × 1 mm resolution. It comes in T1, T2, PD and T2-relaxometry versions. There is a symmetric and an asymmetric version (latter not featuring T2-relaxometry).
  - MNI152 NLIN 2009b: The only of the novel templates available in 0.5 × 0.5 × 0.5 mm resolution. It is available in a T1, T2 and PD version. Due to the high resolution of this template, **it has been adopted by Lead-DBS as the primary anatomy template**. Lead-DBS uses the asymmetric version of this template.
- There are more [MNI templates for different species and different cohorts](http://nist.mni.mcgill.ca/?p=947).
- Within the world of Freesurfer, the [fsaverage](https://surfer.nmr.mgh.harvard.edu/fswiki/FsAverage) space has been roughly / approximately coregistered to MNI space (see the [FreeSurfer coordinate systems page](https://surfer.nmr.mgh.harvard.edu/fswiki/CoordinateSystems), thanks to Denise Ruprai) but is based on different subjects (as far as I know based on the Buckner40 dataset which has become part of the [genomics superstruct repository](http://neuroinformatics.harvard.edu/gsp/)).
  - Thomas Yeo’s lab has [published a paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6239990/) about accurate conversions between MNI and freesurfer space, [their code is openly available](https://github.com/ThomasYeoLab/CBIG).
- Finally, the [Minn/Wash-U Human Connectome Project](https://www.humanconnectome.org/) nonlinearly registered 900 of their subjects into MNI 152 6th-generation space, i.e. into the space used by SPM/FSL. Their templates are high in detail and especially subcortically may exceed the signal to noise contrast of the MNI 2009 versions. They are – however – in a slightly different space as the 2009 versions (namely in 6th-gen space).

</details>

Downloads: the [official MNI templates](http://nist.mni.mcgill.ca/?page_id=714) and the [HCP templates](https://www.humanconnectome.org/data/).

## References

(1)  Brett, M., Johnsrude, I. S., & Owen, A. M. (2002). The problem of functional localization in the human brain. *Nature Reviews Neuroscience*, *3*(3), 243–249. http://doi.org/10.1038/nrn756

(2) Horn, Andreas (2016): MNI T1 6thGen NLIN to MNI 2009b NLIN ANTs transform. figshare. <https://dx.doi.org/10.6084/m9.figshare.3502238.v1>

(3) Lorio, S., Fresard, S., Adaszewski, S., Kherif, F., Chowdhury, R., Frackowiak, R. S., et al. (2016). New tissue priors for improved automated classification of subcortical brain structures on MRI. *NeuroImage*, *130*, 157–166. http://doi.org/10.1016/j.neuroimage.2016.01.062
