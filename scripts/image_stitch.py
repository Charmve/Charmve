# python image_stitch.py -d [图像合集目录] -i [待拼凑的图片] -s [小图最终的边长](30) -r
# python scripts/image_stitch.py -d image/ -i image/chaoyue.jpeg -s 30 -r
#
# https://github.com/godweiyang/FunnyMedia
# https://godweiyang.com/2022/04/22/funny-media/

import argparse
import os
import random
import math
from collections import defaultdict

import numpy as np
import PIL.Image as Image
from tqdm import tqdm, trange


def generate1(dir, size, rand):
    print(f"正在拼接尺寸：{size}...")
    nums = len(os.listdir(dir))
    nums_width = int(math.sqrt(nums))
    nums_height = int((nums + nums_width - 1) / nums_width)
    img_width = nums_width * size
    img_height = nums_height * size

    image = Image.new("RGB", (img_width, img_height), "white")
    x = 0
    y = 0

    files = os.listdir(dir)
    if rand:
        random.shuffle(files)

    for i in tqdm(files):
        try:
            img = Image.open(os.path.join(dir, i))
        except IOError:
            print(i)
            print("图像打开失败")
        else:
            img = img.resize((size, size), Image.ANTIALIAS)
            image.paste(img, (x * size, y * size))
            x += 1
            if x == nums_width:
                x = 0
                y += 1
            img.close()

    image.save(f"avatar_{size}.jpg")
    image.close()


def mean_pixel(colors):
    colors = [0.3 * r + 0.59 * g + 0.11 * b for r, g, b in colors]
    return int(np.mean(colors))


def generate2(dir, source, size, rand):
    print(f"正在拼接尺寸：{size}...")

    files = os.listdir(dir)
    if rand:
        random.shuffle(files)

    image = Image.open(source)
    image = image.convert("RGB")
    img_width, img_height = image.size
    img_width = ((img_width + size - 1) // size) * size * ((size + 9) // 10)
    img_height = ((img_height + size - 1) // size) * size * ((size + 9) // 10)
    image = image.resize((img_width, img_height), Image.ANTIALIAS)

    colors = defaultdict(list)
    for i in tqdm(files):
        try:
            img = Image.open(os.path.join(dir, i))
        except IOError:
            print(i)
            print("图像打开失败")
        else:
            img = img.convert("RGB")
            img = img.resize((size, size), Image.ANTIALIAS)
            colors[mean_pixel(img.getdata())].append(i)
            img.close()
    for i in range(256):
        if len(colors[i]) == 0:
            for n in range(1, 256):
                if len(colors[i - n]) != 0:
                    colors[i] = colors[i - n]
                    break
                if len(colors[i + n]) != 0:
                    colors[i] = colors[i + n]
                    break

    index = defaultdict(int)
    for i in trange(0, img_width, size):
        for j in range(0, img_height, size):
            now_colors = []
            for ii in range(i, i + size):
                for jj in range(j, j + size):
                    now_colors.append(image.getpixel((ii, jj)))
            mean_color = mean_pixel(now_colors)
            img = Image.open(
                os.path.join(
                    dir, colors[mean_color][index[mean_color] % len(colors[mean_color])]
                )
            )
            img = img.convert("RGB")
            img = img.resize((size, size), Image.ANTIALIAS)
            image.paste(img, (i, j))
            img.close()
            index[mean_color] += 1

    source_name = ".".join(source.split(".")[:-1])
    image.save(f"{source_name}_{size}.jpg")
    image.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir", "-d", type=str, default="avatar", help="directory of the avatars"
    )
    parser.add_argument(
        "--img", "-i", type=str, default="", help="source image to be coverd"
    )
    parser.add_argument(
        "--size",
        "-s",
        type=str,
        default="30",
        help="size of each avatar (size1,size2,...)",
    )
    parser.add_argument(
        "--rand",
        "-r",
        action="store_true",
        help="whether to shuffle the avatars",
    )
    args = parser.parse_args()
    sizes = [int(s) for s in args.size.split(",")]
    for size in sizes:
        if len(args.img) == 0:
            generate1(args.dir, size, args.rand)
        else:
            generate2(args.dir, args.img, size, args.rand)
