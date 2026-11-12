---
{
  "title": "Using the platform",
  "linkTitle": "Using the platform",
  "layout": "manual",
  "weight": 47,
  "manual_group": "lead-or",
  "description": "Work with the Lead-OR interface after completing imaging and electrophysiology setup.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-or/using-the-platform",
  "manual_title": "Using the platform",
  "manual_lead": "Work with the Lead-OR interface after completing imaging and electrophysiology setup."
}
---

An overview of the Lead-OR platform using the sample data mentioned in the imaging and electrophysiology setup pages.

1. Open Slicer and load the sample STN planning as mentioned in the [imaging setup](/manual/lead-or/imaging-setup/) page.
2. Open OpenEphys and build a signal chain as mentioned in the [electrophysiology setup](/manual/lead-or/electrophysiology-setup/) page.
3. In Slicer, switch to the Lead-OR module, create a new IGTLConnector and set it to active. Select the Planning transform node.

![Using the platform — screenshot](manual/51ff829f224ec88d.png)

4. In OpenEphys, select IGTLink from the Lead-OR module and connect. Click on Start acquisition.

![Using the platform — screenshot](manual/3efa20b8903479ea.png)

5. Signal streaming will start and will be processed through the different plug-ins. The Lead-OR module in OpenEphys will send the distance to target, together with processed features to Slicer. In Slicer, recording channels will appear and they should be linked to their respective trajectories. This is done by first clicking the channel name and then the desired trajectory.

![Using the platform — screenshot](manual/eba4690e9dfc792f.png)

6. The features sent by OpenEphys also appear in Slicer, where they can be set to map to the Tube's radius and/or color.

That's all! A few more tips:

* Use the Reslice driver button next to distance to target transform selector to set the view inplane with the trajectory.
* Explore different trajectory visualizations: model, line and tip.
* When created by Lead-DBS different planning transforms will be available to select.
