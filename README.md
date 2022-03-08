# Image border color extraction
Find the hex color value of the average color around an image's border

Gets the pixels from the outer 5% of an image, discards outlier values, and returns the average color in hex (as a string)

# Usage
`python image-decoder.py -i path/to/image.jpg`

* `-i` input image
* `-q` quiet mode
* `-p OFF` disables the gui preview of the result


# Implementation
* Downscale the source image to have a width of 200px, keeping the aspect ratio. We don't need to keep the original (large) resolution.
* Choose a percentage of the image's border on each axis to use for the color calculation (I use 5%), and put the coordinates of these pixels into a list.
* Split the scaled image to individual lists of `R, G, B` color channels.
* Populate 3 more lists of just the color values (`0-255`) for the perimeter pixels of those channels.
* Use `numpy` to remove statistically significant outliers from each of the lists made in the previous step.
* Calculate the average value for each channel from the result of the previous step.
* Merge the averages of each channel (an `RGB(1, 2, 3)` value) into hex (`#123456`) and return it.
* Optionally display the input image overlaid over the calculated background color using a GUI with `PIL.Image.show()`.
