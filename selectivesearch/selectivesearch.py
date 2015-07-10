import skimage.io
import skimage.feature
import skimage.color
import skimage.transform
import skimage.util
import skimage.segmentation
import numpy

SEGMENT_SIGMA = 0.90
SEGMENT_K     = 500
SEGMENT_MIN   = 5

def generate_segments(im_orig, scale=SEGMENT_K, sigma=SEGMENT_SIGMA, min_size=SEGMENT_MIN):
    """
        segment smallest regions by the algorithm of Felzenswalb and Huttenlocher
    """

    # open the Image
    im_mask = skimage.segmentation.felzenszwalb(skimage.util.img_as_float(im_orig), scale=scale, sigma=sigma, min_size=min_size)
    #im_mask = skimage.segmentation.quickshift(skimage.util.img_as_float(im_orig))
    #im_mask = skimage.segmentation.slic(skimage.util.img_as_float(im_orig), n_segments=100)

    # merge mask channel to the image as a 4th channel
    im_orig = numpy.append(im_orig, numpy.zeros(im_orig.shape[:2])[:, :, numpy.newaxis], axis=2)
    im_orig[:, :, 3] = im_mask

    return im_orig


def sim_colour(r1, r2):
    """
        calculate the sum of histogram intersection of colour
    """
    return sum([min(a, b) for a, b in zip(r1["hist_c"], r2["hist_c"])])


def sim_texture(r1, r2):
    """
        calculate the sum of histogram intersection of texture
    """
    return sum([min(a, b) for a, b in zip(r1["hist_t"], r2["hist_t"])])


def sim_size(r1, r2, imsize):
    """
        calculate the size similarity over the image
    """
    return 1.0 - (r1["size"] + r2["size"]) / imsize


def sim_fill(r1, r2, imsize):
    """
        calculate the fill similarity over the image
    """
    bbsize = (max(r1["max_x"], r2["max_x"]) - min(r1["min_x"], r2["min_x"])) * (max(r1["max_y"], r2["max_y"]) - min(r1["min_y"], r2["min_y"]))
    return 1.0 - (bbsize - r1["size"] - r2["size"]) / imsize


def calc_sim(r1, r2, imsize):
    return sim_colour(r1, r2) + sim_texture(r1, r2) + sim_size(r1, r2, imsize) + sim_fill(r1, r2, imsize)


def calc_colour_hist(img):
    """
        calculate colour histogram for each region

        the size of output histogram will be BINS * COLOUR_CHANNELS(3)

        number of bins is 25 as same as [uijlings_ijcv2013_draft.pdf]

        extract HSV
    """

    BINS = 25
    hist = numpy.array([])

    for colour_channel in (0, 1, 2):

        # extracting one colour channel
        c = img[ : , colour_channel]

        # calculate histogram for each colour and join to the result
        hist = numpy.concatenate([hist] + [numpy.histogram(c, BINS, (0.0, 255.0))[0]])

    # L1 normalize
    hist = hist / len(img)

    return hist


def calc_texture_gradient(img):
    """
        calculate texture gradient for entier image

        The original SelectiveSearch algorithm proposed gaussian derivative for 8 orientations,
        but we use LBP instead.

        output will be [height(*)][width(*)]
    """
    ret = numpy.zeros((img.shape[0], img.shape[1], img.shape[2]))

    for colour_channel in (0, 1, 2):
        ret[ : , : , colour_channel] = skimage.feature.local_binary_pattern(img[ : , : , colour_channel], 8, 1.0)

    return ret


def calc_texture_hist(img):
    """
        calculate texture histogram for each region

        calculate the histogram of gradient for each colours
        the size of output histogram will be BINS * ORIENTATIONS * COLOUR_CHANNELS(3)
    """
    BINS = 10

    hist = numpy.array([])

    for colour_channel in (0, 1, 2):

        # mask by the colour channel
        fd = img[ : , colour_channel]

        # calculate histogram for each orientation and concatenate them all and join to the result
        hist = numpy.concatenate([hist] + [numpy.histogram(fd, BINS, (0.0, 1.0))[0]])

    # L1 Normalize
    hist = hist / len(img)

    return hist


