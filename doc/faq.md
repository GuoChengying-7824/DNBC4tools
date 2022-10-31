# **FAQ**

### 1. How to set parameters in different sequencing strategy modes or chemistry, and how to adapt the software to analysis?

We set several parameters to read the structure of the library, including `--chemistry`, `--darkreaction` and `--customize`.

When using the default parameters, the software automatically recognizes whether a dark reaction was performed and the version of the chemistry. Of course we can also use `--chemistry`, `--darkreaction` to define it. Currently `--chemistry` includes `scRNAv1HT`,`scRNAv2HT`, and `--darkreaction` can set R1 of cDNA and R1R2 of oligo respectively. For example, R1 of cDNA sets a dark reaction, R1 of oligo sets a dark reaction, and R2 does not set a dark reaction, then we can use `--darkreaction R1,R1`. If `--chemistry` and `--darkreaction` still cannot read the library structure, we can use `--customize` to customize the library results. The definition rules of the json file are as follows:

Library structure for version 1.0 chemistry

- cDNA：

 <img src="https://s2.loli.net/2022/09/27/xOMpQlhtEZHJofB.png" alt="image-20220927164405160" width:"50%">

- oligo：

 <img src="https://s2.loli.net/2022/09/27/IzaBlQOb2SvEjrW.png" alt="image-20220927164440769" width:"50%">
