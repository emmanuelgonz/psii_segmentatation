# PSii Segmentation
This scripts segments pixels based on experimentally-derived pixel thresholds. Rfer to [Herrit et al., 2021](https://doi.org/10.1016/j.softx.2021.100685) for more information about pixel thresholds.

## Inputs
Path to directory containing GeoTIF images.

## Outputs
CSV file containing image thresholds for each plot.

## Arguments and Flags
* **Positional Arguments:** 
    * **Directories containing TIF images:** 'dirs', nargs='+'               

* **Optional Arguments:**
    * **Output directory:** '-o', '--outdir', default='sii_segmentation_out'
