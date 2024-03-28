import os
from PIL import Image, ImageOps

def get_all_image_files(dir_path):
  image_list = []
  valid_extensions = [".jpg",".gif",".png",".tga"]

  for file in os.listdir(dir_path):
    ext = os.path.splitext(file)[1]

    if ext.lower() not in valid_extensions:
      continue

    image_list.append(os.path.join(dir_path, file))

  return image_list

def load_image_from_directory(dir_path, image_index):
  file_list = get_all_image_files(dir_path)
  file_length = len(file_list)

  if file_length == 0:
    return None, -1
  
  file_index = (file_length + image_index) % file_length
  file_path = file_list[file_index]
  file_name = os.path.basename(file_path)

  image = Image.open(file_path)

  return image, file_path, file_name, file_index
