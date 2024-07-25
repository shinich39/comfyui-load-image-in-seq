"""
@author: shinich39
@title: Load Image In Seq
@nickname: Load Image In Seq
@version: 1.0.3
@description: Load png image sequentially with metadata.
"""

import numpy as np
import torch
import os
import comfy
import folder_paths
import folder_paths as comfy_paths
from server import PromptServer
from aiohttp import web
from PIL import ImageOps
from .libs.parser import parse_png
from .libs.utils import load_image_from_directory

DEBUG = False
VERSION = "1.0.3"
WEB_DIRECTORY = "./js"
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

@PromptServer.instance.routes.post("/shinich39/get_metadata")
async def get_metadata(request):
  req = await request.json()
  dir_path = req["dirPath"]
  index = req["index"]
  res = {}
  res["file_index"] = index

  try:
    image, file_path, file_name, file_length, file_index = load_image_from_directory(dir_path, index)
    res["filename"] = file_name
    res["file_path"] = file_path
    res["file_length"] = file_length
    res["file_index"] = file_index
    if os.path.exists(file_path):
      p_prompt, n_prompt, setting, parameter = parse_png(file_path)
      model = None if parameter["model"] == "None" else parameter["model"]
      positive = None if not p_prompt else p_prompt
      negative = None if not n_prompt else n_prompt
      seed = None if parameter["seed"] == "None" else parameter["seed"]
      steps = None if parameter["steps"] == "None" else parameter["steps"]
      cfg = None if parameter["cfg"] == "None" else parameter["cfg"]
      sampler_name = None if parameter["sampler"] == "None" else parameter["sampler"]
      scheduler = None if parameter["scheduler"] == "None" else parameter["scheduler"]
      denoise = None if parameter["denoise"] == "None" else parameter["denoise"]
      res["model"] = model
      res["positive"] = positive
      res["negative"] = negative
      res["seed"] = seed
      res["steps"] = steps
      res["cfg"] = cfg
      res["sampler_name"] = sampler_name
      res["scheduler"] = scheduler
      res["denoise"] = denoise

  except Exception as err:
    print(err)

  return web.json_response(res)

# main
class LoadImageInSeq():
  def __init__(self):
    pass

  @classmethod
  def INPUT_TYPES(cls):
    return {
      "required": {
        "dir_path": ("STRING", {"default": "./ComfyUI/input"}),
        "mode": (["fixed", "increment"],),
        "index":  ("INT", {"default": 0, "min": 0, "step": 1}),
      },
      "optional": {
        "filename": ("STRING", {"default": "",}),
        "ckpt_name": (comfy_paths.get_filename_list("checkpoints"), ),
        "positive": ("STRING", {"default": "", "multiline": True}),
        "negative": ("STRING", {"default": "", "multiline": True}),
        "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
        "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
        "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
        "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
        "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
        "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
      },
    }

  CATEGORY = "image"
  RETURN_TYPES = ("IMAGE", "MASK", "STRING", "MODEL", "CLIP", "VAE", "STRING", "STRING", "INT", "INT", "FLOAT", "STRING", "STRING", "FLOAT")
  RETURN_NAMES = ("IMAGE", "MASK", "FILE_NAME", "MODEL", "CLIP", "VAE", "POSITIVE", "NEGATIVE", "SEED", "STEPS",  "CFG", "SAMPLER_NAME", "SCHEDULER", "DENOISE")

  FUNCTION = "exec"

  def exec(self, dir_path, mode, index, filename, ckpt_name, positive, negative, seed, steps, cfg, sampler_name, scheduler, denoise):
    if DEBUG:
      print(f"dir_path: {dir_path}")
      print(f"mode: {mode}")
      print(f"index: {index}")
      print(f"filename: {filename}")
      print(f"ckpt_name: {ckpt_name}")
      print(f"positive: {positive}")
      print(f"negative: {negative}")
      print(f"seed: {seed}")
      print(f"steps: {steps}")
      print(f"cfg: {cfg}")
      print(f"sampler_name: {sampler_name}")
      print(f"scheduler: {scheduler}")
      print(f"denoise: {denoise}")

    # load image
    image, file_path, file_name, file_length, file_index = load_image_from_directory(dir_path, index)
      
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

    # load ckpt
    if ckpt_name:
      ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)
      ckpt = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"))
    else:
      ckpt = [None, None, None]
    
    return (image, mask.unsqueeze(0), filename, ckpt[0], ckpt[1], ckpt[2], positive, negative, seed, steps, cfg, sampler_name, scheduler, denoise)

NODE_CLASS_MAPPINGS["Load Image In Seq"] = LoadImageInSeq
NODE_DISPLAY_NAME_MAPPINGS["Load Image In Seq"] = "Load Image In Seq"