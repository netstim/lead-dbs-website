---
{
  "title": "Group visualization",
  "linkTitle": "Group visualization",
  "layout": "manual",
  "manual_group": "lead-group",
  "description": "Display electrode reconstructions and stimulation volumes across your cohort.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-group/group-visualization",
  "manual_lead": "Display electrode reconstructions and stimulation volumes across your cohort."
}
---

Adapted from the walkthrough tutorial by Svenja Treu. See the [original tutorial (PDF)](https://ars.els-cdn.com/content/image/1-s2.0-S1053811920305048-mmc1.pdf).

## 2D visualization of electrodes as point clouds coloured by group {#1-2d-visualization-of-electrodes-as-point-clouds-colored-by-group}

![Example image of 2D visualization by group. Adapted from S. Treu et al., 2020.](manual/d3d4d106b9f46285.png "Example image of 2D visualization by group. Adapted from S. Treu et al., 2020.")

![Figure 1a](manual/33e3dbeb3598a932.png "Figure 1a")

1. In the main Lead Group GUI, select all the patients you want to visualize.
2. In the visualization options, select **show active contacts** (additionally **show passive contacts**, if preferred).
3. Under **2D options** > **Settings**, you can adjust the backdrop from the dropdown menu (Figure 1b). Try 7T Ex vivo 100um Brain Atlas (Edlow et al., 2019). Select **Save and close**.

   ![Figure 1b](manual/645db61c4f418cbe.png "Figure 1b")

4. Select **Visualize 2D**. The results will also be saved under the {{< manual-path "leadgroup/groupanalysisname/export/2D" >}} folder.

   ![2D visualization output](manual/891c12586a75b410.png)

## 3D visualization {#2-3d-visualization}

1. Select all the patients you want to visualize.
2. Select **Settings** under **3D Options**. Here you can find options for electrode rendering. It is possible to visualize point clouds and solid or transparent electrodes. An example of each is given in [3D visualization examples](#3d-visualization-examples). Select **Save**.

   ![3D Options settings window](manual/2d8a066ffcca1e15.png)

3. Select **Visualize 3D**. Three new windows will pop up: electrode scene, atlas settings and anatomy slices. From the anatomy slices window, you can select the backdrop of your choice and adjust slice position. From atlas settings, you can choose which atlas structures to display. From the electrode scene window you can adjust the camera angle, lighting of the scene and colours of individual atlas structures.

### 3D visualization examples

![Point clouds. Groups are represented by different colours. GPe is shown blue, STN and GPi are displayed in grey.](manual/2ce102cf882e5dbf.png "Point clouds. Groups are represented by different colours. GPe is shown blue, STN and GPi are displayed in grey.")

![Transparent electrodes with the Highlight Active Contacts option.](manual/6057255a215ce446.png "Transparent electrodes with the Highlight Active Contacts option.")

![Solid electrodes.](manual/889506b7d3ee294d.png "Solid electrodes.")

## Clinical regressors {#3-clinical-regressors}

### Point clouds, coloured by regressor {#31-point-clouds-colored-by-regressor}

![3.1. Active contacts coloured by regressor intensity.](manual/2f180ee22f1f9140.png "3.1. Active contacts coloured by regressor intensity.")

* From **3D Settings**, select point clouds and check the box **color by regressor**. This box can only be checked if point clouds are selected.

  ![Color by regressor option in 3D Settings](manual/58549cad13a4e648.png)

* Preferences for the colormaps can be edited by selecting **Colormap** in **3D Settings**.

![Colormap preferences](manual/dd8d5f85b7cb736c.png)

### Map regressor as interpolated point mesh {#32-map-regressor-as-interpolated-point-mesh}

![Fig. 3.2. The regressor mapped to an equidistant point grid after solving a scattered interpolant based on the original values and active coordinates.](manual/b0473dc604baf4d0.png "Fig. 3.2. The regressor mapped to an equidistant point grid after solving a scattered interpolant based on the original values and active coordinates.")

* Under **3D Visualization Settings**, check the box **Map regressor to Coords**.
* Uncheck the box **Show Active Contacts**.
* In **3D options**, select **Visualize regressor as: Interpolated point mesh**.

![Interpolated point mesh settings](manual/488492e9906f9dc3.png)

### Map regressor as isosurface {#33-map-regressor-as-isosurface}

![Fig. 3.3. The equidistant grid in the previous step can be thresholded and visualized as a 3D surface.](manual/4d03be92259ea37b.png "Fig. 3.3. The equidistant grid in the previous step can be thresholded and visualized as a 3D surface.")

* From **3D settings**, select **Visualize regressor as: isosurface**.
* In the group folder you can then find the resulting surfaces as NIfTI files, named after the regressor and one for each hemisphere.

## References

* Treu, Svenja, Bryan Strange, Simon Oxenford, Wolf-Julian Neumann, Andrea Kühn, Ningfei Li, and Andreas Horn. “Deep Brain Stimulation: Imaging on a Group Level.” NeuroImage 219 (October 1, 2020): 117018. [doi:10.1016/j.neuroimage.2020.117018](https://doi.org/10.1016/j.neuroimage.2020.117018).
