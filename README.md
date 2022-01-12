How to create inventories for MVA studies with Serpent2?
========================================================

This repo contains all the scripts and files used by me to create the dataset available at [10.17632/8z3smmw63p.1](https://data.mendeley.com/datasets/8z3smmw63p/1). The data and the methodology is and described in [10.1016/j.dib.2020.106429](https://www.sciencedirect.com/science/article/pii/S2352340920313111?via%3Dihub). The dataset contains several PWR (UOX and MOX) fuel inventories for various burnup, initial enrichment and cooling time. 

The intention of the repo is to help creating similar datasets for other fuel types.

### Disclaimer

In this work I have used the bumat files created by Serpent2 to read the inventory from. Alternatively, one could use the `_dep.m` files (to a certain extent it is a question whether we want to read in a lot of small files, or rather less large files). Also, since the bumat files are also used to serve as material descriptions for subsequent decay calculations, this seemed to be a good choice at the time of doing the work. Nevertheless it can be noted, that instead of file I/O operations, the work flow could have been built around Serpent's `rfr` and `rfw` commands, that is to write the material composition into binary restart files, and read from that. With little modifications to the script and the Serpent inputfile templates this can be implemented. 

Special attention is needed to check that all the paths are in order when you modify and run these scripts. I have collected these files from various folders, and have not tested them afterwards.

Notice, that several part of the scripts is not the most logical, or nicest code. This was partly, because after I have run some of the depletion calculations, I have changed my mind about what to be included in the final fuel library. Therefore, at many places you might find quick and dirty solutions. Enjoy.

### Helper files

Note that these files need to be run only, if one needs an updated `nuclides.json` file due to some reason. 

- `nuclidesjson.py`: script to dump the ZAID and nuclide symbol pairs in a json file. This needed to make sure that the keys are in an alphabetic order (in case the scripts are executed with python2, this is important). The script reads in additional files.
- `jeff31.xsdata`: XS directory shipped with Serpent2 for JEFF 3.1 data. In case a newer version is used, just update this.
- `sample.bumat`: a sample bumat file (Serpent2 output), which contains the inventory described with ZAID. 

By running `python nuclidesjson.py`, the script will check from `sample.bumat` which nuclides are tracked for the depletion calculation (notice that these are the nuclides with xs data, one could force Serpent to print even more, but for practical reasons we omit this), and will get the symbol+A format from `jeff31.xsdata` for the given ZAID. Notice, that in case not the bumat is used to read the inventories from, but the `_dep.m` files, this might need modifications. Nevertheless the sole goal of this script is to create the `nuclides.json` file, which is then used later, and looks like the following:

```
$ head nuclides.json 
{
    "1001": "H1",
    "1002": "H2",
    "1003": "H3",
    "2003": "He3",
    "2004": "He4",
    "3006": "Li6",
    "3007": "Li7",
    "4009": "Be9",
    "5010": "B10",
```

### Running the calculations

Although one could have certainly built one script, which runs the Serpent2 depletion inputs and then extracts the data into a CSV file, I have decided to to do this in 2 separate steps, and while running the calculations, first just build a bookkeeping csv file to store the related path of the BU-CT-IE combinations. (rationale: at the time of running the script, it was not fully decided what data to be included in the final library, hence it was foreseen that the extraction is anyhow done several times later).

One finds the two folders `/UOX` and `/MOX`, which contain the same type of files (hence here I review only the UOX case). Now of course, one could have certainly done both UOX and MOX also in one step, but the reason I did it in separate tracks was, because first I only created UOX files, so later I just repeated the same for MOX. Definitly if one plans more ahead this can be skipped. If an other type of fuel (eg. different geometry, assembly instead of pincell, temperature etc.) is to be used to create a library, these files need modifications:

1. `UOX_manyBU`: Serpent input template with a spaceholder for the fuel description (this is to be updated by the script based on the initial enrichment). This input defines a depletion history with 0.5 MWd/kgU steps, no decay step, and this is run for each IE values. 
2. `UOX_manyCT`: Serpent input template with a spaceholder for the fuel description (this is to be updated by the script based on the initial enrichment and burnup, and it is copied from the bumat files created after running the input based on `UOX_manyBU`). This input defines the decay steps, and is run for all initial enrichment - burnup couples.
3. `Createdataset_PWR.py`: script to run the Serpent2 calculations. The end product of this script are structured folders storing the Serpent2 output files (note that already in the script some files, eg `_res.m` and `.out` can be removed if it is not intended to use those), and a csv file (`fuellog_strategicPWR_UOX.csv`) storing a link to the output related to the BU-CT-IE triplets. Note, within this python script, the `fuelinput()` function can be updated in order to change the fuel temperature and/or density. 

### Merge fuel log files


As said before, I have run the UOX and MOX cases separately, therefore I ended up with two `fuellog....csv` files. This is fine, if someone wants to have two separate fuel libraries also, however my intention was to have one final file, so 

- `merge_csv.py` simple appends the MOX entries to the end of the UOX entries. (Note, pandas could do this, but there is no pandas on the cluster). Also at this point one might to change the path of the outputfiles which is being copied (maybe not to store the whole path, just the portion starting at the working directory)

### Creating the library

Finally we are there. Nothing to do just run `CreateBigDataFrame.py`. Notice, that previously I wrote the `reactorType` in the csv files, this is not kept in here. Also, you probably need to fix the paths in this script to point to the correct folders. 

And the end product is a large csv file, with all the entries.


