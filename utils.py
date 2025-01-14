#==================================================================================
# Moved some functions from Colab to here for convenience and to make Colab shorter
#==================================================================================

import numpy as np
from PIL import Image
import cv2
import glob
from numpy import random
import matplotlib.pyplot as plt

coco = []
images = []
size = 360
face_loss = "CelebA_loss.txt"
coco_loss = "COCO_loss.txt"  
cropped_width, cropped_height = 176, 176
down_scale = 4
data_dir, repo_dir, HR_dir, LR_dir= "", "", "", ""
num_images = 1000
split_ratio = 0.8
hr_images = []
lr_images = []
epoch_num = []
perceptual_loss = []
content_loss = []
adversarial_loss = []


def get_data():
    """Getting COCO images that are big enough"""
    for img_name in glob.glob("coco/*.jpg"):
        img = np.asarray(Image.open(img_name))
        coco.append(img)

    i = 0
    while len(images) < 1000:
        shape = np.shape(coco[i])
        if len(shape) == 3:
            if shape[0]>=size and shape[1]>=size:
                images.append(coco[i])
        i += 1

    for img in range(len(images)):
        images[img] = cv2.cvtColor(images[img], cv2.COLOR_BGR2RGB)
        cv2.imwrite("data/{}.jpg".format(img+1), images[img])
        

def crop(img, new_w=cropped_width, new_h=cropped_height):
    "Crop center of image."
    h = img.shape[0]
    w = img.shape[1]
    assert h > new_h and w > new_w
    left = int(np.ceil((w - new_w) / 2))
    right = w - int(np.floor((w - new_w) / 2))
    top = int(np.ceil((h - new_h) / 2))
    bottom = h - int(np.floor((h - new_h) / 2))
    cropped_img = img[top:bottom, left:right, ...]
    return cropped_img


def test_preprocess(img, dir):
    rand_int = random.randint(0, num_images)
    original_test = np.asarray(Image.open(dir + "{}.jpg".format(rand_int)))
    cropped_test = crop(original_test, cropped_width, cropped_height)
    down_sampled_test = down_sample(cropped_test, down_scale)

    print("Original Shape: ", np.shape(original_test))
    print("Cropped Shape: ", np.shape(cropped_test))
    print("Down Sampled Shape: ", np.shape(down_sampled_test))

    fig, ax = plt.subplots(1,3, figsize=(12,6))
    ax[0].set_title("Original")
    ax[0].imshow(original_test)
    ax[1].set_title("Cropped")
    ax[1].imshow(cropped_test)
    ax[2].set_title("Down Sampled")
    ax[2].imshow(down_sampled_test)


def down_sample(img, scale=down_scale):
    """Convert image to lower resolution."""
    new_h = img.shape[0]//scale;
    new_w = img.shape[1]//scale;
    lr_img = np.asarray(Image.fromarray(np.uint8(img)).resize((new_w, new_h), Image.BICUBIC))
    return lr_img


def normalize(img):
    """Normalize image to [-1,1]."""
    n_img = np.divide(img.astype(np.float32), 127.5) - np.ones_like(img, dtype=np.float32)
    return n_img


def get_processed_data(data_dir = data_dir):
    """Populate 4D arrays of high res and low res images."""
    for img_name in glob.glob(data_dir + "*.jpg"):
        img = np.asarray(Image.open(img_name))
        images.append(img)
    for img in range(len(images)):
        hr_img = crop(images[img], cropped_width, cropped_height)
        lr_img = down_sample(hr_img, down_scale)
        hr_images.append(hr_img)
        lr_images.append(lr_img)


