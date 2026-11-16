---
{
  "title": "Command line options",
  "linkTitle": "Command line options",
  "layout": "manual",
  "manual_group": "appendix",
  "description": "Look up the flags used to select processing steps and methods from the command line.",
  "source_url": "https://netstim.gitbook.io/leaddbs/appendix/command-line-interface/command-line-options",
  "manual_lead": "Look up the flags used to select processing steps and methods from the command line."
}
---

| Option | Description |
| --- | --- |
| `-dicomcheck` | Import DICOM series |
| `-coreg_checkbox` | Run coregistration |
| `-coregctmethod` | CT to MRI coregistration method |
| `-coregmrpopup` | MRI to MRI coregistration method |
| `-normalize_checkbox` | Run normalization |
| `-normmethod` | Normalization method: 1 SPM SHOOT, 2 SPM Segment, 3 SPM Dartel, 4 three step affine, 5 MaGeT Brain like segmentation, 6 MaGet Brain like normalization, 7 FSL FNIRT, 8 Re-Apply, 9 ANTs (default) |
| `-scrf` | Run brain shift correction |
| `-scrfmask` | Brain shift correction method |
| `-extractsurface` | Run extract surface |
| `-surcafemethod` | Extract surface method |
| `-doreconstruction_checkbox` | Run pre-reconstruct algorithm |
| `-reconmethod` | Pre-reconstruct method |
| `-manualheight_checkbox` | Manual localization of DBS electrodes |
| `-render_checkbox` | Open 3D viewer |
