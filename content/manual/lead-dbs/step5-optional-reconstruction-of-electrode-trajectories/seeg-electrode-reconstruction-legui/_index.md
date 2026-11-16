---
{
  "title": "SEEG electrode reconstruction (LeGUI)",
  "linkTitle": "SEEG reconstruction",
  "layout": "manual",
  "manual_group": "lead-dbs",
  "description": "Reconstruct SEEG electrodes using LeGUI within Lead-DBS.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-dbs/step5-optional-reconstruction-of-electrode-trajectories/seeg-electrode-reconstruction-legui",
  "manual_lead": "Reconstruct SEEG electrodes using LeGUI within Lead-DBS."
}
---

SEEG electrode reconstruction and labelling using LeGUI.

Lead-DBS supports SEEG electrode reconstruction, labelling, and visualization through integration of the LeGUI software by Davis et al. Read the [paper describing the legacy version of LeGUI](https://pubmed.ncbi.nlm.nih.gov/34955721/).

The LeGUI pipeline consists of 3 main steps:

1. Automatic contact detection (**Auto Elec**) and manual corrections
2. Electrode contact labelling (**Assign Electrodes**) through a semi-automatic algorithm
3. (Optional) Electrode re-alignment (**Align Lead**).

To start LeGUI, select **LeGUI (Davis 2021)** in the pre-reconstruction method drop-down menu.

## LeGUI main window

![LeGUI main window with the 2D view on the left, the 3D view on the right and the toolbar at the top](manual/e24763c277c4f2a3.png)

The LeGUI main window consists of a left panel showing the preoperative MRI and postoperative CT (2D view), a right panel showing the cortical surface reconstruction (3D view), and a toolbar at the top.

To adjust the view in the left panel:

* Move the slider at the bottom to adjust the CT-MRI overlay (that is, show the CT or MRI) **(1)**.
* Under the **Image Display** toolbar **(2)**, use the **View** dropdown menu to select the axial, coronal, or sagittal view.
* The **CLim** values control the colour contrast in the CT and MRI.
* The **Inline** option allows you to rotate the MRI and CT images so that the selected lead is effectively brought into the viewing plane, meaning that all contacts along the entire lead are displayed together on one 2D slice. This requires assigning electrodes first.
* The **Label** option will show the assigned contact labels. This requires assigning electrodes first.

The view in the right panel is controlled by the button range above **(3)**.

* Select the **Rotate 3D** button to activate 3D rotation of the surface model.
* Set the **Brain Vis** option below this panel **(4)** to lower opacity values (for example, 0.1) to visualize electrode contacts within the brain.

Contacts can be selected in two ways:

* Use left click to select a contact in the 2D or 3D view.
* Select the **Polygon selection** tool above the 3D panel to select a group of contacts by circling them with the mouse in the 3D panel.
* Selected contacts are displayed in red.

## Electrode contact detection

### Detect the contacts

1. Select the **Auto Elec** button in the **Electrode Creation and Display** toolbar to launch automatic contact detection. This step typically runs in less than 20s. The contact count will reflect how many electrode contacts have been detected. Detected contacts are shown as blue dots.
2. Carefully review the results by looking at the different views as needed. Some electrodes may be easier to review in the axial plane, while others may be easier to review in the coronal plane.
3. To remove one or several false positive contact(s), select them with a left click or by circling them with the polygon selection tool. Selected contacts are shown in red. Then, press the delete key.
4. To add a missing contact, right click its position on the CT (2D view). LeGUI enforces a minimal distance between contacts; if you are not able to add a contact for this reason, select the **Manual Draw** option in the **Electrode Creation and Display** panel to override this constraint.
5. Once all electrode contacts are properly marked, you may proceed to electrode assignment.

## Electrode assignment

This step allows you to name all electrode contacts following the implantation scheme, using a semi-automatic approach.

### Assign the electrodes

1. Once both automatic and manual electrode detection are complete, select the **Assign Electrodes** button at the top of the window.
2. Display options in the electrode assignment GUI are similar to those of the main GUI.
3. Select the **Auto Name** button at the top of the window. The following window opens, showing the electrodes that were detected.

![Auto Name window listing the detected electrodes](manual/3fcc385b1a4120fe.png)

4. It is possible that some contacts may be incorrectly grouped into electrodes; you will be able to fix this in the next step.
5. Select the correct electrode model and name each of the electrodes based on your implantation scheme. To identify which electrode each row corresponds to, click rows to highlight the corresponding contacts in the 3D view.
6. Once you are done, select **Apply Changes** and close the window. You will be able to come back to it if you made a mistake, but changes only get transferred to the main electrode assignment GUI when you select **Apply Changes**.
7. You can now check and correct electrode assignments in the main assignment GUI. First, set the table control mode to **Check**.

![Electrode assignment window in Check mode](manual/86a1aec0125aa153.png)

8. You can now check whether contacts were correctly labelled. Click a contact in the 3-D view to highlight its label, or click a label in the table to highlight its corresponding contact. By default, contacts are numbered from deepest to closest to the cortical surface. You may select the deepest contact in the table and use the top arrow to quickly verify the contact numbering for a given electrode.
9. If some assignments are incorrect, first, switch to the **Edit** table control mode to correct the table. Right-click a column to delete an electrode. Contacts that are no longer assigned will be highlighted in blue. You can also add additional contacts to an electrode by manually entering additional labels, or rename any contacts in the table.
10. Once the table is correct, switch to the **Assign** table control mode to re-assign blue contacts. Select the contacts using a left click or the polygon selection tool, then select the corresponding labels in the table, and select the **Assign** button below the table.
11. When all assignments are correct, close the electrode assignment window, which will save your work.

## Electrode alignment

The **Align Lead** option, accessible from the LeGUI main window, allows users to align contacts along a modeled electrode trajectory using contact spacing automatically estimated from the median Euclidean distance between detected contacts (shown as 5 mm in the example below). This step is optional and may be only applied to electrodes that look poorly aligned. This may occur as the LeGUI automatic contact detection algorithm does not use information on electrode trajectory, but instead detects each contact individually. Use the polygon selection tool to select the electrode contacts to be realigned, and select **Align Lead**. A warning message will appear if the stored electrode spacing does not correspond to the empirical electrode spacing.

![Align Lead result with contacts aligned along the modeled trajectory](manual/67fd819df2dde31b.png)

You are now done with electrode reconstruction and labeling! Do not forget to select the **Save** button before you exit LeGUI!

Optional: select **Export PDF** to generate a PDF report of the electrode reconstructions and save electrode contact information (contacts, MNI coordinates, native coordinates, tissue type, NMM atlas region) in a CSV file.
