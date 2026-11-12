---
{
  "title": "Coregister Volumes",
  "linkTitle": "Coregistration",
  "layout": "manual",
  "weight": 12,
  "manual_group": "lead-dbs",
  "description": "Align pre-operative and post-operative images in the same space, then inspect the registration.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-dbs/step3-volume-registrations/coregister-volumes",
  "manual_title": "Coregister Volumes",
  "manual_lead": "Align pre-operative and post-operative images in the same space, then inspect the registration."
}
---

## Coregister the images

1. Load your patient folder in BIDS format into Lead as described in [Load a patient](/manual/lead-dbs/step1-load-patient-folder/).
2. Select the patient you want to register in the window on the left (arrow 1).
3. Select `Coregister Volumes` and `Check Results`, so you can see the output of coregistration (arrows 2 and 3).
4. If coregistration has been run before, select `Retouch/overwrite approved results` (arrow 4) to get a new instance of coregistration results.
5. Press `Run`. The processing power of your computer determines the duration of the coregistration step.
6. To see how to check your results, consult [Checking the Coregistration and Normalization](/manual/lead-dbs/step3-volume-registrations/checking-the-coregistration/).

![Annotated coregistration interface: arrow 1 selects the patient, arrows 2 and 3 enable Coregister Volumes and Check Results, and arrow 4 marks Retouch/overwrite approved results.](manual/16d44d8d6ed46fdd.png "Coregistration controls: patient selection (1), registration (2), result checking (3) and overwrite (4).")

<details>
<summary>View the full interface</summary>

![Lead-DBS interface with the patient list on the left, Coregister Volumes and Check Results under Registration, and the Run button below.](manual/afd466e6511205b8.png "Lead-DBS registration controls in the main window.")

</details>

### Output

A pop-up lists the methods and references used. You can close it after reviewing the information. The coregistration data are saved under {{< manual-path "derivatives/leaddbs/patient_name/coregistration/" >}}.

## How coregistration works

### Registration methods

By default, Lead-DBS uses SPM for MRI-to-MRI coregistration and ANTs for MRI-to-CT coregistration. You can change these settings in the GUI. Available methods include SPM, ANTs, FSL, Brainsfit and customized ANTs presets.

Coregistration aligns images with linear transformations. It can shift, scale and skew an image, but does not expand one region while shrinking another.

### Reference image and resolution

The pre-operative T1-weighted MRI is the reference image. If no T1 is available, Lead-DBS uses the T2-weighted MRI instead.

Lead-DBS checks the reference image's resolution before registration. If a voxel dimension exceeds 1 mm on any axis, the image is upsampled; missing intensity values are interpolated from surrounding values. Other pre-operative scans are aligned to the reference first, followed by the post-operative data.

### Check the alignment

Coregistration is crucial to electrode localization. Check that the images align throughout the volume using Lead-DBS or an additional viewer such as [3D Slicer](https://www.slicer.org/). See [Checking the Coregistration and Normalization](/manual/lead-dbs/step3-volume-registrations/checking-the-coregistration/) for the inspection workflow.

## Realign to AC-PC

This option allows to realign the anchor image (i.e., preoperative T1w MRI) to the AC-PC plane. This pre-processing step is fully optional and has been implemented as a legacy function of LeGUI.

### Select the landmarks

1. Select `realign to AC-PC` and click `Run`.
2. A pop-up window will open. Scroll over the different slices to find the anatomical landmarks (AC, PC and midsaggital point).
3. Use right click to mark **in order** the AC (green dot), PC (red dot), and a midsaggital point (blue dot). Use a midsaggital point close to the superior brain edge, anywhere between the AC and PC points on the antero-posterior axis. Typically, axial view works best to place the AC and PC, and coronal view works best to place the midsaggital point.
4. If needed, adjust the cropping box to skin edge.
5. Close window to save and indicate whether you wish to crop the image.

![Coregister Volumes — screenshot](manual/7ce82ec22dc004fc.png)

{{% manual-note "info" %}}
Note that the realign to AC-PC step overwrites the corresponding image in the preprocessing > anat folder. For this reason, if used, it should be run before the image registration steps (coregistration, normalization).
{{% /manual-note %}}
