"""image processing module"""
from __future__ import division



from builtins import str
from builtins import object
import sys
from io import StringIO
from PIL import Image, ImageDraw, ImageFont, ImagePalette
from utils.exception import VDOM_exception
import managers

class VDOM_imaging(object):
	"""imaging class"""

	def __init__(self):
		"""constructor"""
		self.__im = None
		self.__font = None
		self.__format = None
		#from src!.utils import font_factory
		#self.__font_factory = font_factory

	def load(self, application_id, res_id):
		"""load image from file"""
		self.__im = None
		try:
			resource = managers.resource_manager.get_resource(application_id,res_id)
			if not resource:
				raise VDOM_exception(("Cannot load resource"))
		except:
			debug("[Imagin]Error reading resource %s:%s\n" % (str(application_id), str(res_id))) #TODO: change to logger
			return ""

		formats = {"jpg": "JPEG", "jpeg": "JPEG", "gif": "GIF", "bmp": "BMP","png": "PNG"}
		
		if resource.res_format.lower() in formats:
			self.__format = formats[resource.res_format.lower()]
			
		try:
			self.__im = Image.open(StringIO(resource.get_data()))
		except: 
			debug("[Imagin]Resource loading failture: "+str(resource.id))

		
		return self.__im
		
	#def get_fonts(self):
	#	return self.__font_factory.get_font_families()

	def create_font(self, name = "arial.ttf", size = 12, color = "black", fontstyle = 'normal', fontweight = 'normal'):
		"""load font"""
		try:
			self.__font = ImageFont.truetype(VDOM_CONFIG["FONT-DIRECTORY"] + "/" + name + ".ttf", size,0, encoding="unic")
			#self.__font = self.__font_factory.get_font(name, size, fontstyle = fontstyle, fontweight = fontweight)
		except Exception as e:
			self.__font = ImageFont.truetype(VDOM_CONFIG["FONT-DIRECTORY"] + "/arial.ttf", size,0, encoding="unic")			
			debug("creating font error")
			debug(str(e))			
			#self.__font = self.__font_factory.get_font("arial", size, fontstyle = fontstyle, fontweight = fontweight)

	def write_text(self, text, color=(0,0,0), align="", ident=0, textdecoration = 'none'):
		"""write text on the image"""
		if not self.__im: return
		if not self.__font: self.create_font()
		
		if self.__im.mode == "P":
			self.__im =  self.__im.convert("RGB")
			self.__format = "PNG"
			
		(txtw, txth) = self.__font.getsize(text)
		(imgw, imgh) = self.__im.size
		
		if align == "left":
			if txtw + int(ident) < imgw:
				left = int(ident)
			else:
				left = 0
		elif align == "right":
			if txtw + int(ident) < imgw:
				left = imgw - txtw - int(ident)
			else:
				left = imgw - txtw
		else:
			left = (imgw - txtw) / 2
		top = (imgh - txth) /  2
		
		draw = ImageDraw.Draw(self.__im)
		try:
			draw.text((left , top), text, font = self.__font, fill = color)
			if textdecoration == 'underline':
				right = left + txtw
				y = top + txth * 8 / 9
				draw.line([(left, y) , (right, y)], fill = color)			
		except Exception as e: 
			debug("!!!!!!!!!!!!VDOM_imagin error:")
			debug(str(e))
		
	def crop(self,x,y,w,h):
		"""returns a rectangular region from the current image"""
		if not self.__im: return ""
		self.__im = self.__im.crop((x,y,x+w,y+h))
		
	def thumbnail(self, size):
		"""resize image for preview"""
		if not self.__im: return ""
		self.__im.thumbnail(size, Image.ANTIALIAS)
		
	def save_temporary(self, application_id, object_id, label, format = "JPEG"):
		"""save temporary image to file"""
		if not self.__im: return ""
		exts = {"JPEG": "jpg", "BMP":"bmp", "GIF":"gif" , "PNG" : "png"}
		output = StringIO()

		if self.__format:
			self.__im.save(output, self.__format, quality=100)
			extension = exts[self.__format]
		else:
			self.__im.save(output, format, quality=100)
			extension = exts[format]
			self.__format = format

		attributes = {
			"name" : label,
			"res_format": self.__format,
			"res_type" : "temporary",
			"label" : label
		}
		
		res_id = managers.resource_manager.add_resource(application_id, object_id, attributes, output.getvalue())

		return res_id
	def save(self, application_id, name, format = "JPEG"):
		"""save image to resources"""
		if not self.__im: return ""
		exts = {"JPEG": "jpg", "BMP":"bmp", "GIF":"gif" , "PNG" : "png"}
		output = StringIO()

		if self.__format:
			self.__im.save(output, self.__format, quality=100)
			extension = exts[self.__format]
		else:
			self.__im.save(output, format, quality=100)
			extension = exts[format]
			self.__format = format

		attributes = {
			"name" : name,
			"res_format": self.__format,
			"res_type" : "permanent"

		}
		
		res_id = managers.resource_manager.add_resource(application_id, None, attributes, output.getvalue())

		return res_id
	def __get_size(self):
		if not self.__im: return (0,0)
		return self.__im.size
	size=property(__get_size, None)
