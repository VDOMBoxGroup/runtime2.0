


from io import StringIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

import managers, security
from uuid import uuid4

class VDOM_resource_editor(object):
    """resource editor class"""

    def __init__(self):
        self.formats = {"jpg": "JPEG", "jpeg": "JPEG", "gif": "GIF", "bmp": "BMP","png": "PNG"}
        self.converts = {"jpg": "RGB", "jpeg": "RGB", "png": "RGB"}

    def modify_resource(self, sid, appid, objid, resid, attrname, operation, param):
        if not managers.acl_manager.session_user_has_access2(appid, appid, security.modify_application):
            raise VDOM_exception(("Modifying resource is not allowed"))
        app = managers.xml_manager.get_application(appid)
        obj = app.search_object(objid)
        # check if need to backup this resource
        need_backup = False
        key = objid + attrname
        s = managers.session_manager.get_session(sid)
        last = s.value("resource_editor_last")
        if key != last:
            need_backup = True
            s.value("resource_editor_last", "")
            if obj.has_attribute("resource_cache"):
                obj.set_attribute("resource_cache", "")
        # go
        ro = managers.resource_manager.get_resource(appid, resid)
        if not ro:
            return (False, _("Resource not found"))
        if not obj.has_attribute(attrname):
            return (False, _("Object has no attribute '%s'") % str(attrname))
        if not obj.has_attribute("resource_cache"):
            return (False, _("Object has no attribute 'resource_cache'"))
        res_data = ro.get_data()
        try:
            (data, msg, rest_wh) = getattr(self, operation)(s, app, obj, resid, attrname, res_data, ro, param)
            # save data in new resource
            if data:
                attributes = {
                    "id" : str(uuid4()),
                    "name" : ro.name,
                    "res_format": ro.res_format
                    }
                managers.resource_manager.add_resource(appid, None, attributes, data)
                if need_backup:
                    obj.set_attribute("resource_cache", "#Res(%s)" % resid)
                    s.value("resource_editor_last", key)
#               old_w = old_h = None
#               if rest_wh:
#                   try:
#                       old_w = obj.width
#                       old_h = obj.height
#                   except:
#                       rest_wh = False
                obj.set_attribute(attrname, "#Res(%s)" % attributes["id"])
                if rest_wh:
                    obj.set_attributes(rest_wh)
