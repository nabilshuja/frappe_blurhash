import blurhash
import frappe
import numpy as np
import requests
from frappe.core.doctype.file.file import get_local_image, get_web_image


def on_file_upload(doc, methods=None):
    if not is_valid_file_for_blurhash_creation(doc):
        return
    frappe.enqueue(set_blur_hash, enqueue_after_commit=True, queue="short", now=True, doc=doc)


MAX_RESIZE = (512, 512)


def set_blur_hash(doc):
    # gracefully handle failure's of blurhash
    try:
        if doc.file_url:
            if doc.file_url.startswith("/files") or doc.file_url.startswith("/private/files"):
                try:
                    image, filename, extn = get_local_image(doc.file_url)
                    image.thumbnail(MAX_RESIZE)
                except IOError:
                    return

            else:
                try:
                    image, filename, extn = get_web_image(doc.file_url)
                    image.thumbnail(MAX_RESIZE)
                except (
                    requests.exceptions.HTTPError, requests.exceptions.SSLError,
                    IOError,
                    TypeError):
                    return
            doc.db_set('blurhash', blurhash.encode(np.array(image.convert("RGB"))))
        return doc
    except Exception:
        frappe.log_error(title=f"Failed to create blurhash for file {doc.name}.")


def is_valid_file_for_blurhash_creation(file_doc):
    """
    Conditions to create blurhash..
    => Extension of file should be valid image
    """
    from frappe.utils import is_image
    path = file_doc.get_full_path()
    return is_image(path)
