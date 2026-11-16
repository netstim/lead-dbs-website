---
{
  "title": "Reconstruction file",
  "linkTitle": "Reconstruction file",
  "layout": "manual",
  "manual_group": "lead-dbs",
  "description": "Understand the data stored in the electrode reconstruction file.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-dbs/step5-optional-reconstruction-of-electrode-trajectories/reconstruction-file",
  "manual_lead": "Understand the data stored in the electrode reconstruction file."
}
---

This page might be outdated. We continuously work on updating our documentation, thank you for your patience.

The data is stored

* for the BIDS version, under {{< manual-path "derivatives/leaddbs/patientID/reconstructions/sub-patientID_desc-reconstruction.mat" >}}
* for the classic version, under the `ea_reconstruction.mat` file inside the patient directory.

There is a single variable `reco`.

`reco.native` stores reconstruction in native postoperative space, `reco.scrf` is after subcortical refine (brainshift correction - if it was applied) and `reco.mni` stores the reconstruction in the MNI space.

`reco.native.coords_mm` stores the coordinates for electrode contacts. For instance, `reco.native.coords_mm{2}(3,:)` is the left (`{2}`) third lowest (`(3,:)`) contact coordinates in x, y, z in native postoperative space.

The indexing of the contacts usually follows **the same order as defined by the lead manufacturer**, starting from the bottom. **For segmented contacts**, different manufacturers may have different order definitions. For example, at level 2 of the directed electrode from Boston Scientific (Fig. 1), the order is 2 -> 3 -> 4 (counter-clockwise seen from top). But for Abbott, it’s 1A -> 1B -> 1C (clockwise seen from top) (Fig. 2).

![Figure 1: order of directed electrodes from Boston Scientific.](manual/831f1eaaa172f561.png "Figure 1: order of directed electrodes from Boston Scientific.")

![Figure 2: Abbott directional lead organization.](manual/00c4437e5e9d2cff.png "Figure 2: Abbott directional lead organization.")
