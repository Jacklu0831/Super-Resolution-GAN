'''
DISCLAIMER:
THE FUNCTIONS IN THIS FILE ARE FROM https://github.com/tsc2017/Frechet-Inception-Distance. MY OWN CODE START ON LINE 82.

Code derived from https://github.com/tensorflow/tensorflow/blob/master/tensorflow/contrib/gan/python/eval/python/classifier_metrics_impl.py

Usage:
    Call get_fid(images1, images2)
Args:
    images1, images2: Numpy arrays with values ranging from 0 to 255 and shape in the form [N, 3, HEIGHT, WIDTH] where N, HEIGHT and WIDTH can be arbitrary. 
    dtype of the images is recommended to be np.uint8 to save CPU memory.
Returns:
    Frechet Inception Distance between the two image distributions.
'''

import tensorflow as tf
import os
import functools
import numpy as np
import time
from tensorflow.python.ops import array_ops
tfgan = tf.contrib.gan


session=tf.compat.v1.InteractiveSession()
BATCH_SIZE = 64


# Run images through Inception.
inception_images = tf.compat.v1.placeholder(tf.float32, [None, 3, None, None])
activations1 = tf.compat.v1.placeholder(tf.float32, [None, None], name = 'activations1')
activations2 = tf.compat.v1.placeholder(tf.float32, [None, None], name = 'activations2')
fcd = tfgan.eval.frechet_classifier_distance_from_activations(activations1, activations2)


def inception_activations(images = inception_images, num_splits = 1):
    images = tf.transpose(images, [0, 2, 3, 1])
    size = 299
    images = tf.compat.v1.image.resize_bilinear(images, [size, size])
    generated_images_list = array_ops.split(images, num_or_size_splits = num_splits)
    activations = tf.map_fn(
        fn = functools.partial(tfgan.eval.run_inception, output_tensor = 'pool_3:0'),
        elems = array_ops.stack(generated_images_list),
        parallel_iterations = 1,
        back_prop = False,
        swap_memory = True,
        name = 'RunClassifier')
    activations = array_ops.concat(array_ops.unstack(activations), 0)
    return activations

activations = inception_activations()


def get_inception_activations(inps):
    n_batches = int(np.ceil(float(inps.shape[0]) / BATCH_SIZE))
    act = np.zeros([inps.shape[0], 2048], dtype = np.float32)
    for i in range(n_batches):
        inp = inps[i * BATCH_SIZE : (i + 1) * BATCH_SIZE] / 255. * 2 - 1
        act[i * BATCH_SIZE : i * BATCH_SIZE + min(BATCH_SIZE, inp.shape[0])] = session.run(activations, feed_dict = {inception_images: inp})
    return act


def activations2distance(act1, act2):
     return session.run(fcd, feed_dict = {activations1: act1, activations2: act2})
       

def get_fid(images1, images2):
    assert(type(images1) == np.ndarray)
    assert(len(images1.shape) == 4)
    assert(images1.shape[1] == 3)
    assert(np.min(images1[0]) >= 0 and np.max(images1[0]) > 10), 'Image values should be in the range [0, 255]'
    assert(type(images2) == np.ndarray)
    assert(len(images2.shape) == 4)
    assert(images2.shape[1] == 3)
    assert(np.min(images2[0]) >= 0 and np.max(images2[0]) > 10), 'Image values should be in the range [0, 255]'
    assert(images1.shape == images2.shape), 'The two numpy arrays must have the same shape'
    print('Calculating FID with %i images from each distribution' % (images1.shape[0]))
    start_time = time.time()
    act1 = get_inception_activations(images1)
    act2 = get_inception_activations(images2)
    fid = activations2distance(act1, act2)
    print('FID calculation time: %f s' % (time.time() - start_time))
    return fid


# STARTING FROM HERE IS MY OWN CODE (Jacklu0831)

import argparse
from PIL import Image
import matplotlib.pyplot as plt
import glob

ap = argparse.ArgumentParser()
ap.add_argument("-i1", "--input1", required=True, help="input image directory 1")
ap.add_argument("-i2", "--input2", required=True, help="input image directory 2")
args = vars(ap.parse_args())

ims1 = []
ims2 = []

# get all images sorted into (N, 176, 176, 3) arrays (input2 can either be LR with bicubic interpolation or SR with coco or celebA models)
for im1, im2 in zip(os.listdir(args["input1"]), os.listdir(args["input1"])):
    ims1.append(np.asarray(Image.open(os.path.join(args["input1"], im1))))
    # ims2.append(np.asarray(Image.open(os.path.join(args["input2"], im2)))) 
    ims2.append(np.asarray(Image.open(os.path.join(args["input2"], im2)).resize((176,176), Image.BICUBIC)))

# swap shape to (N, 3, 176, 176) for function
ims1 = np.reshape(ims1, (len(ims1), 3, 176, 176))
ims2 = np.reshape(ims2, (len(ims2), 3, 176, 176))

# get FID
FID = get_fid(np.asarray(ims1), np.asarray(ims2))

# see result in terminal
print(PID)
