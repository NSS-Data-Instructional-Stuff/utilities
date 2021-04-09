from PIL import Image, ImageOps
import os
import pandas as pd
import numpy as np
import json
from collections import Counter
import string


def prepare_df(csv_path):
    df = pd.read_csv(csv_path)
    if "First" not in df.columns:
        df[["First", "Last"]] = df['Name'].str.replace('  ', ' ').str.split(' ', expand = True)
    return df


def clean_string(s):
    if type(s) == str:
        return s.replace('“', '"').replace('”', '"').replace("’", "'").replace("—", "-")
    else:
        return 'nan'


def fix_url(url):
    if url != "nan":
        if all(part not in url for part in ["www", "github"]):
            url = 'www.'+url
        if "https://" not in url:
            url = "https://"+url
    return url


def check_file(sub_folder, name, path_to_repo):
    if os.path.exists('{}/assets/{}/{}'.format(path_to_repo, sub_folder, name)):
        return '../assets/{}/{}'.format(sub_folder, name)
    else:
        return 'nan'


def make_mirrored_images(existing_img_list, image_dir):
    existing_img_ppl = Counter([im[:-5] for im in existing_img_list if '.jpg' in im])
    need_flipped_names = [k+'1.jpg' for k, v in existing_img_ppl.items() if v == 1]
    pro_imgs = [im for im in existing_img_list if im in need_flipped_names]
    for im in pro_imgs:
        i = Image.open(image_dir+'/'+im)
        i_mirror = i.transpose(Image.FLIP_LEFT_RIGHT)
        i_mirror.save(image_dir + '/' + im[:-5] + '2.jpg')


def remove_punct(s):
    return s.translate(str.maketrans('', '', string.punctuation))
    
    
def combine_names(names, sep = '_'):
    names = [remove_punct(n) for n in names]
    return sep.join(names)


def make_cohort_dict(class_info, path_to_repo, names_to_use):
    '''
    function to make cohort.json.
    arg class_info: pandas DataFrame, df including minimally the columns:
        First, Last, Tagline, Bio, Github, LinkedIn, Capstone (link), Capstone (video), Email
    '''
    cohort_json = {"cohort": []}
    for ind, row in class_info.iterrows():
        student_dict = {"id": ind,
                        "firstName": row['First'],
                        "lastName": row['Last'],
                        "reelThemIn": clean_string(row['Tagline']),
                        "bio": clean_string(row['Bio']),
                        "github": fix_url(str(row['Github'])),
                        "linkedIn": fix_url(str(row['LinkedIn'])),
                        "portfolio": fix_url(str(row['Capstone (link)'])),
                        "proImg": check_file("img", "{}1.jpg".format(combine_names([row[name].lower() for name in names_to_use])), path_to_repo),
                        "funImg": check_file("img", "{}2.jpg".format(combine_names([row[name].lower() for name in names_to_use])), path_to_repo),
                        "video": fix_url(str(row['Capstone (video)'])),
                        "resume": check_file("resume", "{}.pdf".format(combine_names([row[name].lower() for name in names_to_use])), path_to_repo),
                        "email": str(row['Email'])}
        student_dict = {k:v for k, v in student_dict.items() if v != 'nan'}
        cohort_json['cohort'].append(student_dict)
    return cohort_json


def make_cohort_json(csv_path, names_to_use = ['First']):
    if type(names_to_use) != list:
        names_to_use = [names_to_use]
    split_path = csv_path.split("/")
    repo_ind = [i for i, p in enumerate(split_path) if ".github.io" in p][0]
    path_to_repo = "/".join(split_path[:repo_ind+1])
    df = prepare_df(csv_path)
    cohort_json = make_cohort_dict(df, path_to_repo, names_to_use)
    outpath = "/".join(csv_path.split("/")[:-1])+"/cohort.json"
    with open(outpath, "w") as outfile:
        json.dump(cohort_json, outfile)
    print("cohort.json created: {}".format(outpath))


def make_techs_json(csv_path):
    df = pd.read_csv(csv_path)
    techs_json = {"techs":[]}
    for ind, row in df.iterrows():
        tech_dict = {"name": row["Technology Name"],
                     "image": "../assets/tech_img/"+row["Image Name"],
                     "link": row["Info Link"]}
        techs_json['techs'].append(tech_dict)
    outpath = "/".join(csv_path.split("/")[:-1])+"/techs.json"
    with open(outpath, "w") as outfile:
        json.dump(techs_json, outfile)
    print("techs.json created: {}".format(outpath))


def convert_to_jpg(img_path):
    '''
    Converts image to JPEG and saves new file with .jpg extension
    '''
    img = Image.open(img_path)
    if img.format != "JPEG" or img_path[-4:] != ".jpg":
        img_path = '.'.join(img_path.split(".")[:-1]) + ".jpg" # join with '.' in case multiple . in path
        try:
            img.save(img_path, "JPEG")
        except OSError:
            img = img.convert('RGB')
            img.save(img_path, "JPEG")


def decrease_image_res(img_path):
    '''
    Decreases image resolution to 72dpi
    '''
    im = Image.open(img_path)
    try:
        if im.info['dpi'][0] > 72:
            im.save(img_path, dpi = (72, 72))
    except KeyError:
        print('{} does not have dpi attribute'.format(img_path.split('/')[-1]))

def find_image_height(img_path, aspect_ratio):
    '''
    print new image height with correct aspect ratio
    '''
    im = Image.open(img_path)
    im_name = img_path.split('/')[-1]
    new_height = round(im.width/aspect_ratio)
    if new_height > im.height:
        new_width = round(im.height * aspect_ratio)
        print('new width for {}: '.format(im_name), new_width)
    else:
        print('new height for {}: '.format(im_name), new_height)
    
def find_max_aspect_ratio(img_dir, img_list):
    pro_imgs = [im for im in img_list if '1' in im]
    max_ar = 0
    for img in pro_imgs:
        im = Image.open(img_dir+'/'+img)
        new_ar = im.width/im.height
        if new_ar < 1:
            max_ar = max(max_ar, new_ar)
    print('max_ar: ', max_ar)
    return max_ar

def prepare_images(img_dir, ignore_files = ['.DS_Store']):
    existing_img_list = [im for im in os.listdir(img_dir) if im not in ignore_files]
    max_ar = find_max_aspect_ratio(img_dir, existing_img_list)
    for img_name in existing_img_list:
        decrease_image_res(img_dir+'/'+img_name)
        convert_to_jpg(img_dir+'/'+img_name)
        if '1' in img_name:
            find_image_height(img_dir+'/'+img_name, max_ar)
    existing_img_list = [im for im in os.listdir(img_dir) if im not in ignore_files]
    make_mirrored_images(existing_img_list, img_dir)
    print("prepared all images in {}".format(img_dir))
