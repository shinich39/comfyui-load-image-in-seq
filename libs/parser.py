from PIL import Image
from PIL.PngImagePlugin import PngInfo, PngImageFile
from PIL.JpegImagePlugin import JpegImageFile

from .comfyui import ComfyUI

def parse_png(file_path):
  with Image.open(file_path) as image:
    if not isinstance(image, PngImageFile):
      raise Exception("Only supported for PNG format")

    width = image.width
    height = image.height
    info = image.info
    format = image.format
    
    parser = ComfyUI(info=info, width=width, height=height)
    positive = parser.positive
    negative = parser.negative
    setting = parser.setting
    parameter = parser.parameter

    return positive, negative, setting, parameter