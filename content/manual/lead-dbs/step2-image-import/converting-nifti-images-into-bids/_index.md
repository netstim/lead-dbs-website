---
{
  "title": "Converting NIfTI-images into BIDS",
  "linkTitle": "Converting NIfTI-images into BIDS",
  "layout": "manual",
  "weight": 9,
  "manual_group": "lead-dbs",
  "description": "Organize existing NIfTI images in a Lead-DBS BIDS dataset.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-dbs/step2-image-import/converting-nifti-images-into-bids",
  "manual_title": "Converting NIfTI-images into BIDS",
  "manual_lead": "Organize existing NIfTI images in a Lead-DBS BIDS dataset."
}
---

## Prepare NIfTI images {#toc95749082}
<ol>
- In the following steps, Lead DBS converts the legacy NIfTI-images into Brain Imaging Data Structure (BIDS) images.

- BIDS is a data structure for neuroimaging and behavioural data used in the imaging domain.

- This step is necessary to re-assure that the lead-DBS will be able to work with data. Moreover, using BIDS is an easy way to store and re-use the data between various toolboxes.
</ol>

| <h4 id="toc95749083">Info panel</h4>                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| <ol><li><strong>Make sure that one folder stores all of your patient data, that data are in NIfTI format, and the file names do not contain any spaces or special character</strong>s.</li><li>The folder should contain <strong>pre-operative anat files and post-operative postop files</strong>.</li><li>CT files cannot be used as pre-operative data, MRI files are used instead.</li></ol> |

Screenshot 1. Patient file - NIfTI

![Converting NIfTI-images into BIDS — screenshot](manual/2eb2da674aae3e49.png)

To start the importing process, simply select "Import NIfTI to BIDS dataset" and click "RUN". It is possible to import multiple patient files by holding shift and selecting multiple patients.

![Converting NIfTI-images into BIDS — screenshot](manual/27dbe0ab0c8a6e78.png)

A window will pop up where you need to s**pecify the session (preop or postop), type (anat, functional, dwi), modality and acquisition (sag, cor, axial, iso)**

![Converting NIfTI-images into BIDS — screenshot](manual/80009c10869c34dd.png)

Here is another example with postoperative CT scans.

![Converting NIfTI-images into BIDS — screenshot](manual/6f0734214e0498e0.png)

### Output

* After Lead migrated all NIfTI files into BIDS format, you can find them in the selected output folder/dataset directory. In our case, the folder’s name was “Directory”
* The folder contains three main sub-folders: “derivatives”, “raw data” and "source data". Each of these files contains data about our patients. The raw images that we have just converted will be stored under the **"rawdata/sub-\[PATIENTNAME]”** folder. The Lead will use these data for further analysis.
* “Dataset\_description” file contains information about your dataset.

![Converting NIfTI-images into BIDS — screenshot](manual/538ba67202e47acd.png)
