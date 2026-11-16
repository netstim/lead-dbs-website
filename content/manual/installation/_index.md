---
{
  "title": "Installation",
  "linkTitle": "Installation",
  "layout": "manual",
  "manual_group": "getting-started",
  "description": "Install Lead-DBS and its dependencies, keep it up to date and solve common setup problems.",
  "source_url": "https://netstim.gitbook.io/leaddbs/installation",
  "manual_lead": "Set up Lead-DBS and its dependencies, then start your first analysis."
}
---

## Requirements {#prerequisite}

| Requirement | Version or recommendation |
| --- | --- |
| MATLAB | R2024b or later |
| Memory | 32 GB RAM or more recommended |
| SPM | [SPM12](https://www.fil.ion.ucl.ac.uk/spm/software/spm12/) |

**Required MATLAB toolboxes:** Image Processing Toolbox, Signal Processing Toolbox, and Statistics and Machine Learning Toolbox.

<details>
<summary>Optional MATLAB toolboxes</summary>

Curve Fitting Toolbox and Parallel Computing Toolbox.

</details>

## Install Lead-DBS {#normal-installation}

1. [Download Lead-DBS](/download/).
2. **Extract the archive** into your MATLAB toolbox folder. For example, it can be in your home folder under `Documents/MATLAB/toolbox`. Avoid extracting Lead-DBS into the MATLAB installation folder or any other folder that requires `sudo` or administrator permission. Also avoid an installation path that contains spaces.
3. **Add SPM12** to your MATLAB search path: right-click the SPM12 folder and choose **Add to Path** > **Selected Folders** (not **Selected Folders and Subfolders**).
4. **Add Lead-DBS** to your MATLAB search path: right-click the Lead-DBS folder and choose **Add to Path** > **Selected Folders and Subfolders**.

Open the MATLAB Command Window and start Lead-DBS:

```matlab
lead dbs
```

## Installation via GitHub

To work on the code or update with Git, install from GitHub:

1. Clone (do not download) the Lead-DBS repository from [GitHub](https://github.com/netstim/leaddbs) and switch to `develop` branch.
2. Download the necessary [data](https://www.lead-dbs.org/release/download.php?id=data_pcloud) and unzip it into the cloned git repository.
3. **Add SPM12** to your MATLAB search path: right-click the SPM12 folder and choose **Add to Path** > **Selected Folders** (not **Selected Folders and Subfolders**).
4. **Add Lead-DBS** to your MATLAB search path: right-click the Lead-DBS folder, choose **Add to Path** > **Selected Folders** (not **Selected Folders and Subfolders**) and then run `ea_setpath` in MATLAB Command Window to set the path.

Use `git pull` to get updates.

If you have the GitHub installation of Lead-DBS and need to switch between the `develop` branch and the `classic` branch, you must also download the [classic data](https://www.lead-dbs.org/release/download.php?id=data_classic_pcloud) and unzip it into the Lead-DBS installation folder. To switch branches, use the MATLAB helper functions `ea_switch2classic` and `ea_switch2dev`; they keep the preferences and recent histories of both branches. They need [Git](https://git-scm.com/downloads), which usually comes with Linux and macOS; on Windows, install it first.

To contribute your changes, open a pull request or ask us for push access.

## Installing OSS-DBS v2

OSS-DBS v2 is an electric field and pathway activation modelling platform used by Lead-DBS. It is installed automatically in the background (via conda) the first time you select it in the Lead-DBS GUI. If the automatic installation succeeds, no further steps are needed.

{{% manual-note "warning" %}}
The automatic conda-based installation may fail in the following cases:

* Windows: `git` is not installed (see prerequisites above)
* All platforms: a conflicting Anaconda installation is present on the system
* All platforms: firewall policies block the download
{{% /manual-note %}}

In these cases, follow the manual installation instructions below.

### Windows: pre-built binaries {#manual-installation-via-pre-built-binaries-windows-only}

If the automatic conda-based installation of OSS-DBS fails, you can link a pre-built binary bundle manually:

1. Download the [OSS-DBS v0.5.5 binary bundle](https://github.com/SFB-ELAINE/OSS-DBSv2/releases/download/v0.5.5/ossdbs_bundle.zip) (`ossdbs_bundle.zip`).
2. Extract the zip to a permanent location on your system, for example `C:\software\ossdbs_bundle`.
3. In the Lead-DBS GUI, go to **Preferences** > **Edit Preferences File**.
4. Add the following line at the end of the file:

   ```matlab
   prefs.oss_bin_path = 'C:\software\ossdbs_bundle';
   ```

5. Lead-DBS will use the binary bundle instead of the conda environment.

### Linux and macOS: pip {#manual-installation-via-pip-linux-and-macos}

If the automatic installation fails on Linux or macOS, you can install OSS-DBS via pip:

1. Run the following commands in your terminal:

   ```bash
   python3 -m venv ossdbs-env
   source ossdbs-env/bin/activate
   pip install ossdbs
   ```

2. In the Lead-DBS GUI, go to **Preferences** > **Edit Preferences File** and add the following line at the end, replacing the path with your actual venv location:

   ```matlab
   prefs.ext_oss_env = '/home/username/ossdbs-env/';
   ```

{{% manual-note "info" %}}
On Ubuntu 24.04 and later, a virtual environment is required for pip installs (enforced via PEP 668). The commands above create and activate one before installing. You can confirm the correct path by activating the environment (`source ossdbs-env/bin/activate`) and running `which ossdbs` - use the output path without the trailing `/bin/ossdbs`.
{{% /manual-note %}}

## Installing additional content

Several add-ons are available which can be installed manually from inside Lead-DBS. For most cases, Lead-DBS will try to auto-install these when needed. You can also take a look at the **Install** menu within the main Lead-DBS GUI to install custom items.

## Update Lead-DBS

* If you have a normal installation of Lead-DBS, you can use the menu **Install** > **Install development version of Lead-DBS**. It will download and apply the latest hotfix before a new release is available.
* If you have Lead-DBS installed via GitHub, simply `pull` from GitHub (in the terminal or any Git client you prefer).

## Troubleshooting

<details>
<summary>Reset preferences after an update</summary>

If a new version produces errors after upgrading, run `ea_restoreprefs(1,1)` in the MATLAB Command Window to reset preferences, then try again.

</details>

<details>
<summary>Resolve an “Unrecognized function or variable” error</summary>

Some Lead-DBS subfolders may be missing from the MATLAB search path. Run `ea_setpath` in the MATLAB Command Window to update the path.

</details>

<details>
<summary>Check MATLAB compatibility on macOS</summary>

Lead-DBS versions earlier than 3.0 and the classic branch on GitHub support MATLAB R2023a or earlier on macOS.

</details>

<details>
<summary>Resolve macOS permission errors</summary>

If you encounter a permission error when running Lead-DBS on macOS, run `ea_clear_xattr`.

</details>

## Disclaimer

We try to maintain compatibility to Linux, macOS and Windows, but given our small team, not all functions are well tested on all OSs ([fork us on GitHub and join our team to improve that](https://www.github.com/netstim/leaddbs)).

## Useful tools

DICOM viewer [Aliza](https://www.aliza-dicom-viewer.com)

NIfTI viewer [MRIcron](https://www.nitrc.org/projects/mricron/), [Mango](https://mangoviewer.com/mango.html)

[DTI-TK Quicklook plugin](https://dti-tk.sourceforge.net/pmwiki/pmwiki.php?n=QuicklookPlugin.Main) (macOS)

[3D Slicer](https://www.slicer.org)

[FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/)

[DSI-Studio](https://dsi-studio.labsolver.org/)

[TrackVis](https://trackvis.org/)
