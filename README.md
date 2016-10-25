# Selective Search Implementation for Python

This is a simple Selective Search Implementation for Python

## Install

```
$ pip install selectivesearch
```

## Usage

It is super-simple.

```python
import skimage.data
import selectivesearch

img = skimage.data.astronaut()
img_lbl, regions = selectivesearch.selective_search(img, scale=500, sigma=0.9, min_size=10)
regions[:10]
=>
[{'labels': [0.0], 'rect': (0, 0, 15, 24), 'size': 260},
 {'labels': [1.0], 'rect': (13, 0, 1, 12), 'size': 23},
 {'labels': [2.0], 'rect': (0, 15, 15, 11), 'size': 30},
 {'labels': [3.0], 'rect': (15, 14, 0, 0), 'size': 1},
 {'labels': [4.0], 'rect': (0, 0, 61, 153), 'size': 4927},
 {'labels': [5.0], 'rect': (0, 12, 61, 142), 'size': 177},
 {'labels': [6.0], 'rect': (7, 54, 6, 17), 'size': 8},
 {'labels': [7.0], 'rect': (28, 50, 18, 32), 'size': 22},
 {'labels': [8.0], 'rect': (2, 99, 7, 24), 'size': 24},
 {'labels': [9.0], 'rect': (14, 118, 79, 117), 'size': 4008}]
```

See also an example/example.py which generates :
![alt tag](https://github.com/AlpacaDB/selectivesearch/raw/develop/example/result.png)

## Parameters of selective search

Let's see this paper: http://cs.brown.edu/~pff/papers/seg-ijcv.pdf

#### sigma

```
In general we use a Gaussian filter to
smooth the image slightly before computing the edge weights, in order to compensate
for digitization artifacts. We always use a Gaussian with σ = 0.8, which does not
produce any visible change to the image but helps remove artifacts.
```

#### min_size

If the rect size is reached on `min_size`, the calculation is stopped.

#### scale

```
There is one runtime parameter for the algorithm, which is the value of k that
is used to compute the threshold function τ . Recall we use the function τ (C) =
14
k/|C| where |C| is the number of elements in C. Thus k effectively sets a scale of
observation, in that a larger k causes a preference for larger components. We use
two different parameter settings for the examples in this section (and throughout the
paper), depending on the resolution of the image and the degree to which fine detail
is important in the scene.
```

## Blog
- EN: http://blog.alpaca.ai/open-source-pure-python-selective-search-and-advanced-object-recognition-with-labellio/
- JP: http://blog-jp.alpaca.ai/entry/2015/08/05/235408
