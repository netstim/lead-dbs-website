---
{
  "title": "Registration",
  "linkTitle": "Registration",
  "layout": "manual",
  "manual_group": "lead-dbs",
  "description": "Align patient images, normalize them to a template and inspect the results.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-dbs/step3-volume-registrations",
  "manual_lead": "Align patient images, normalize them to a template and inspect the results.",
  "keywords": [
    "3. Volume Registrations"
  ]
}
---

First steps in the Lead-DBS pipeline.

![3. Volume Registrations — screenshot](manual/105ed15df60fdffd.png)

First, Lead-DBS coregisters preoperative and postoperative images. MR images are coregistered to MR images by default with SPM. Postoperative CT images are coregistered to preoperative MR images with ANTs (red arrow number 1).

Second, you can choose to normalize the volumes to the MNI nonlinear 2009b space with ANTs (red arrow 2). The ANTs settings are optimized for the subcortex, see [Ewert et al. (2019)](https://doi.org/10.1016/j.neuroimage.2018.09.061). With a multi-core computer, you can increase the number of threads to reduce computation time. To do this, select **Settings**. Find more information [about the MNI spaces](https://www.lead-dbs.org/about-the-mni-spaces/). For more information about templates and other normalization methods, see [Normalizing the images](/manual/lead-dbs/step3-volume-registrations/normalization-of-images/).

Third, brainshift correction is recommended to improve lead localization (red arrow 3). Due to the lead implantation, brain shift is highly likely, that is, the brain moves with respect to the skull. Find more information about the correction in [Brainshift correction](/manual/lead-dbs/step3-volume-registrations/subcortical-refine-post-to-pre-transforms/).

Finally, you can approve, recalculate or reject the registration and normalization results visually by ticking **Check Results**. **WarpDrive** allows for fine manual adjustments to better match, for instance, an atlas fit of the subthalamic nucleus with the patient-specific nucleus (red arrows 4 & 5). See the [WarpDrive documentation](https://github.com/netstim/SlicerNetstim/tree/master/WarpDrive) for more information.

The following subpages provide more technical detail.
