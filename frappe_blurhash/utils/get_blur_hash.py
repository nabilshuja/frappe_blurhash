import frappe


def get_blur_hash(dt, dn, df):
    """
    dt : Doc-type
    dn : Doc-name
    df : Doc-field
    """
    if "frappe_blurhash" not in frappe.get_installed_apps():
        return frappe.throw(frappe._("Frappe blurhash not installed in current site."))
    fields = ["blurhash"]
    file_url = frappe.get_value(dt, dn, df)
    if frappe.is_table(dt):
        dt, dn = frappe.get_value(dt, dn,
                                  ("parenttype", "parent"))
    attachments = get_attachments_by_docfield(dt, dn, df, file_url, fields)
    return attachments[0].get("blurhash") if len(attachments) else None


def get_attachments_by_docfield(dt, dn, df, file_url, fields):
    filters = {"attached_to_name": dn, "file_url": file_url,
               "attached_to_doctype": dt, "attached_to_field": df}
    files = frappe.get_all("File", fields=fields, filters=filters)
    if not files:
        # lets try again to find the image just by looking at file_url
        files = frappe.get_all("File", fields=fields,
                               filters={"file_url": file_url,
                                        "blurhash": ("!=", "")})
    return files
