---
{
  "title": "VTA calculation troubleshooting",
  "linkTitle": "VTA calculation problems",
  "layout": "manual",
  "manual_group": "appendix",
  "description": "Diagnose mesh-building and electric-field calculation problems in the FieldTrip/SimBio workflow.",
  "source_url": "https://netstim.gitbook.io/leaddbs/appendix/troubleshooting-specific-help/vta-calculation-troubleshoot",
  "manual_lead": "Diagnose mesh-building and electric-field calculation problems in the FieldTrip/SimBio workflow."
}
---

Use this guide to troubleshoot VTA or electric-field calculations with the FieldTrip/SimBio method in Lead-DBS.

## Use OSS-DBS v2

Go for the new and shiny tool, OSS-DBS v2. This is the future anyway, the model is better and it just works. We recommend trying it. OSS-DBS is available on the `develop` branch. Windows users might need to install git if it has not been installed previously.

1. Install Lead-DBS via GitHub (see [Installation via GitHub](/manual/installation/#installation-via-github)).
2. If you have Lead-DBS already installed, we still recommend to update your templates/ folder with the latest [data](https://www.lead-dbs.org/release/download.php?id=data_pcloud). This will ensure that the SPM-based segmentation files are up-to-date.
3. Check out the `develop` branch (you can search online for how to check out branches on git if new to git, it’s all very well documented with tons of tutorials online).
4. Have fun with OSS-DBS (choose the model instead of the FieldTrip one). Don't forget to take a look at **Settings** to check the simulation setup, for example the electric field thresholding.
5. Occasionally, OSS-DBS will be re-installed when running a new simulation. This happens automatically when we update the remote repository.

## Understand mesh failures

1. Calculating the stimulation volume is dependent on creating a suitable tetrahedral volumetric mesh describing the structure of the conducting & insulating parts of the electrode surrounded by anatomical structures (grey and white matter). Lead-DBS uses multiple tools to do this, including the SimBio - FieldTrip pipeline (Vorwerk et al, 2018) as well as Iso2Mesh (Qianqian Fang, 2009) and, most importantly, TetGen (Hang Si, 2015).
2. Given the variations of electrode placements relative to anatomical structures, it can happen that during mesh building, triangles of the two components intersect. This will lead to downstream problems for calculating the voltage distribution and electric field. If this happens, Lead-DBS will throw out an error.
3. This is a general problem of finite element method (FEM)-related mesh building and not unique to Lead-DBS. In other words, this is often not easy to automate for all cases of electrode placements and all atlases. For that reason, commercial software, such as SureTune or GuideXT uses heuristic shortcuts to calculate VTAs more robustly. In Lead-DBS, a similar shortcut that will work robustly has been implemented in form of the FastField method (Baniasadi et al, 2020).
4. We have tried to make the process as robust as possible. However, despite many strategies and attempts, calculating VTAs with the SimBio method can still fail in some cases.
5. If none of this helps, see below.

## Check the FieldTrip/SimBio setup

1. First make sure that no other MATLAB code is on your path except the base folder of Lead-DBS and the base folder of SPM. Retry and see if it works. If it does, great.
2. Make sure you have the toolboxes (statistics, image processing and signal processing) installed which Lead-DBS generally needs.
3. Make sure the Fortran libraries are installed (see [Adding Fortran dependencies for VTA modelling](/manual/appendix/troubleshooting-specific-help/adding-fortran-dependencies-for-vta-modeling/)).
4. Change the VTA settings to use no atlas or the DISTAL Nano atlas under the **Visualization** step (see below).

![VTA settings — screenshot 1](manual/c283889907f4b6c7.png) ![VTA settings — screenshot 2](manual/0dec33da212e79fe.png)

## Further troubleshooting

1. Delete the `headmodel.mat` files (for example, `headmodel1.mat`) under the `headmodel` directory, and re-run VTA reconstruction.
2. Retry calculating the VTAs several times, even if it failed the first time (there are some non-deterministic components in the pipeline).
3. If all fails, slightly reposition the electrodes (by sub-millimetres that still make the reconstruction accurate) using the **Reconstruction of electrode trajectories (optional)** module.
4. If none of that solves the issue, set a breakpoint on line 135 in the file `ea_genvat_horn.m`. Select the **Calculate** button again to calculate a VTA. The code will stop at that line. Select the following line, right-click it and choose **Evaluate Selection in Command Window**:

   ```matlab
   [mesh.tet,mesh.pnt,activeidx,wmboundary,centroids,tissuetype]=ea_mesh_electrode(fv,elfv,ntissuetype,electrode,options,S,side,electrode.numel,Ymod,elspec);
   ```

   This will likely crash and show an error report. Send us that error report (on Slack) if it is not obvious to solve the issue for yourself.

## References

{{< manual-references >}}

1. Vorwerk, J., Oostenveld, R., Piastra, M.C. *et al.* The FieldTrip-SimBio pipeline for EEG forward solutions. *BioMed Eng OnLine* **17,** 37 (2018). [doi:10.1186/s12938-018-0463-y](https://doi.org/10.1186/s12938-018-0463-y)
2. Qianqian Fang and David Boas, "Tetrahedral mesh generation from volumetric binary and gray-scale images," Proceedings of IEEE International Symposium on Biomedical Imaging 2009, pp. 1142-1145, 2009
3. Hang Si. 2015. "[*TetGen, a Delaunay-Based Quality Tetrahedral Mesh Generator*](https://doi.acm.org/10.1145/2629697)". ACM Trans. on Mathematical Software. **41** (2), Article 11 (February 2015), 36 pages. [doi:10.1145/2629697](https://doi.acm.org/10.1145/2629697)
4. Baniasadi M, Proverbio D, Gonçalves J, Hertel F, Husch A. FastField: An open-source toolbox for efficient approximation of deep brain stimulation electric fields. Neuroimage. 2020 Dec;223:117330. doi: 10.1016/j.neuroimage.2020.117330. Epub 2020 Sep 2. PMID: 32890746.

{{< /manual-references >}}
