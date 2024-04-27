"""
@author: shinich39
@title: Load Image In Seq
@nickname: Load Image In Seq
@version: 1.0.2
@description: Load png image sequentially with metadata.
"""

import server
import numpy as np
import torch
import os
import comfy
import folder_paths as comfy_paths
from server import PromptServer
from aiohttp import web
from PIL import Image, ImageOps
from .libs.parser import parse_png
from .libs.utils import load_image_from_directory

DEBUG = False
VERSION = "1.0.2"
WEB_DIRECTORY = "./js"
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# main
class LoadImageInSeq():
  def __init__(self):
    pass

  @classmethod
  def INPUT_TYPES(cls):
    return {
      "hidden": {
        "unique_id": "UNIQUE_ID", # for update index
      },
      "required": {
        "dir_path": ("STRING", {"default": "./ComfyUI/input"}),
        "mode": (["fixed", "increment"],),
        "index":  ("INT", {"default": 0, "min": 0, "step": 1}),
      },
      "optional": {
        "default_ckpt_name": (comfy_paths.get_filename_list("checkpoints"), ),
        "default_positive": ("STRING", {"default": "", "multiline": True}),
        "default_negative": ("STRING", {"default": "", "multiline": True}),
        "default_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
        "default_steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
        "default_cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
        "default_sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
        "default_scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
        "default_denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
      },
    }
  
  @classmethod
  def IS_CHANGED(cls, **kwargs):
    return float("NaN")

  CATEGORY = "image"
  RETURN_TYPES = ("IMAGE", "MASK", "STRING", "INT", "STRING", "STRING", "STRING", "INT", "INT", "FLOAT", "STRING", "STRING", "FLOAT")
  RETURN_NAMES = ("image", "mask", "filename", "index", "ckpt_name", "positive", "negative", "seed", "steps",  "cfg", "sampler_name", "scheduler", "denoise")

  FUNCTION = "exec"

  def exec(self, unique_id, dir_path, mode, index, default_ckpt_name, default_positive, default_negative, default_seed, default_steps, default_cfg, default_sampler_name, default_scheduler, default_denoise):
    if DEBUG:
      print(f"LoadImageInSeq.unique_id: {unique_id}")
      print(f"LoadImageInSeq.dir_path: {dir_path}")
      print(f"LoadImageInSeq.mode: {mode}")
      print(f"LoadImageInSeq.index: {index}")

    if not os.path.isdir(dir_path):
      raise FileNotFoundError(f"{dir_path} not found.")
  
    # load
    image, file_path, file_name, file_length, file_index = load_image_from_directory(dir_path, index)

    if image is None:
      raise FileNotFoundError(f"Image not found.")
    
    if DEBUG:
      print(f"LoadImageInSeq.file_path: {file_path}")
      print(f"LoadImageInSeq.file_name: {file_name}")
      print(f"LoadImageInSeq.file_length: {file_length}")
      print(f"LoadImageInSeq.file_index: {file_index}")
      
    # parse
    p_prompt, n_prompt, setting, parameter = parse_png(file_path)

    if DEBUG:
      print(f"LoadImageInSeq.positive: {p_prompt}")
      print(f"LoadImageInSeq.negative: {n_prompt}")
      print(f"LoadImageInSeq.setting: {setting}")
      print(f"LoadImageInSeq.parameter: {parameter}")

    model = default_ckpt_name if parameter["model"] == "None" else parameter["model"]
    positive = default_positive if not p_prompt else p_prompt
    negative = default_negative if not n_prompt else n_prompt
    seed = default_seed if parameter["seed"] == "None" else parameter["seed"]
    steps = default_steps if parameter["steps"] == "None" else parameter["steps"]
    cfg = default_cfg if parameter["cfg"] == "None" else parameter["cfg"]
    sampler_name = default_sampler_name if parameter["sampler"] == "None" else parameter["sampler"]
    scheduler = default_scheduler if parameter["scheduler"] == "None" else parameter["scheduler"]
    denoise = default_denoise if parameter["denoise"] == "None" else parameter["denoise"]

    # image
    img = ImageOps.exif_transpose(image)
    image = img.convert("RGB")
    image = np.array(image).astype(np.float32) / 255.0
    image = torch.from_numpy(image)[None,]
    if 'A' in img.getbands():
      mask = np.array(img.getchannel('A')).astype(np.float32) / 255.0
      mask = 1. - torch.from_numpy(mask)
    else:
      mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

    if mode == "increment":
      updates = {}
      updates[unique_id] = file_index + 1 if file_index + 1 < file_length else 0

      # update index
      server.PromptServer.instance.send_sync("load-image-in-seq", updates)

    return (image, mask.unsqueeze(0), file_name, file_index, model, positive, negative, seed, steps, cfg, sampler_name, scheduler, denoise)

NODE_CLASS_MAPPINGS["Load Image In Seq"] = LoadImageInSeq
NODE_DISPLAY_NAME_MAPPINGS["Load Image In Seq"] = "Load Image In Seq"