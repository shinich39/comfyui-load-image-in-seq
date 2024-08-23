"""
@author: shinich39
@title: Load Image In Seq
@nickname: Load Image In Seq
@version: 1.0.4
@description: Load png image sequentially with metadata.
"""

import numpy as np
import torch
import os
import comfy
import folder_paths
import folder_paths as comfy_paths
import shutil
from pathlib import Path
from io import BytesIO
from server import PromptServer
from aiohttp import web
from PIL import ImageFile, Image, ImageOps
from PIL.PngImagePlugin import PngInfo
from .libs.parser import parse_png
from .libs.utils import get_all_image_files

# fix
ImageFile.LOAD_TRUNCATED_IMAGES = True

DEBUG = False
VERSION = "1.0.4"
WEB_DIRECTORY = "./js"
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

@PromptServer.instance.routes.get("/shinich39/liis/get_image")
async def get_image(request):
  if "path" in request.rel_url.query:
    file_path = request.rel_url.query["path"]
    if os.path.isfile(file_path):
      filename = os.path.basename(file_path)
      with Image.open(file_path) as img:
        image_format = 'webp'
        quality = 90
        buffer = BytesIO()
        img.save(buffer, format=image_format, quality=quality)
        buffer.seek(0)

        return web.Response(body=buffer.read(), content_type=f'image/{image_format}',
          headers={"Content-Disposition": f"filename=\"{filename}\""})

  return web.Response(status=404)

@PromptServer.instance.routes.post("/shinich39/liis/get_images")
async def get_images(request):
  req = await request.json()
  dir_path = req["dirPath"]
  files = []

  try:
    file_list = get_all_image_files(dir_path)
    for file_path in file_list:

      mask_name = "."+Path(file_path).name
      mask_path = Path(dir_path).joinpath(mask_name).as_posix()

      file = {}
      file["original_path"] = file_path
      file["original_name"] = Path(file_path).resolve().stem
      file["mask_path"] = mask_path

      if os.path.exists(file_path):
        if not os.path.exists(mask_path):
          shutil.copyfile(file_path, mask_path)

        p_prompt, n_prompt, setting, parameter = parse_png(file_path)

        file["model"] = None if parameter["model"] == "None" else parameter["model"]
        file["positive"] = None if not p_prompt else p_prompt
        file["negative"] = None if not n_prompt else n_prompt
        file["seed"] = None if parameter["seed"] == "None" else parameter["seed"]
        file["steps"] = None if parameter["steps"] == "None" else parameter["steps"]
        file["cfg"] = None if parameter["cfg"] == "None" else parameter["cfg"]
        file["sampler_name"] = None if parameter["sampler"] == "None" else parameter["sampler"]
        file["scheduler"] = None if parameter["scheduler"] == "None" else parameter["scheduler"]
        file["denoise"] = None if parameter["denoise"] == "None" else parameter["denoise"]

      files.append(file)

  except Exception as err:
    print(err)

  return web.json_response(files)

@PromptServer.instance.routes.post("/shinich39/liis/save_mask")
async def upload_mask(request):
  post = await request.post()
  image = post.get("image")
  original_path = post.get("original_path")
  mask_path = post.get("mask_path")

  if os.path.isfile(original_path):
    with Image.open(original_path) as original_pil:
      metadata = PngInfo()
      if hasattr(original_pil,'text'):
        for key in original_pil.text:
          metadata.add_text(key, original_pil.text[key])
      original_pil = original_pil.convert('RGBA')
      mask_pil = Image.open(image.file).convert('RGBA')

      # alpha copy
      new_alpha = mask_pil.getchannel('A')
      original_pil.putalpha(new_alpha)
      original_pil.save(mask_path, compress_level=4, pnginfo=metadata)

    return web.json_response({ "mask_path": mask_path })

@PromptServer.instance.routes.post("/shinich39/liis/remove_mask")
async def remove_mask(request):
  req = await request.json()
  original_path = req["original_path"]
  mask_path = req["mask_path"]

  if os.path.exists(original_path):
    shutil.copyfile(original_path, mask_path)

  return web.Response(status=200)
  
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
    file_list = get_all_image_files(dir_path)
    file_path = file_list[(index + len(file_list)) % len(file_list)]
    mask_name = "."+Path(file_path).name
    mask_path = Path(dir_path).joinpath(mask_name).as_posix()
    is_mask_exists = os.path.exists(mask_path)
  
    # image
    image = Image.open(mask_path if is_mask_exists else file_path)
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