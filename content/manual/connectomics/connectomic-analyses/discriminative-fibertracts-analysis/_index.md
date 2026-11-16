---
{
  "title": "Discriminative fibertracts analysis",
  "linkTitle": "Discriminative fibertracts",
  "layout": "manual",
  "manual_group": "connectomics",
  "description": "Investigate fibre tracts associated with differences in stimulation outcomes.",
  "source_url": "https://netstim.gitbook.io/leaddbs/connectomics/connectomic-analyses/discriminative-fibertracts-analysis",
  "manual_lead": "Investigate fibre tracts associated with differences in stimulation outcomes."
}
---

The concept of discriminative fibertracts is to isolate bundles that are associated with an effect upon neuromodulation. This effect could be clinical (for example, %-UPDRS-III improvement following STN-DBS) or behavioural (for example, change in risk-taking behaviour or movement speed in a motor task).

This analysis builds upon [Lead Group](/manual/lead-group/group-analyses-with-lead-dbs/). It is important to have all VTAs/E-Fields calculated for this (select the **Calculate stats & VTA** button).

Select the **Visualize 3D** button inside Lead Group.

In the 3D viewer, select the **Add discriminative fibertract** button:

![Select this button to open up the Discriminative Fibertracts explorer](manual/b1f7ba12c84604d9.png)

{{% manual-note "info" %}}
In this analysis stream, you have to once calculate tract metrics for any combination of normative connectomes and statistical metric. After this calculation, you can explore the results interactively.
{{% /manual-note %}}

In the 3D fibres viewer, choose your metric of choice. The following metrics have been implemented:

## Spearman's correlations and E-fields {#spearmans-correlations--e-fields}

![Fig. 1: Spearman's Correlations / E-Fields method](manual/5ae23e8f6d38a908.png)

Each tract in the normative connectome is analysed separately. Panel A shows one example tract. Parts of this tract pass through some of the E-fields shown in yellow. They traverse less closely to the ones shown in blue but will still traverse through areas of those E-Fields that have a lower magnitude sum (remember that the E-Field is the estimated vector field denoting changes in voltage induced by the stimulation; its magnitude would be the absolute difference of voltage between two points).

**Fig. 1 A:** Each tract is represented as discrete points in space (N x 3 vector if N is the length of the tract; red dots in (A)). For each E-field, sample its values at the points along the tract, whether the field is shown in yellow or blue in panel A. Depending on the analysis, average or sum these values. Alternatively, you can simply use the peak value (more conforming to the "all or nothing" principle of action potentials) or the 5% peak values. This strategy will lead to one value for each pair of tract and E-Field (N x M if N is number of tracts and M is number of E-Fields; represented as `fibsval` for each hemisphere in the code).

**Fig. 1 B:** When calculating Spearman's correlations between this structure and a clinical/behavioural variable (for example, %-UPDRS-III improvement), we will get one Spearman's correlation coefficient for each tract.

**Fig. 1 C:** We can now use these coefficients (R) to colour-code and select tracts for visualization.

## Two-sample t-tests and VTAs {#two-sample-t-tests--vtas}

![Fig. 2: T-Test / VTA method](manual/7d76635ea5607711.png)

In this method, the same is done for binary VTAs (which in the case of Lead-DBS are thresholded E-Fields).

**Fig. 2 A:** Each tract can either be connected or not connected to any VTA. Thus, each single tract splits the group of VTAs (in template space) into two sets.

**Fig. 2 B:** When calculating Two-sample T-tests between a clinical/behavioural variable (for example, %-UPDRS-III improvement) observed in the group of connected vs. unconnected VTAs, we will get a T-value for each tract.

**Fig. 2 C:** We can now use these values (T-scores) to colour-code and select tracts for visualization.
