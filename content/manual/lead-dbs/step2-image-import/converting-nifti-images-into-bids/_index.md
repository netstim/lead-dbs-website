---
{
  "title": "Converting NIfTI-images into BIDS",
  "linkTitle": "NIfTI to BIDS",
  "layout": "manual",
  "manual_group": "lead-dbs",
  "description": "Organize existing NIfTI images in a Lead-DBS BIDS dataset.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-dbs/step2-image-import/converting-nifti-images-into-bids",
  "manual_lead": "Organize existing NIfTI images in a Lead-DBS BIDS dataset."
}
---

## Prepare NIfTI images {#toc95749082}

In the following steps, Lead-DBS converts the legacy NIfTI images into Brain Imaging Data Structure (BIDS) images. BIDS is a data structure for neuroimaging and behavioural data used in the imaging domain.

This step is necessary to ensure that Lead-DBS can work with the data. Moreover, using BIDS is an easy way to store and re-use the data between various toolboxes.

{{% manual-note "info" %}}
- **Make sure that one folder stores all of your patient data, that data are in NIfTI format, and the file names do not contain any spaces or special characters.**
- The folder should contain **pre-operative anat files and post-operative postop files**.
- CT files cannot be used as pre-operative data, MRI files are used instead.
{{% /manual-note %}}

![Patient folder containing NIfTI files](manual/2eb2da674aae3e49.png "Screenshot 1. Patient file - NIfTI")

To start the importing process, select **Import NIfTI to BIDS dataset** and select **Run**. It is possible to import multiple patient files by holding Shift and selecting multiple patients.

![Import NIfTI to BIDS dataset option in the Lead-DBS main window](manual/27dbe0ab0c8a6e78.png)

A window will pop up where you need to **specify the session (preop or postop), type (anat, functional, dwi), modality and acquisition (sag, cor, axial, iso)**.

![Window for specifying session, type, modality and acquisition of each NIfTI file](manual/80009c10869c34dd.png)

Here is another example with postoperative CT scans.

![The same window with postoperative CT scans](manual/6f0734214e0498e0.png)

### Output

* After Lead-DBS migrated all NIfTI files into BIDS format, you can find them in the selected output folder (dataset directory). In our case, the folder’s name was “Directory”.
* The folder contains three main subfolders: “derivatives”, “rawdata” and "sourcedata". Each of these contains data about our patients. The raw images that we have just converted will be stored under the **"rawdata/sub-\[PATIENTNAME]”** folder. Lead-DBS will use these data for further analysis.
* The `dataset_description` file contains information about your dataset.

![Dataset directory after the conversion, with derivatives, rawdata and sourcedata folders](manual/538ba67202e47acd.png)
