---
{
  "title": "Converting DICOM files into BIDS",
  "linkTitle": "DICOM to BIDS",
  "layout": "manual",
  "manual_group": "lead-dbs",
  "description": "Convert DICOM imaging data into the BIDS layout used by Lead-DBS.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-dbs/step2-image-import/converting-dicom-files-into-bids",
  "manual_lead": "Convert DICOM imaging data into the BIDS layout used by Lead-DBS."
}
---

## Prepare DICOM images {#toc96000786}

Original patient imaging data are usually stored in the DICOM format. In the following steps, we will convert DICOM files into BIDS. The process is essentially similar to converting NIfTI to BIDS. However, DICOM files are first converted to NIfTI and then to BIDS.

{{% manual-note "info" %}}
- Make sure that one folder stores all of your patient data, and the file names do not contain any spaces or special characters.
- Your patient’s folder should contain all the images in DICOM format (pre-operative structural T1-weighted and T2-weighted MRI and post-operative CT or MRI) (Screenshot 23).
{{% /manual-note %}}

![Patient folder containing DICOM files](manual/e2c455f93ded2a92.png "Screenshot 23. Patient file - DICOM")

### Convert the images {#toc96000788}

1. Select the patient that you want to convert from the main Lead-DBS GUI.
   1. From the **Import** section, select **Import DICOM to BIDS dataset**.
   2. Select the DICOM conversion tool you'd like to use.
   3. Select **Run**.
2. Lead-DBS will convert DICOM into NIfTI files, and a new window will appear. This is a new step we have not seen when converting NIfTI to BIDS (Screenshot 25).
   1. What you need to do here is to fill out the table using the drop-down menu and choose from the options (Screenshot 25B).
   2. In the **Session** column, choose whether the data are post-operative or pre-operative.
   3. The **Type** column is anat for both pre-and post-operative data.
   4. The **Modality** column is T1w and T2w for pre-operative data, and for post-operative data, you use CT (in this case) or MRI.
   5. The **Acquisition** section is filled automatically.

![Import section of the main Lead-DBS GUI](manual/5095da917daf45dc.png "Screenshot 24. Import section of the main Lead-DBS GUI")

![Table for assigning session, type, modality and acquisition during the conversion to BIDS](manual/560356499bb46e00.png "Screenshot 25. Lead-DBS to BIDS conversion")

### Output {#toc96000789}

1. This time, three folders appeared in the output directory (Screenshot 26).
2. Source data contain the original DICOM files.
3. Raw data contain raw NIfTI files with pre-operative and post-operative data.
4. The derivatives folder contains the main output from the processing tool.

![Dataset directory after the conversion, with sourcedata, rawdata and derivatives folders](manual/c1459cd6d618f506.png "Screenshot 26. Lead-DBS to BIDS conversion")