def save_processed_data(repo_dir=repo_dir, HR_dir=HR_dir, LR_dir=LR_dir):
    """Save datasets in respective directories."""
    if os.path.isdir(repo_dir + "processed_data"):
        shutil.rmtree(repo_dir + "processed_data")
        
    os.mkdir(repo_dir + "processed_data")
    os.mkdir(HR_dir)
    os.mkdir(LR_dir)
    
    for img in range(len(hr_images)):
        im = Image.fromarray(np.uint8(hr_images[img]))
        file_name = str(img) + ".jpg"
        im.save(os.path.join(HR_dir, file_name))
    
    for img in range(len(lr_images)):
        im = Image.fromarray(np.uint8(lr_images[img]))
        file_name = str(img) + ".jpg"
        im.save(os.path.join(LR_dir, file_name))


def load_train_data(dir=data_dir, num_img=num_images, split_ratio=split_ratio, hr_images=hr_images, lr_images=lr_images):
    """Perform train-test split for high and low res images (load from directories)."""
    num_train = int(num_img * split_ratio)
    hr_files_train = hr_files[:num_train]
    hr_files_test = hr_files[num_train:]
    lr_files_train = lr_files[:num_train]
    lr_files_test = lr_files[num_train:num_img]
    
    hr_train = []
    hr_test = []
    lr_train = []
    lr_test = []
    
    for i in range(len(hr_files_train)):
        hr_img = np.asarray(Image.open(hr_files_train[i]))
        lr_img = np.asarray(Image.open(lr_files_train[i]))
        hr_img = normalize(hr_img)
        lr_img = normalize(lr_img)
        hr_train.append(hr_img)
        lr_train.append(lr_img)
        
    for i in range(len(hr_files_test)):
        hr_img = np.asarray(Image.open(hr_files_test[i]))
        lr_img = np.asarray(Image.open(lr_files_test[i]))
        hr_img = normalize(hr_img)
        lr_img = normalize(lr_img)
        hr_test.append(hr_img)
        lr_test.append(lr_img)
    
    return hr_train, hr_test, lr_train, lr_test


# def download_local(dir):
#     '''This function is only meant to be used for Jupyter Notebook / Colab'''
#     !tar -czf archive.tar.gz dir/data_dir
#     files.download("raw_data.tar.gz")
#     !tar -czf archive.tar.gz dir/processed_data
#     files.download("processed_data.tar.gz")
#     !tar -czf model.tar.gz dir/model
#     files.download("model.tar.gz")
#     !tar -czf output.tar.gz dir/output
#     files.download("output.tar.gz")


def plot_performance():
    """
    Plot performance of different upsampling methods.
    BICUBIC  50.112873
    COCO     11.100603
    CelebA   6.984465
    """
    objects = ('BICUBIC', 'COCO', 'CelebA')
    y_pos = np.arange(len(objects))
    performance = [50.11, 11.10, 6.98]

    plt.bar(y_pos, performance, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.ylabel('Fréchet Inception Distance')
    plt.title('Performance Evaluation with FID')
    plt.savefig("performance.jpg")


def parse_loss():
    f = open(face_loss, "r")
    text = f.read().split("\n")
    for i, line in enumerate(text):
        # if (i+1)%1 == 0 and 1500<=i<=1750:
        if (i+1)%10 == 0:
            split = line.split()
            e = int(split[1])
            c = float(split[6][:7])
            a = float(split[7][:4])*0.001
            p = c + a
            epoch_num.append(e)
            content_loss.append(c)
            adversarial_loss.append(a)
            perceptual_loss.append(p)


def plot_loss():
    fig = plt.figure(figsize=(20,5))
    per, = plt.plot(epoch_num, perceptual_loss, label="Perceptual Loss")
    con, = plt.plot(epoch_num, content_loss, label="Content Loss")
    adv, = plt.plot(epoch_num, adversarial_loss, label="Adversarial Loss (0.1%)")

    plt.legend(['Perceptual Loss','Content Loss', 'Adversarial Loss * 0.001'], loc='upper right')
    # plt.xticks(np.arange(0, 2600, 50))
    plt.xticks(np.arange(0, 2600, 100))

    plt.tight_layout()
    plt.margins(x=0.005)

    plt.savefig("test.jpg")
