---
{
  "title": "Command line options",
  "linkTitle": "Command line options",
  "layout": "manual",
  "weight": 55,
  "manual_group": "appendix",
  "description": "Look up the flags used to select processing steps and methods from the command line.",
  "source_url": "https://netstim.gitbook.io/leaddbs/appendix/command-line-interface/command-line-options",
  "manual_title": "Command line options",
  "manual_lead": "Look up the flags used to select processing steps and methods from the command line."
}
---

| Option                       | Description                                                                                                                                                                                                                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-dicomcheck`                | **Import DICOM series**                                                                                                                                                                                                                                                         |
| `-coreg_checkbox`            | **Run coregistration**                                                                                                                                                                                                                                                          |
| `-coregctmethod`             | **CT to MRI coregistration method**                                                                                                                                                                                                                                             |
| `-coregmrpopup`              | **MRI to MRI coregistration method**                                                                                                                                                                                                                                            |
| `-normalize_checkbox`        | **Run normalization**                                                                                                                                                                                                                                                           |
| `-normmethod`                | <p><strong>Normalization method</strong></p><p>1: SPM SHOOT</p><p>2: SPM Segment</p><p>3: SPM Dartel</p><p>4: three step affine</p><p>5: MaGeT Brain like segmentation</p><p>6: MaGet Brain like normalization</p><p>7: FSL FNIRT</p><p>8: Re-Apply</p><p>9: ANTs (default)</p> |
| `-scrf`                      | **Run Brain Shift Correction**                                                                                                                                                                                                                                                  |
| `-scrfmask`                  | **Brain Shift Correction method**                                                                                                                                                                                                                                               |
| `-extractsurface`            | **Run extract surface**                                                                                                                                                                                                                                                         |
| `-surcafemethod`             | **Extract surface method**                                                                                                                                                                                                                                                      |
| `-doreconstruction_checkbox` | **Run pre-Recontruct algorithm**                                                                                                                                                                                                                                                |
| `-reconmethod`               | **pre-Recontruct method**                                                                                                                                                                                                                                                       |
| `-manualheight_checkbox`     | **Manual localization of DBS electrodes**                                                                                                                                                                                                                                       |
| `-render_checkbox`           | **Open 3D viewer**                                                                                                                                                                                                                                                              |