def extract_regions(img):

    R = {}

    # get hsv image
    hsv = skimage.color.rgb2hsv(img[ : , : , : 3])

    # pass 1: count pixel positions
    for y, i in enumerate(img):

        for x, (r, g, b, l) in enumerate(i):

            # initialize a new region
            if l not in R:
                R[l] = { "min_x"  : 0xffff, "min_y"  : 0xffff, "max_x"  : 0, "max_y"  : 0, "labels" : [l] }

            # bounding box
            if R[l]["min_x"] > x:
                R[l]["min_x"] = x
            if R[l]["min_y"] > y:
                R[l]["min_y"] = y
            if R[l]["max_x"] < x:
                R[l]["max_x"] = x
            if R[l]["max_y"] < y:
                R[l]["max_y"] = y

    # pass 2: calculate texture gradient
    tex_grad = calc_texture_gradient(img)

    # pass 3: calculate colour histogram of each region
    for k, v in R.items():

        # colour histogram
        masked_pixels = hsv[ :, :, : ][img[:, :, 3] == k]
        R[k]["size"] = len(masked_pixels / 4)
        R[k]["hist_c"] = calc_colour_hist(masked_pixels)

        # texture histogram
        R[k]["hist_t"] = calc_texture_hist(tex_grad[ : , : ][img[ : , : , 3] == k])

    return R


def extract_neighbours(regions):

    def intersect(a, b):
        if a["min_x"] < b["min_x"] < a["max_x"] and a["min_y"] < b["min_y"] < a["max_y"]:
            return True
        if a["min_x"] < b["max_x"] < a["max_x"] and a["min_y"] < b["max_y"] < a["max_y"]:
            return True
        if a["min_x"] < b["min_x"] < a["max_x"] and a["min_y"] < b["max_y"] < a["max_y"]:
            return True
        if a["min_x"] < b["min_x"] < a["max_x"] and a["min_y"] < b["max_y"] < a["max_y"]:
            return True
        return False

    R = regions.items()
    neighbours = []
    for cur, a in enumerate(R[:-1]):
        for b in R[cur + 1 : ]:
            if intersect(a[1], b[1]):
                neighbours.append((a, b))

    return neighbours


def merge_regions(r1, r2):
    new_size = r1["size"] + r2["size"]
    rt = {
        "min_x" : min(r1["min_x"], r2["min_x"]),
        "min_y" : min(r1["min_y"], r2["min_y"]),
        "max_x" : max(r1["max_x"], r2["max_x"]),
        "max_y" : max(r1["max_y"], r2["max_y"]),
        "size"  : new_size,
        "hist_c" : (r1["hist_c"] * r1["size"] + r2["hist_c"] * r2["size"]) / new_size,
        "hist_t" : (r1["hist_t"] * r1["size"] + r2["hist_t"] * r2["size"]) / new_size,
        "labels" : r1["labels"] + r2["labels"]
    }
    return rt


def selective_search(im_orig, image_size):
    """
        Selective Search algorithm

        "Selective Search for Object Recognition" by J.R.R. Uijlings et al.

        Modified version with HOG extractor for texture vectorization
    """

    # load image and get smallest regions
    # region label is stored in the 4th value of each pixel [r,g,b,(region)]
    im_orig = skimage.transform.resize(im_orig, (image_size,image_size))
    img = generate_segments(im_orig)

    if img is None:
        return None, {}

    imsize = img.shape[0] * img.shape[1]
    R = extract_regions(img)

    # extract neighbouring information
    neighbours = extract_neighbours(R)

    # calculate initial similarities
    S = {}
    for (ai, ar), (bi, br) in neighbours:
        S[(ai, bi)] = calc_sim(ar, br, imsize)

    # hierarchal search
    while S != {}:

        # get highest similarity
        i, j = sorted(S.items(), cmp=lambda a, b: cmp(a[1], b[1]))[-1][0]

        # merge corresponding regions
        t = max(R.keys()) + 1.0
        R[t] = merge_regions(R[i], R[j])

        # mark similarities for regions to be removed
        key_to_delete = []
        for k, v in S.items():
            if (i in k) or (j in k):
                key_to_delete.append(k)

        # remove old similarities of related regions
        for k in key_to_delete:
            del S[k]

        # calculate similarity set with the new region
        for k in filter(lambda a: a != (i, j), key_to_delete):
            n = k[1] if k[0] in (i, j) else k[0]
            S[(t, n)] = calc_sim(R[t], R[n], imsize)

    return img, R
