---
{
  "title": "Group Visualization",
  "linkTitle": "Group visualization",
  "layout": "manual",
  "weight": 34,
  "manual_group": "lead-group",
  "description": "Display electrode reconstructions and stimulation volumes across your cohort.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-group/group-visualization",
  "manual_title": "Group Visualization",
  "manual_lead": "Display electrode reconstructions and stimulation volumes across your cohort."
}
---

Adapted from the Walkthrough Tutorial by Svenja Treu.

The original tutorial can be found [here.](https://ars.els-cdn.com/content/image/1-s2.0-S1053811920305048-mmc1.pdf)

## 1) 2D Visualization of Electrodes as Point Clouds colored by Group

![Group Visualization — screenshot](manual/d3d4d106b9f46285.png)Example Image of 2D visualization by group. Adapted from S. Treu et al., 2020.

![Figure 1a](manual/33e3dbeb3598a932.png "Figure 1a")

1.1. In the main Lead Group GUI, select all the patients you want to visualize.

1.2. In the visualization options, select “show active contacts” (additionally “show passive contacts”, if preferred)

1.3. Under 2D options – Settings, you can adjust the backdrop from the dropdown menu. (Figure 1b) Try 7T Ex vivo 100um Brain Atlas (Edlow et al., 2019). Save and close.

![Figure 1b](manual/645db61c4f418cbe.png)

1.4. Press Visualize 2D. The results will also be saved under leadgroup/groupanalysisname/export/2D folder.

![Group Visualization — screenshot](manual/891c12586a75b410.png)

***

### 2) 3D visualization

2.1. Select all the patients you want to visualize.

2.2. Click "Settings" under "3D Options". Here you can find options for electrode rendering. It is possible to visualize point clouds and solid or transparent electrodes. An example of each is given [at the end of this section](#3d-visualization-examples). Click "Save".

![Group Visualization — screenshot](manual/2d8a066ffcca1e15.png)

2.3. Click "Visualize 3D." 3 new windows will pop up: Electrode scene, atlas settings and anatomy slices. From anatomy slices window, you can select the backdrop of your choice and adjust slice position. From atlas settings, you can choose which atlas structures to display. From the electrode scene window you can adjust the camera angle, lighting of the scene and colors of individual atlas structures.

#### 3D Visualization Examples

![Group Visualization — screenshot](manual/2ce102cf882e5dbf.png)**Point clouds.** Groups are represented by different colors. GPe is shown blue, STN and GPi are displayed in gray.

![Group Visualization — screenshot](manual/6057255a215ce446.png)**Transparent electrodes with "Highlight Active Contacts" option.**

![Group Visualization — screenshot](manual/889506b7d3ee294d.png)**Solid electrodes.**

***

### 3) Clinical Regressors

#### 3.1. Point clouds, colored by regressor

![Group Visualization — screenshot](manual/2f180ee22f1f9140.png)3.1. Active contacts colored by regressor intensity.

* From 3D Settings, select point clouds and check the box “color by regressor”. This box can only be checked if Point-Clouds are selected.
* ![Group Visualization — screenshot](manual/58549cad13a4e648.png)
* Preferences for the colormaps can be edited by clicking "Colormap" in 3D Settings.

![Group Visualization — screenshot](manual/dd8d5f85b7cb736c.png)

#### 3.2. Map regressor as interpolated point mesh

![Group Visualization — screenshot](manual/b0473dc604baf4d0.png)

Fig. 3.2. The regressor mapped to an equidistant point grid after solving a scattered interpolant based on the original values and active coordinates.

* Under 3D Visualization Settings check the box “Map regressor to Coords”
* Uncheck the box “Show Active Contacts”
* In 3D options, select “Visualize regressor as: Interpolated point mesh”

![Group Visualization — screenshot](manual/488492e9906f9dc3.png)

#### 3.3. Map regressor as isosurface

![Group Visualization — screenshot](manual/4d03be92259ea37b.png)

Fig. 3.3. The equidistant grid in the previous step can be thresholded and visualized as a 3D surface.

* From 3D settings, select “Visualize regressor as: isosurface”
* In the group folder you can then find the resulting surfaces as nifti files, named after the regressor and one for each hemisphere.

## References

* Treu, Svenja, Bryan Strange, Simon Oxenford, Wolf-Julian Neumann, Andrea Kühn, Ningfei Li, and Andreas Horn. “Deep Brain Stimulation: Imaging on a Group Level.” NeuroImage 219 (October 1, 2020): 117018. <https://doi.org/10.1016/j.neuroimage.2020.117018>.
