---
{
  "title": "Adding Fortran dependencies for VTA modelling",
  "linkTitle": "Fortran dependencies",
  "layout": "manual",
  "manual_group": "appendix",
  "description": "Install the Fortran dependencies needed for VTA modelling.",
  "source_url": "https://netstim.gitbook.io/leaddbs/appendix/troubleshooting-specific-help/adding-fortran-dependencies-for-vta-modeling",
  "manual_lead": "Install the Fortran dependencies needed for VTA modelling."
}
---

The FEM-based VTA model (Horn et al. 2017) needs Fortran dependencies since it uses the [SimBio toolbox](https://www.mrt.uni-jena.de/simbio/index.php/Main_Page) that is partially based on Fortran code.

## On a Mac

1. Open a Terminal.
2. If you don't have Homebrew installed, do so by typing:

   ```bash
   /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
   ```

3. Install gcc by typing `brew install gcc`.
4. Add a symbolic link between the file `libgfortran.3.dylib` and the `/usr/local/lib/` folder. You can do so, for example, by typing the following into the Terminal:

   ```bash
   ln /usr/local/Cellar/gcc@4.9/4.9.4/lib/gcc/4.9/libgfortran.3.dylib /usr/local/lib/libgfortran.3.dylib
   ```

   However, depending on the installation of your local gcc, folders might be a bit different in your case.

## For Windows

Check if you have the "Intel(R) Visual Fortran Redistributables for Windows" installed on your system. Otherwise, download them from the [Intel redistributable libraries page](https://software.intel.com/en-us/articles/redistributable-libraries-of-the-intel-c-and-fortran-compiler-for-windows/).

If you do not have them already you might also need "Microsoft Visual C++ 2008 Redistributables" as well as a C++ compiler. In our experience the model works when you have C++ 2008 Redistributables version 9.0.30729.6161 and version 9.0.21022 installed. If you experience problems when trying to run the model we recommend to install these versions.
