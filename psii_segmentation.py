#!/usr/bin/env python3
"""
Author : Emmanuel Gonzalez
**Notes: This code was developed by collaborators at the USDA
        (see references). It was modified to allow for it's
        integration in a scalable data processing pipeline.**
References: Jacob Long, Matthew Herritt, Alison Thompson
Date   : 2020-08-23
Purpose: Segment PS2 images given a set of thresholds
"""

import argparse
import os
import sys
import numpy as np
import glob
from collections import Counter, defaultdict
import pandas as pd
from osgeo import gdal, ogr, osr
import json
from datetime import datetime
startTime = datetime.now()

# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='PS2 image segmentation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('dirs',
                        metavar='dirs',
                        nargs='+',
                        type=str,
                        help='Directories containing TIF images')

    parser.add_argument('-o',
                        '--outdir',
                        help='Output directory',
                        metavar='str',
                        type=str,
                        default='psii_segmentation_out')

    return parser.parse_args()


# --------------------------------------------------
def apply_threshold(img_path):
    plot = img_path.split('/')[-2]

    g_img = gdal.Open(img_path)
    a_img = g_img.GetRasterBand(1).ReadAsArray()

    all_pixels = []
    for row in a_img:
        all_pixels.extend(row)
    all_pixels = np.asarray(all_pixels)

    thresholds = {
        "t1": (0, 7 ),
        "t2": (8, 10 ),
        "t3": (11, 14 ),
        "t4": (15, 19 ),
        "t5": (20, 255 ),
    }

    unique, counts = np.unique(all_pixels, return_counts=True)
    pixel_counts = dict(zip(unique, counts))

    threshold_counts = Counter()
    averages_dict = {}

    for threshold_name, threshold in thresholds.items():
        average_dict = {}

        for pixel_value, count in pixel_counts.items():
            if threshold[0] <= pixel_value <=threshold[1]:
                threshold_counts[threshold_name] += count
                average_dict[pixel_value] = count

            num = 0
            total = 0
            for pixel_value, count in average_dict.items():

                num += pixel_value * count
                total += count

            try:
                averages_dict[threshold_name] = num/total
            except:
                averages_dict[threshold_name] = 0

    output_list = []

    for key, threshold in thresholds.items():

        output_list.append({
            'Label': os.path.basename(img_path),
            'Area':  threshold_counts[key],
            'Mean':  averages_dict[key],
            'Min':   threshold[0],
            'Max':   threshold[1],
            'Plot':  plot
        })
    return output_list


# --------------------------------------------------
def main():
    """Segment images here"""

    args = get_args()

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    for dir in args.dirs:
        startTime_ind = datetime.now()
        
        image_paths = glob.glob(f'{dir}/*.tif')
        basename = os.path.splitext(os.path.basename(image_paths[0].split('_')[-2]))[0]
        out_path = os.path.join(args.outdir, basename + '_segmentation.csv')

        image_dicts = []
        for ip in image_paths:
            image_dicts.extend(apply_threshold(ip))

        df = pd.DataFrame(image_dicts)

        df.to_csv(out_path)
        print(f'Created {out_path}\nProcessing time: {datetime.now() - startTime_ind}\n')

    print(f'Done.\nEntire processing time: {datetime.now() - startTime}')


# --------------------------------------------------
if __name__ == '__main__':
    main()
