### **version 2.0.4**

`2022.08.13`

- Update： Add docker version.

- Fix： 

  There is a problem with the annotation logic statistics in the previous version, and this version has been corrected.

  Fixed some description in html.
  
  The previous version was too strict with the format of gtf file, we fix it.

It is recommended to upgrade this version, git clone and then update the environment.



### **version 2.0.0**

`2022.06.20`
- Update： The software is updated to version 2.0, which can use wdl process and command line mode.
- Fix： The process interruption caused by empty beads similarity analysis, and errors in QC and clustering when the number of cells is small.
- Optimization： Reduce the time and memory used for alignment and annotation analysis. Intronic reads are added by default in the annotation for expression analysis; the emptydrops method is added in the cell calling step, which is used by default; the display results of the pictures in the result report are optimized.
- Added： Saturation analysis; annotation of cell clustering results; added Fraction Reads in cells results.