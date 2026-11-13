---
{
  "title": "Load a patient",
  "linkTitle": "Load a patient",
  "layout": "manual",
  "weight": 6,
  "manual_group": "lead-dbs",
  "description": "Load your dataset, select patients and configure electrode information.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-dbs/step1-load-patient-folder",
  "manual_title": "1. Load Patient Folder",
  "manual_lead": "Load your dataset, select patients and configure electrode information.",
  "keywords": [
    "1. Load Patient Folder"
  ]
}
---

![1. Load Patient Folder — screenshot](manual/629516e0e009eed7.png)

Click on `Choose Dataset Directory` at the top of the main window to select the folder you would like to save your data to.

{{% manual-note "info" %}} **The name of this dataset directory should contain ONLY alphanumeric characters, but NO special characters, including underscores. It is also strongly recommended to**** *****not***** ****use reserved words such as**** *****leaddbs*****,**** *****lead\_group*****,*****derivatives***** ****as the name of the dataset directory**.
{{% /manual-note %}}

The name should reflect the project you are working o&#x6E;*.* You can use a folder already in BIDS format or select an empty folder. If you select an empty folder, Lead-DBS will automatically create 3 subfolders **(derivatives, rawdata, sourcedata)** and a json file **(dataset\_description.json)** within that folder. The resulting dataset folder should look like this:

![An example folder in BIDS format.](manual/31d46ac3a2399369.png "An example folder in BIDS format.")

**To add patients** to your dataset, click on the button shown below. Select the patient folder you want to add from the pop-up window. It is possible to hold shift and select multiple patients to import. Patient folders should contain preoperative and postoperative brain images. These files can be in DICOM, nifti or BIDS format.

![Add patients](manual/e91e679960bfa492.png "Add patients")

![Patient selection - it is possible to select multiple patients to import.](manual/a48021a69580bc28.png "Patient selection - it is possible to select multiple patients to import.")

You can use the additional buttons shown below to remove patients, rename patients and to add additional nifti or DICOM images to the patients folder.

If your images are not in BIDS format, the folder will be highlighted in red as shown below. You need to convert the patient files to BIDS format from **0. Import** section, which is explained in the next section.

![1. Load Patient Folder — screenshot](manual/47b32dc1a044a662.png)

**In the dropdown menu, select the electrode model and the number of electrodes.** By default, `R` and `L`are selected, i.e., a bilateral implantation in the right and left hemispheres is assumed. For some applications such as epilepsy, more electrodes may be applicable.

To analyze images, Lead-DBS needs **at least** the following views:

* for MR images, a post-operative image (at least a transversal view)
* for CT images, a post-operative acquisition plus a pre-operative MR image.

These images should be in the selected patient folder. **You may have more views and sequences available**, in which case electrode localization is made easier, more robust and more precise. These images can be in DICOM or NIfTI format. Lead-DBS needs to convert DICOM images into NIfTI (.nii) format as described in the [next step](/manual/lead-dbs/step2-image-import/).

You can use the up and down arrows in this part to select the previous or next patient folder. For instance, you may have a folder `cohort`with patient folders `patient001`through to `patient010`and would like to move up or down between patient folders. The dropdown menu `Recent patients` provides quick access to recently analyzed patient folders.

The indicator at the bottom notifies whether a postoperative MR or CT image was detected. This can be changed with the [next step](/manual/lead-dbs/step2-image-import/) after importing and renaming images.

{{% manual-note "info" %}}
If you are using LeGUI check the SEEG box, you do not need to set an electrode model and number of electrodes at this stage. This will be set within LeGUI later on.
{{% /manual-note %}}
