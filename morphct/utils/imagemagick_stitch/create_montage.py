import sys
import os
import subprocess as sp
import glob
import argparse


def stitch_images(montage_dims, images_to_stitch, morphology_name, title):
    # First delete previous output to prevent ImageMagick issue
    if title is None:
        title = morphology_name
    try:
        os.remove("./" + title.replace(" ", "_") + ".png")
    except:
        pass
    # Then load all the files
    print("Converting images and adding annotations...")
    directory = "/".join(images_to_stitch[0].split("/")[:-2])
    for ID, image in enumerate(images_to_stitch):
        ID_str = "%04d" % (ID)
        if image[-4:] == ".pdf":
            ## Load image using supersampling to keep the quality high,
            ## and "crop" to add a section of whitespace to the left
            # sp.call(["convert", "-density", "500", image, "-resize", "20%",
            #         "-gravity", "West", "-bordercolor", "white",
            #         "-border", "7%x0", IDStr + "_crop.png"])
            ## Now add the annotation
            # sp.call(["convert", IDStr + "_crop.png", "-font", "Arial-Black",
            #         "-pointsize", "72", "-gravity", "NorthWest",
            #         "-annotate", "0", str(ID+1) + ")", IDStr + "_temp.png"])
            print("Vectorized input image detected, using supersampling...")
            sp.call(
                [
                    "convert",
                    "-density",
                    "500",
                    image,
                    "-resize",
                    "20%",
                    "-font",
                    "Arial-Black",
                    "-pointsize",
                    "10",
                    "-gravity",
                    "NorthWest",
                    "-splice",
                    "0x10%",
                    "-page",
                    "+0+0",
                    "-annotate",
                    "0",
                    str(ID + 1) + ")",
                    directory + "/" + ID_str + "_temp.png",
                ]
            )
        else:
            # Rasterized format, so no supersampling
            # sp.call(["convert", image, "-gravity", "West",
            #         "-bordercolor", "white", "-border", "7%x0",
            #         IDStr + "_crop.png"])
            # Now add the annotation
            # sp.call(['convert', image, '-font', 'Arial-Black',
            #         '-pointsize', '72', '-gravity', 'NorthWest',
            #         '-bordercolor', 'white', '-border', '140x80',
            #         '-page', '+0+0', '-annotate', '0',
            #         str(ID+1) + ')', IDStr + '_temp.png'])
            sp.call(
                [
                    "convert",
                    image,
                    "-resize",
                    "500x500",
                    "-font",
                    "Arial-Black",
                    "-pointsize",
                    "72",
                    "-gravity",
                    "NorthWest",
                    "-splice",
                    "100x120",
                    "-page",
                    "+0+0",
                    "-annotate",
                    "+40+0",
                    str(ID + 1) + ")",
                    directory + "/" + ID_str + "_temp.png",
                ]
            )
    # Create montage
    print("Creating montage...")
    montage = sp.Popen(
        [
            "montage",
            "-mode",
            "concatenate",
            "-tile",
            montage_dims,
            directory + "/*_temp.png",
            "miff:-",
        ],
        stdout=sp.PIPE,
    )
    print("Exporting montage...")
    convert = sp.call(
        [
            "convert",
            "miff:-",
            "-density",
            "500",
            "-resize",
            "2000x",
            "-font",
            "Arial-Black",
            "-pointsize",
            "10",
            "-gravity",
            "North",
            "-bordercolor",
            "white",
            "-border",
            "0x100",
            "-annotate",
            "0",
            title,
            directory + "/" + title.replace(" ", "_") + ".png",
        ],
        stdin=montage.stdout,
    )
    montage.wait()
    print("Removing temporary files...")
    for file_name in glob.glob(directory + "/*_temp.png") + glob.glob(
        directory + "/*_crop.png"
    ):
        os.remove(file_name)
    print(
        "Montage created and saved at "
        + directory
        + "/"
        + title.replace(" ", "_")
        + ".png"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dimensions",
        default="x1",
        required=False,
        help=(
            "The dimensions flag is used to specify the montage"
            " dimensions. The format should be '2x3', which corresponds"
            " to a montage with 2 columns and 3 rows. Dimensions can be"
            " omitted such as '3x', which will create a montage with 3"
            " columns and as many rows as required based on the number"
            " of input figures. Default is a single row of all input images."
        ),
    )
    parser.add_argument(
        "-t",
        "--title",
        default=None,
        required=False,
        help=(
            "Set a custom title for the montage. If not set, will be"
            "assigned based on the enclosing directory."
        ),
    )
    args, directories = parser.parse_known_args()
    for directory in directories:
        morphology_name = os.path.split(directory)[1]
        try:
            images_to_stitch = [
                os.path.join(directory, "figures", figure)
                for figure in os.listdir(os.path.join(directory, "figures"))
            ]
            if len(images_to_stitch) == 0:
                raise FileNotFoundError
        except FileNotFoundError:
            continue
        stitch_images(args.dimensions, images_to_stitch, morphology_name, args.title)


if __name__ == "__main__":
    main()
