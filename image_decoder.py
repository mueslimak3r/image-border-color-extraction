import sys, getopt
import numpy as np
from PIL import Image

def reject_outliers(data, m = 6.):
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    output = data[s<m].tolist()

    # sometimes numpy tolist() returns a nested list
    if type(output[0]) == list:
        return output[0]

    return output

def clamp(x): 
    return max(0, min(x, 255))

def rgb_to_hex(r, g, b):
    return "#{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))

def average_pixels(img, pixels_coords, quiet):
    r, g, b = img.convert('RGB').split()

    r_sum = 0
    g_sum = 0
    b_sum = 0

    r_list = []
    g_list = []
    b_list = []

    for x, y in pixels_coords:
        r_list.append(r.getpixel((x, y)))
        g_list.append(g.getpixel((x, y)))
        b_list.append(b.getpixel((x, y)))

    if not quiet:
        img_size = img.width * img.height
        print(img.width, img.height)
        print('found border %s pixels (%s percent of %s pixels in scaled image)' % (len(pixels_coords), (len(pixels_coords) / img_size) * 100, img_size))

    r_list = reject_outliers(r_list)
    g_list = reject_outliers(g_list)
    b_list = reject_outliers(b_list)

    if not quiet:
        print('rejected outliers: r %s g %s b %s' % (len(pixels_coords) - len(r_list), len(pixels_coords) - len(g_list), len(pixels_coords) - len(b_list)))

    for r in r_list:
        r_sum += r

    for g in g_list:
        g_sum += g

    for b in b_list:
        b_sum += b

    r_average = round(r_sum / len(r_list))
    g_average = round(g_sum / len(g_list))
    b_average = round(b_sum / len(b_list))

    if not quiet:
        print('averages: r %s g %s b %s' % (r_average, g_average, b_average))

    average_color = rgb_to_hex(r_average, g_average, b_average)
    return average_color


def get_border(img, quiet):
    width, height = img.size
    pixels = []

    percent = 0.05

    border_width = round(width * percent)
    border_height = round(height * percent)

    if not quiet:
        print('border width %s border height %s' % (border_width, border_height))

    for y in range(0, height):
        for x in range(0, width):
            if (x < border_width or x > width - border_width) and \
                (y < border_height or y > height - border_height):
                pixels.append((x, y))
    return list(set(pixels))

def downscale_image(image_path, quiet):
    try:
        img = Image.open(image_path) # open source image as PIL/Pillow object
    except IOError:
        print('%s could not be opened' % image_path)
        return None
    width, height = img.size

    aspect_ratio = height / width

    newsize = (200, round(200 * aspect_ratio))
    if not quiet:
        print('aspect ratio %s new size %s old size %s' % (aspect_ratio, newsize, (width, height)))
    new_img = img.resize(newsize)
    img.close()
    return new_img

def decode(image_path, show_preview = False, quiet = True):
    img = downscale_image(image_path, quiet)

    if img == None:
        print('error processing image')
        return '#FFF'

    pixels_to_average = []
    pixels_to_average = get_border(img, quiet)
    average_color = average_pixels(img, pixels_to_average, quiet)

    if not quiet:
        print('got color: %s' % average_color)

    if show_preview:
        img_size = img.size
        preview_size = (round(img.width * 1.5), round(img.height * 1.5))

        # for some reason PIL doesn't play nicely with hex inputs here
        # manually convert back to RGB here since occasionally it won't accept certain values
        preview_img = Image.new("RGB", preview_size, tuple(int(average_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))

        preview_img.paste(img, ((preview_size[0]-img_size[0])//2,
                        (preview_size[1]-img_size[1])//2))
        preview_img.show()
        preview_img.close()
    img.close()
    return average_color

def main(argv):

    image_path = ''
    show_preview = True
    quiet = False

    try:
        opts, args = getopt.getopt(argv,"hi:qp:")
    except getopt.GetoptError:
        print('\n *   -q to supress debug output (except for errors)')
        print(' *   -p OFF to disable showing the image at the end in a gui')
        print(' *   when used as a module, the default is "-q -p OFF"\n')
        print('image_decoder.py -i <inputfile> -q -p OFF\n')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('\n *   -q to supress debug output (except for errors)')
            print(' *   -p OFF to disable showing the image at the end in a gui')
            print(' *   when used as a module, the default is "-q -p OFF"\n')
            print('image_decoder.py -i <inputfile> -q -p OFF\n')
            sys.exit()
        elif opt == '-i':
            image_path = arg
        elif opt == '-q':
            quiet = True
        elif opt == '-p':
            show_preview = False if arg == 'OFF' else True

    if image_path == '':
        print('\n *   -q to supress debug output (except for errors)')
        print(' *   -p OFF to disable showing the image at the end in a gui')
        print(' *   when used as a module, the default is "-q -p OFF"\n')
        print('image_decoder.py -i <inputfile> -q -p OFF\n')
        sys.exit(2)

    color = decode(image_path, show_preview, quiet)
    if quiet:
        print(color)

if __name__ == "__main__":
   main(sys.argv[1:])