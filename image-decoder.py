import sys, getopt
import numpy as np
from PIL import Image

def reject_outliers(data, m = 2.):
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]

def rgb_to_hex(r, g, b):
  return ('#{:X}{:X}{:X}').format(r, g, b)

def average_pixels(img, pixels_coords):
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
    
    r_list = reject_outliers(r_list)
    g_list = reject_outliers(g_list)
    b_list = reject_outliers(b_list)

    for r in r_list:
        r_sum += r

    for g in g_list:
        g_sum += g

    for b in b_list:
        b_sum += b

    r_average = round(r_sum / len(r_list))
    g_average = round(g_sum / len(g_list))
    b_average = round(b_sum / len(b_list))

    print('averages: r %s g %s b %s' % (r_average, g_average, b_average))

    average_color = rgb_to_hex(r_average, g_average, b_average)
    print('got color: %s' % average_color)

    return average_color


def get_border(img):
    width, height = img.size
    pixels = []

    border_width = round(width * 0.05)
    border_height = round(height * 0.05)

    print('border width %s border height %s' % (border_width, border_height))

    for y in range(0, height):
        for x in range(0, width):
            if (x < border_width or x > width - border_width) and \
                (y < border_height or y > height - border_height):
                pixels.append((x, y))
    return list(set(pixels))

def downscale_image(image_path):
    img = Image.open(image_path) # open source image as PIL/Pillow object
    width, height = img.size

    aspect_ratio = height / width

    newsize = (200, round(200 * aspect_ratio))
    print('aspect ratio %s new size %s old size %s' % (aspect_ratio, newsize, (width, height)))
    new_img = img.resize(newsize)
    img.close()
    return new_img

def decode(image_path):
    img = downscale_image(image_path)

    pixels_to_average = []
    pixels_to_average = get_border(img)
    average_color = average_pixels(img, pixels_to_average)

    old_size = img.size
    new_size = (round(img.width * 1.5), round(img.height * 1.5))
    new_im = Image.new("RGB", new_size, average_color)
    new_im.paste(img, ((new_size[0]-old_size[0])//2,
                      (new_size[1]-old_size[1])//2))
    new_im.show()
    new_im.close()
    img.close()
    return average_color

def main(argv):

    image_path = ''

    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print('decode.py -i <inputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('decode.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            image_path = arg
    if image_path == '':
        print('decode.py -i <inputfile>')
        sys.exit(2)

    decode(image_path)

if __name__ == "__main__":
   main(sys.argv[1:])