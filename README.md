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

img = skimage.data.lena()
img_lbl, regions = selectivesearch.selective_search(img, scale=500, sigma=0.9, min_size=10)
regions
=> [{'labels': [0.0], 'rect': (0, 0, 59, 511), 'size': 15633},
 {'labels': [1.0], 'rect': (58, 0, 1, 132), 'size': 173},
 {'labels': [2.0], 'rect': (60, 18, 1, 5), 'size': 8},
 {'labels': [3.0], 'rect': (5, 57, 25, 335), 'size': 507},
 {'labels': [4.0], 'rect': (27, 166, 0, 9), 'size': 10},
 {'labels': [5.0], 'rect': (59, 498, 0, 0), 'size': 1},
 {'labels': [6.0], 'rect': (35, 484, 0, 27), 'size': 28},
 {'labels': [7.0], 'rect': (58, 122, 4, 374), 'size': 581},
 {'labels': [8.0], 'rect': (59, 40, 0, 81), 'size': 82},
 {'labels': [9.0], 'rect': (59, 0, 33, 497), 'size': 2344},
 {'labels': [10.0], 'rect': (66, 258, 22, 60), 'size': 67},
 ...
```

See also an example/example.py which generates :
![alt tag](https://github.com/AlpacaDB/selectivesearch/raw/develop/example/result.png)

## Blog
- EN: http://blog.alpaca.ai/open-source-pure-python-selective-search-and-advanced-object-recognition-with-labellio/
- JP: http://blog-jp.alpaca.ai/entry/2015/08/05/235408
