---
{
  "title": "Customizing atlas visualization",
  "linkTitle": "Customizing atlas visualization",
  "layout": "manual",
  "manual_group": "appendix",
  "description": "Adjust atlas colours, labels and structure selections for visualization.",
  "source_url": "https://netstim.gitbook.io/leaddbs/appendix/acquiring-and-setting-atlases/customizing-atlas-visualization",
  "manual_lead": "Adjust atlas colours, labels and structure selections for visualization."
}
---

Atlases need to be installed inside the `lead_dbs/atlases` directory (to do so, see [Acquiring and installing atlases](/manual/appendix/acquiring-and-setting-atlases/)).

Once installed, Lead-DBS will create a small file called `atlas_index.mat` inside the atlas directory upon the first 3D-visualization of the atlas. Inside this file, all the tesselation info of the whole atlas-set is stored, allowing for a faster visualization the next time. In principle, only this file is needed for visualization. If you make changes to the actual atlas files, make sure to delete this file so that it will be rebuilt the next time.

## Changing atlas colours

Inside the file, you can also change the colour information of the atlas set by modifying the `atlases.color` field of the struct inside MATLAB. Choose colour intensities from 1 to 64 which will be converted to a real colour value based on the colormap you choose upon visualization. To change the colormap, you can press the colormap button before starting the 3D-visualization.

## Changing atlas thresholds

Atlases are visualized by showing an isosurface of the actual atlas files. This means that the surface that is being visualized goes through all atlas points with the same intensity. In binary atlases, the whole atlas is always displayed by default. For probabilistic atlases, a change of intensities might be needed. To do so, you can again load the `atlas_index.mat` file inside the atlas directory once it has been generated (after the first visualization using the atlas). To change the thresholds to be applied, you need to modify the `atlases.threshold` field of the `atlases` struct variable.

Several threshold possibilities are available which can be set as a string variable in `atlases.threshold.type` – make sure that you write the string exactly as mentioned below.

* *relative intensity* (default): Here, one value from >0 to 0). A value of 0.5 sets the intensity to half of the maximum value detected.
* *relative intensity vector*: Here, the same as above applies, but you can set one value for each component of the atlas. See the `atlases.names` field to see how many components Lead-DBS detects and how they are called.
* *absolute intensity*: Here, the absolute intensity value can be entered and is applied to all components of the atlas set.
* *absolute intensity vector*: Same as above applies, but you can set one value for each component of the atlas. See the `atlases.names` field to see how many components Lead-DBS detects and how they are called.
* *percentage*: Here, a percentage of all atlas voxels are shown. Set a value between 0 and 1 (to show no or 100% of the atlas voxels). This can be different to an absolute/relative intensity, depending on the distribution of intensities within the atlas.
* *percentage vector*: Same as above applies, but you can set one value for each component of the atlas. See the `atlases.names` field to see how many components Lead-DBS detects and how they are called.
