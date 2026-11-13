---
{
  "title": "Imaging setup",
  "linkTitle": "Imaging setup",
  "layout": "manual",
  "weight": 45,
  "manual_group": "lead-or",
  "description": "Prepare imaging data for use with Lead-OR.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-or/imaging-setup",
  "manual_title": "Imaging setup",
  "manual_lead": "Prepare imaging data for use with Lead-OR."
}
---

Imaging setup to use the Lead-OR platform

## Requirements

1. **3D Slicer:** [3D Slicer](https://download.slicer.org/) (v >= 5.2.2) together with the SlicerNetstim, SlicerOpenIGTLink and SlicerIGT extensions should be installed.
2. **ORScene:** An *ORScene* is a file that includes subject images, planning information and atlas-based segmentations ready to loaded into Slicer. It can be created from Lead-DBS and an example dataset is already included in the SlicerNetstim extension.

## Loading sample ORScene

A sample ORScene is included to test the platform. To load it follow the next steps:

1. Open Slicer.
2. Switch to Sample Data module.
3. Scroll down and select STN Planning.

See the following screenshots as reference:

![Step 2: Switch to Sample Data module.](manual/b89a3b90a855b011.png "Step 2: Switch to Sample Data module.")

![Step 3: Select STN Planning ORScene.](manual/96c8764ca7ca375e.png "Step 3: Select STN Planning ORScene.")

## Creating new ORScene

In order to create an ORScene follow the next steps:

1. Process a subject in Lead-DBS with the **co-registration** and **normalization** steps.
2. Place the surgical planning files under a `leador` subfolder within the subject folder.
3. Load the subject in Lead-DBS and select `Tools > Lead-OR > Create ORScene`. Note that the selected atlas will be put into the scene as well.
4. Drag and drop the `ORScene.mrb` file into Slicer.

See the following screenshots as reference.

![Step 2: Lead-DBS subject processed and with Brainlab planning files in respective folder.](manual/c66db91386815122.png "Step 2: Lead-DBS subject processed and with Brainlab planning files in respective folder.")

![Step 3: Create ORScene from Lead-DBS.](manual/7de596d0d56e50f8.png "Step 3: Create ORScene from Lead-DBS.")

![Step 4: Output folder with file to load into Slicer.](manual/b0b596b80bcb318b.png "Step 4: Output folder with file to load into Slicer.")
