# -*- coding: utf-8 -*-
import skimage.io
import skimage.data
import skimage.color
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from selectivesearch import selective_search


def main():

    img = skimage.data.lena()

    _, regions = selective_search(
        img,
        None,
        segment_sigma=0.90,
        segment_k=500,
        segment_min=5
    )

    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))

    ax.imshow(img)

    for idx, r in enumerate(regions):
        (x, y, w, h) = r['rect']
        rect = mpatches.Rectangle(
            (x, y), w, h, fill=False, edgecolor='red', linewidth=1)
        ax.add_patch(rect)

    fig.show()


if __name__ == "__main__":
    main()
