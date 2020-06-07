from PIL import Image
import os
import pandas as pd
import numpy as np
import json


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
    if "https://" not in url and url[:3] == "www":
        return "https://"+url
    else:
        return url


def clean_dict(d):
    for k, v in d.items():
        if v == 'nan':
            d.pop(k)
    return d


def check_file(name, sub_folder):
    return "stuff"


def make_flipped_images(existing_img_list):
    return "stuff"



def make_cohort_dict(class_info):
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
                        "proImg": "../assets/img/{}1.jpg".format(row['First'].lower()),
                        "funImg": "../assets/img/{}2.jpg".format(row['First'].lower()),
                        "video": fix_url(str(row['Capstone (video)'])),
                        "resume": "../assets/resume/{}.pdf".format(row['First'].lower()),
                        "email": str(row['Email'])}
        student_dict = {k:v for k, v in student_dict.items() if v != 'nan'}
        cohort_json['cohort'].append(student_dict)
    return cohort_json


def make_cohort_json(csv_path):
    df = prepare_df(csv_path)
    cohort_json = make_cohort_dict(df)
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
        img.save(img_path, "JPEG")
    return img_path


def decrease_image_res(img_path):
    '''
    Decreases image resolution to 72dpi
    '''
    im = Image.open(img_path)
    print(img_path)
    if im.info['dpi'][0] > 72 and im.info['dpi'][0] > 72:
        im.save(img_path, dpi = (72, 72))


def prepare_images(img_dir, ignore_files = ['.DS_Store']):
    existing_img_list = [im for im in os.listdir(img_dir) if im not in ignore_files]
    for img_name in existing_img_list:
        full_img_path = convert_to_jpg(img_dir+'/'+img_name)
        decrease_image_res(full_img_path)
    #make_flipped_images(existing_image_list)
    print("prepared all images in {}".format(img_dir))


##################
### DO NOT USE ###
###   BROKEN   ###
### NEEDS FIXN ###
##################

def calc_min_img_ratio(img_dir):
    min_ratio = 10000 #just make a really large number to start with
    for img_path in os.listdir(img_dir):
        img = Image.open(img_dir+img_path)
        s = img.size
        if s[0]/s[1] < min_ratio:
            min_ratio = s[0]/s[1]
    return min_ratio


def crop_image(img_path, ratio, desired_width = 1024, desired_height = 153):
    img = Image.open(img_path)
    width, height = img.size

    new_height_half = (width/ratio)/2

    # width_diff = width - desired_width
    # height_diff = height - desired_height
    #
    # if width_diff < 0:
    #     raise Exception ("Image too narrow")
    # else:
    #     remove_left_right = width_diff/2
    #
    # if height_diff < 0:
    #     raise Exception ("Image too short")
    # else:
    #     remove_top_bottom = height_diff/2



    cropped = img.crop((0, new_height_half, width, height - new_height_half))
    cropped.save(img_path, "JPEG")
