import frappe
import blurhash
import numpy as np
from PIL import Image

def is_image_path(path):
  if not path:
    return
  exts = ["jpg", "jpeg", "png"]
  path = path.lower()
  for e in exts:
    if e in path:
      return True
  return False


def on_file_upload(doc, methods=None):
  if not is_image_path(doc.file_url) or doc.is_private:
    return doc
  # TODO create doctype settings for components
  file_url = doc.file_url
  if file_url.startswith("/private"):
    file_url_path = (file_url.lstrip("/"),)
  else:
    file_url_path = ("public", file_url.lstrip("/"))

  file_path = frappe.get_site_path(*file_url_path)

  image = Image.open(file_path)

  hash = blurhash.encode(np.array(image.convert("RGB")))
  doc.db_set('blurhash', hash)
  return doc



