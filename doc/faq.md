# **FAQ**

### 1. How to set parameters in different sequencing strategy modes or chemistry, and how to adapt the software to analysis?

We set several parameters to read the structure of the library, including `--chemistry`, `--darkreaction` and `--customize`.

When using the default parameters, the software automatically recognizes whether a dark reaction was performed and the version of the chemistry. Of course we can also use `--chemistry`, `--darkreaction` to define it. Currently `--chemistry` includes `scRNAv1HT`,`scRNAv2HT`, and `--darkreaction` can set R1 of cDNA and R1R2 of oligo respectively. For example, R1 of cDNA sets a dark reaction, R1 of oligo sets a dark reaction, and R2 does not set a dark reaction, then we can use `--darkreaction R1,R1`. If `--chemistry` and `--darkreaction` still cannot read the library structure, we can use `--customize` to customize the library results. The definition rules of the json file are as follows:

Library structure for version 1.0 chemistry

- cDNA：

 <img src="https://s2.loli.net/2022/09/27/xOMpQlhtEZHJofB.png" alt="image-20220927164405160" width="50%">

- oligo：

 <img src="https://s2.loli.net/2022/09/27/IzaBlQOb2SvEjrW.png" alt="image-20220927164440769" width="50%">

The software uses the json file in the directory DNBC4tools/config to identify sequence information such as cell barcode, umi, and read.

The json file format is as follows:

```json
{
    "cell barcode tag":"CB",
    "cell barcode":[
     {
         "location":"R1:1-10",
            "distance":"1",
            "white list":[
                "TAACAGCCAA",
                "CTAAGAGTCC",
                ...
                "GTCTTCGGCT"
            ]
     },
     {
         "location":"R1:11-20"
            "distance":"1",
            "white list":[
                "TAACAGCCAA",
                "CTAAGAGTCC",
                ...
                "GTCTTCGGCT"
            ]
     },
    ],
    "UMI tag":"UR",
    "UMI":{
     "location":"R1:21-30",
    },
    "read 1":{
     "location":"R2:1-100",
    }
}
```

The tag information corresponding to the key of the json file:

| key                       | comment                                                      |
| ------------------------- | ------------------------------------------------------------ |
| cell barcode tag          | SAM tag for cell barcode, after corrected. "CB" is suggested. |
| cell barcode              | JSON array for cell barcode segments                         |
| cell barcode raw tag      | SAM tag for raw cell barcode; "CR" is suggested.             |
| cell barcode raw qual tag | SAM tag for cell barcode sequence quality; "CY" is suggested. |
| distance                  | minimal Hamming distance                                     |
| white list                | white list for cell barcodes                                 |
| location                  | location of sequence in read 1 or 2                          |
| sample barcode tag        | SAM tag for sample barcode                                   |
| sample barcode            | SAM tag for sample barcode sequence quality                  |
| UMI tag                   | SAM tag for UMI; "UR" is suggested for raw UMI; "UB" is suggested for corrected UMI |
| UMI qual tag              | SAM tag for UMI sequence quality                             |
| UMI                       | location value for the UMI                                   |
| read 1                    | read 1 location                                              |
| read 2                    | read 2 location                                              |

The cDNA library and the oligo library were sequenced separately, and the cDNA and oligo were dark-reacted with the immobilized sequences. Use `scRNA_beads_darkReaction.json` and `scRNA_oligo_darkReaction.json`.

```shell
cDNA
cell barcode:R1:1-10、R1:11-20
umi:R1:21-30
read 1:R2:1-100
oligo
cell barcode:R1:1-10、R1:11-20
read 1:R2:1-30
```

The cDNA library and the oligo library were sequenced on one chip, and the cDNA and oligo were dark-reacted only at the R1 end. Use `scRNA_beads_darkReaction.json` and `scRNA_oligo_R2_noDarkReaction.json`.

```shell
cDNA
cell barcode:R1:1-10、R1:11-20
umi:R1:21-30
read 1:R2:1-100
oligo
cell barcode:R1:1-10、R1:11-20
read 1:R2:1-10,R2:17-26,R2:33-42
```

For other sequencing strategies, you can customize the json file and fill in the location according to the location information.