#                   obj.set_attributes({"width": old_w, "height": old_h})
            if data: return (True, data)
            else: return (True, msg)
        except Exception as e:
            return (False, str(e))

    def rollback(self, sess, app, obj, resid, attrname, data, ro, param):
        if "" != obj.attributes.resource_cache:
            sess.value("resource_editor_last", "")
            obj.set_attribute(attrname, obj.attributes["resource_cache"].original_value)
            obj.set_attribute("resource_cache", "")
        return (None, "", {"width": obj.attributes.width, "height": obj.attributes.height})

    def resize(self, sess, app, obj, resid, attrname, data, ro, param):
        img = Image.open(StringIO(data))
        if ro.res_format.lower() in self.converts and img.mode != self.converts[ro.res_format.lower()]:
            img = img.convert(self.converts[ro.res_format.lower()])
        new_img = img.resize((int(param["width"]), int(param["height"])), Image.BICUBIC)
        tw = StringIO()
        new_img.save(tw, self.formats[ro.res_format.lower()])
        return (tw.getvalue(), "", None)

    def brightness(self, sess, app, obj, resid, attrname, data, ro, param):
        img = Image.open(StringIO(data))
        if ro.res_format.lower() in self.converts and img.mode != self.converts[ro.res_format.lower()]:
            img = img.convert(self.converts[ro.res_format.lower()])
        f = float(param["factor"])
        f += 1
        if f < 0: f = 0
        enhancer = ImageEnhance.Brightness(img)
        new_img = enhancer.enhance(f)
        tw = StringIO()
        new_img.save(tw, self.formats[ro.res_format.lower()])
        return (tw.getvalue(), "", {"width": obj.attributes.width, "height": obj.attributes.height})

    def contrast(self, sess, app, obj, resid, attrname, data, ro, param):
        img = Image.open(StringIO(data))
        if ro.res_format.lower() in self.converts and img.mode != self.converts[ro.res_format.lower()]:
            img = img.convert(self.converts[ro.res_format.lower()])
        f = float(param["factor"])
        f += 1
        if f < 0: f = 0
        enhancer = ImageEnhance.Contrast(img)
        new_img = enhancer.enhance(f)
        tw = StringIO()
        new_img.save(tw, self.formats[ro.res_format.lower()])
        return (tw.getvalue(), "", {"width": obj.attributes.width, "height": obj.attributes.height})

    def crop(self, sess, app, obj, resid, attrname, data, ro, param):
        img = Image.open(StringIO(data))
        if ro.res_format.lower() in self.converts and img.mode != self.converts[ro.res_format.lower()]:
            img = img.convert(self.converts[ro.res_format.lower()])
        y = int(param["top"])
        x = int(param["left"])
        w = int(param["width"])
        h = int(param["height"])
        new_img = img.crop((x, y, x+w, y+h))
        new_img.load()
        tw = StringIO()
        new_img.save(tw, self.formats[ro.res_format.lower()])
        return (tw.getvalue(), "", {"width": obj.attributes.width, "height": obj.attributes.height})

    def flip(self, sess, app, obj, resid, attrname, data, ro, param):
        img = Image.open(StringIO(data))
        if ro.res_format.lower() in self.converts and img.mode != self.converts[ro.res_format.lower()]:
            img = img.convert(self.converts[ro.res_format.lower()])
        m = int(param["method"])
        new_img = None
        if 0 == m:
            new_img = img.transpose(Image.FLIP_TOP_BOTTOM)
        elif 1 == m:
            new_img = img.transpose(Image.FLIP_LEFT_RIGHT)
        new_img.load()
        tw = StringIO()
        new_img.save(tw, self.formats[ro.res_format.lower()])
        return (tw.getvalue(), "", {"width": obj.attributes.width, "height": obj.attributes.height})

    def greyscale(self, sess, app, obj, resid, attrname, data, ro, param):
        img = Image.open(StringIO(data))
        if ro.res_format.lower() in self.converts and img.mode != self.converts[ro.res_format.lower()]:
            img = img.convert(self.converts[ro.res_format.lower()])
        img.draft("L", img.size)
        tw = StringIO()
        debug(ro.res_format.lower())
        debug(str(self.formats))
        img.save(tw, self.formats[ro.res_format.lower()])
        return (tw.getvalue(), "", {"width": obj.attributes.width, "height": obj.attributes.height})

    def rotate(self, sess, app, obj, resid, attrname, data, ro, param):
        img = Image.open(StringIO(data))
        if ro.res_format.lower() in self.converts and img.mode != self.converts[ro.res_format.lower()]:
            img = img.convert(self.converts[ro.res_format.lower()])
        m = int(param["method"])
        new_img = None
        if 1 == m:
            new_img = img.transpose(Image.ROTATE_270)
        elif 0 == m:
            new_img = img.transpose(Image.ROTATE_90)
        new_img.load()
        tw = StringIO()
        new_img.save(tw, self.formats[ro.res_format.lower()])
        return (tw.getvalue(), "", {"width": obj.attributes.height, "height": obj.attributes.width})

    def do_thumbnail(self, format, data, width, height):
        img = Image.open(StringIO(data))
        if ro.res_format.lower() in self.converts and img.mode != self.converts[ro.res_format.lower()]:
            img = img.convert(self.converts[ro.res_format.lower()])
        new_img = img.resize((width, height), Image.BICUBIC)
        tw = StringIO()
        new_img.save(tw, self.formats[format])
        return tw.getvalue()
