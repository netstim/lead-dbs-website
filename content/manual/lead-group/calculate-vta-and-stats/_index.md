---
{
  "title": "Calculate VTA and stats",
  "linkTitle": "VTAs & statistics",
  "layout": "manual",
  "manual_group": "lead-group",
  "description": "Calculate stimulation volumes and the statistics used in group analyses.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-group/calculate-vta-and-stats",
  "manual_lead": "Calculate stimulation volumes and the statistics used in group analyses."
}
---

To calculate stats and VTA, select **Calculate stats & VTA** in the main GUI.

![Calculate stats & VTA button in the Lead Group main GUI](manual/a1bc5085e9f27d32.png)

This will calculate the VTAs and electrical fields for both hemispheres for each patient, in native and in MNI space. The generated files will be stored under the `stimulations` folder of each patient. An example of the folder structure is displayed below:

![Example stimulations folder structure](manual/4a406bb74d86813a.png)

## Explore stats

After calculating VTA and stats, Lead Group provides statistical tests for group comparison. It is possible to see which electrode contacts reside within an anatomical atlas structure, to calculate the distance of contacts to an anatomical atlas structure, to generate correlation plots between a clinical variable and the intersection of contacts with a structure.

![Figure 3: Explore Stats](manual/5ebf43850a73f948.png "Figure 3: Explore Stats")

### Calculate distance between VTA and an anatomical atlas structure

1. Select **Explore Stats** under the **Calculate Stats & VTA** section in the main GUI.
2. From the window that pops up (Fig. 3), choose the subcortical region you're interested in. If the structure you're interested in is not on the list, you can change the subcortical atlas from the main GUI under **General Settings**.
3. From the **Activated regions** menu, choose VTAs or E-fields.
4. Select **Generate Target Report**. From the pop-up window, select the threshold you want to use in mm.
5. Two windows will pop up, one showing the distances of electrode centers to the nearest voxel of the target and one showing electrode centers residing in the target structure based on the selected threshold. Active contacts will be highlighted in red.

![Target report windows with contact distances and contacts inside the target](manual/0d73a721957a8b74.png)

{{% manual-note "info" %}}
Since the distance to the closest voxel of a target is rendered, **even if the electrode contact is in the middle of the target structure, the distance to the shell of the target will be listed**. Thus, a visual check of the contact positions is recommended!
{{% /manual-note %}}

### Correlate variable and VTA intersection

1. Select **Explore Stats** under the **Calculate Stats & VTA** section in the main GUI.
2. From the window that pops up (Fig. 3), choose the variable and subcortical region of your interest. If the structure you're interested in is not on the list, you can change the subcortical atlas from the main GUI under **General Settings**.
3. From the **Activated regions** menu, choose VTAs or E-fields.
4. Select **Correlate Variable and VTA Intersection**. This will generate correlation plots (Fig. 4), showing the correlation between VTA and target intersection and the clinical variable of choice.

![Figure 4: correlation plot between VTA-target intersection and a clinical variable](manual/65fa76ef835334e0.png "Figure 4")
