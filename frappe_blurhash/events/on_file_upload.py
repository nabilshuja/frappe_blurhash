import blurhash
import frappe
import numpy as np
import requests
from frappe.core.doctype.file.file import get_local_image, get_web_image


def on_file_upload(doc, methods=None):
    frappe.enqueue(set_blur_hash, enqueue_after_commit=True, queue="short",
                   now=frappe.flags.in_test, doc=doc)


MAX_RESIZE = (512, 512)


def set_blur_hash(doc):
    # TODO create doctype settings for components
    if doc.file_url:
        if doc.file_url.startswith("/files"):
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
