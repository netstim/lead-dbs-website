---
{
  "title": "Reconstruction statistics",
  "linkTitle": "Reconstruction statistics",
  "layout": "manual",
  "manual_group": "lead-dbs",
  "description": "Read the electrode, atlas, stimulation and connectivity statistics exported by Lead-DBS.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-dbs/reconstruction-statistics",
  "manual_lead": "Read the electrode, atlas, stimulation and connectivity statistics exported by Lead-DBS."
}
---

Lead-DBS exports statistics about your electrode reconstructions during

* 3D visualization
* Simulation of stimulations (calculation of the volume of activated tissue and fibre connectivities).

During both processes, a file named `ea_stats.mat` is written out in MATLAB which can be used within your own analysis pipelines or together with the group analysis GUI `lead_group`. The structure of the variable file is as follows:

## Contact distances

* `conmat`: An *m* × *n* matrix showing the distance between the centre of each contact (*m* electrodes contacts numbered from K0 (right hemisphere) upwards) and the closest voxel within the *nth* atlas. Corresponding atlas names can be found in the file, as well (see below). These values are never zero, even if the electrode contact resides within the atlas. This is due to the fact that both voxels and electrode contacts are represented as mathematical points and these are "never" exactly identical. Thus, to answer the question about whether a contact resides within a certain nucleus, you have to either define a distance threshold yourself, or try to work with one of the following two entries.
* `conmat_inside_vox`: A copy of `conmat`, where all entries are set to zero that show a smaller distance than the voxel resolution of the according atlas. This matrix can be used to see whether a contact resides surely within a certain atlas.
* `conmat_inside_hull`: Another copy of `conmat`, where all entries are set to zero for the condition that the centre of an electrode contact resides within the concave hull of a certain nucleus. This is only valid for the *centre* of each contact. If the centre of an electrode contact is close to the border of the nucleus, the contact might still reside "within" the nucleus without the entry of this matrix being zero. Taken together, for binary classifications, our advice is to analyse data with the pure `conmat` and defining your own reasonable threshold that tells you whether a contact is "within" or "outside" a certain nucleus.

## Patient and atlas information

* `patname`: The name/pseudonym of the analysed patient.
* `atlases`: Information about the atlases used.
  * `names`: The names of the atlases. You can use this list for referencing all stats entries. As an example, entry (5,6) of `conmat` described above shows the distance between contact
  * `types`: The types of atlas. Types can be the following:
    * *1*: Right hemispheric atlas, that is, one that is *only* present in the *atlases/youratlasset/rh* directory.
    * *2*: Left hemispheric atlas, that is, one that is *only* present in the *atlases/youratlasset/lh* directory.
    * *3*: An atlas that is present for both hemispheres and is composed of two files with the exact same name, one lying in the *atlases/youratlasset/lh* and one in the *atlases/youratlasset/rh* directory.
    * *4*: An atlas that is present for both hemispheres but is read-in only from one file residing within the *atlases/youratlasset/mixed* directory. When processed, these atlases are divided along the *x = 0 mm* (midsagittal) plane into two compartments.
    * *5*: An atlas that shows a midline structure, that is, one that is not being divided along the *x = 0 mm* plane. These atlases can be used for structures around the midsagittal plane, such as the subcallosal cortex or Broca's area 25.
* `colormap`: A colormap used for visualization. You can change the colormap from within the `lead` GUI by pressing the colormap button, selecting a colormap and re-running the 3D visualization step.

## Electrode reconstruction

`electrodes`: A structure with information about the reconstruction. This is the same information as can be found in the `ea_reconstruction.mat` file within the patient folder, namely:

* `coords_mm`: A (usually) 1 × 2 cell filled with n × 3 matrices denoting the coordinates of each electrode contact in millimetres (within MNI space). The first cell accounts for the right electrode, the second one for the left electrode. Within each matrix, the first row accounts for the ventralmost contact. For example, `ea_stats.electrodes.coords_mm{2}(3,:)` accounts for the coordinates of the third-ventralmost contact on the left hemisphere, often referred to as `K10` (or sometimes as `K6`).
* `trajectory`: A (usually) 1 × 2 cell filled with n × 3 matrices, each describing a coordinate list of the reconstructed trajectory. Points on these lines should be equidistant and on a straight line.
* `name`: The name/pseudonym of the patient.

## Stimulation volumes

`vat`: Information about volumes of activated tissue (VAT). Each struct in here has the following fields:

* `U`: The voltage applied to build this VAT in V.
* `Im`: The impedance measured while stimulating, in Ω.
* `Contact`: The electrode contact where this VAT found its origin. An entry \[1 2] would refer to right (1) contact number 2, that is, the second-ventralmost right contact, usually referred to as `K1`. \[2 2] would be its left counterpart `K9`/`K5`.
* `Side`: Whether the contact was left or right (redundant with the first entry in the `Contact` field).
* `AtlasIntersection`: The 1 × n matrix in this field estimates how many cubic millimetres of tissue of each nucleus got stimulated by the generated VAT (n := number of atlases in the set). If the second entry in this matrix amounts to a value of 8.7, this means that according to the simulation, 8.7 cubic millimetres of the second atlas (as labeled by `ea_stats.atlases.names{2}`) was stimulated by this particular VAT.

## Fibre tracking

`ft`: A structure accounting for fibertracking-related statistics.

* `fibercounts`: A n × 1 matrix accounting for how many fibres connected the VAT to the n structures within the particular labeling atlas.
* `labels`: A n × 1 cell with the names of the labeling atlas.
* `vatsused`: refers to the VATs used for this fibre-tracking analysis. If you have more than one struct of `ft`, this can be used to keep track of which analysis was which.

## Analysis history

`vatanalyses`: A meta-structure keeping track of the analyses performed. For example, if this structure has three entries, three analyses have been performed. In theory, this could also be used to keep track of stimulation settings that may change over time for a certain patient. In `lead_group`, the *Analysis* listbox refers to the last entry in `vatanalyses`, if it is set to 0. It refers to the second-last entry if it is set to -1, and so forth. This way, more than one VAT/Fibertracking analyses can be stored for each patient and analysed separately with `lead_group`.

* `vatsused`: Which entries of the `ea_stats.vat` structure have been used in this particular analysis.
* `fibersused`: Which entries of the `ea_stats.ft` structure have been used in this particular analysis.
