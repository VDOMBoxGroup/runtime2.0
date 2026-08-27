class VDOM_pagination(VDOM_object):

    def pages_count(self):
        """ get correct pages_count value. Method include some checks """

        pages_count = 1

        try:
            pages_count = int(self.pagescount)
        except Exception:
            pages_count = 1

        if pages_count < 0:
            pages_count = 1

        return pages_count


    def current_page(self):
        """ get correct current_page value """

        current_page = 1

        try:
            current_page = int(self.currentpage)
        except Exception:
            current_page = 1

        if current_page < 0:
            current_page = 1
        if current_page > self.pages_count():
            current_page = self.pages_count()

        return current_page


    def show_count(self):
        """ get correct showcount value """

        show_count = 0

        try:
            show_count = int(self.showcount)
        except Exception:
            show_count = 0

        if show_count < 9:
            show_count = 9

        return show_count


    def section_count(self):
        """ comput count of sections """

        if self.pages_count() <= self.show_count():
          return self.pages_count()

        return self.show_count() / 3


    def css_class(self):
        """ create unique css class for this object """
        return 'pagination-' + self.id

    
    def css_style(self):
      """ return css style of this object """

      if not self.style:
          return ''

      #fix error with percents in format
      style = self.style.replace('%', '%%')
      style = style.replace('%%(', '%(')

      try:
          return style % {"css_class": 'div.' + self.css_class()}
      except Exception:
          return ''

    
    def need_to_render(self):
        """ check pagination.. may be it don't need to render """

        if self.visible == "0":
            return False

        if self.pages_count() > 1:
            return True
        else:
            return False

    
    def page_link(self, page):
        """ Create link of one page on pagination """

        result = u"""
            <a onclick='execEventBinded("%(id)s", "pageSelected", {"pagenumber": "%(page_number)s"})'>
                %(page_number)s
            </a>
        """ % { "id"          : self.id.replace('-', '_'),
                "page_number" : page}

        return result


    def create_empty_td_element(self):
        """ create html <td> element with dots """

        result = u"""<td class='empty'>...</td>"""
        return result


    def create_td_element(self, page):
        """ create html <td> element for one link in pagination """

        page_link = self.page_link(page)

        #mark current page
        if page == self.current_page():
                page_link = u"<span>{page}</span>".format(page = str(page))

        result = u"<td>{page_link}</td>".format(page_link = page_link)

        return result

    
    def create_td_elements(self):
        """ create all td elements """

        sections_dict = self.create_sections_dict()
        result = ""

        pages_list = self.create_pages_list()

        last_i = 1
        for i in pages_list:
            if int(i) - last_i > 1:
                result += self.create_empty_td_element()
            result += self.create_td_element(i)
            last_i = i

        return result

    
    def create_pages_list(self):
        """ Create one list of pages """

        result = []
        sections_dict = self.create_sections_dict()

        for key in sorted(sections_dict):
            result += sections_dict[key]

        return result

    
    def create_sections_dict(self):
        """ Create dictionary for three sections of pagination.
            In result will be dictionary with lists of pages.
              result["1"] - first section
              result["2"] - second
              result["3"] - third
        """

        result = {"1": "", "2": "", "3": ""}

        count = self.section_count() #count of elements in section

        #section 1
        begin = 1
        end = begin + count

        result["1"] = range(begin, end)
        if self.pages_count() <= count:
            return result


        #section 2
        begin = self.current_page() - count / 2 #center of section 2 - current_page

        if self.current_page() >= self.pages_count() - count: #current page in the end of section 2
            begin = self.pages_count() - count * 2 + 1

        if begin < end: #begin of section 2 > end of section 1 => need "..."
            begin = end

        end = begin + count
        result["2"] = range(begin, end)



        #section 3
        begin = self.pages_count() - count + 1

        if begin < end: #begin of section 3 > end of section 2 => need "..."
            begin = end

        count = self.pages_count() - begin + 1
        end = begin + count
        result["3"] = range(begin, end)

        return result

    def check_unit(self, value):
        return value + "px" if value.isdigit() else value
    
    def render(self, contents=""):
        """ Render of this type object """

        # check if not need to render

        #create pagination output
        table_data = self.create_td_elements()

        table = u"""<table width="100%"><tr>{tabledata}</tr></table>""".format(tabledata = table_data)
        
        display = u"none" if self.visible == "0" else self.displaying
        position = self.positioning if self.positioning and self.positioning != "static" else u""

        if not self.need_to_render():
            table = ""

        styles = {
            "z-index": self.zindex if int(self.zindex) != 0 else u"",
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "position": position,
            "display": display
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
        
        style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])
        
        result = \
            u"""<style>{css_style}</style>
                <div id="o_{id}" objname="{name}" class="{css_class}" style="{style}">
                    {table}
                </div>
            """.format(id=self.id.replace('-', '_'),
                style=style,
                table=table,
                css_class=self.css_class(),
                css_style=self.css_style(),
                name=self.name)

        return VDOM_object.render(self, contents=result)


    def wysiwyg(self, contents=""):
        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]
        
        if not self.need_to_render():
            from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

            image_id = "2ff58b6b-d20a-a45b-7c2a-16bad6d574ec"
            result = get_empty_wysiwyg_value(self, image_id)

            return VDOM_object.wysiwyg(self, contents=result)


        table_data = "<table width='100%'><tr>" + self.create_td_elements() + "</tr></table>"
        css_style = "<style>" + self.css_style() + "</style>"
        css_class = self.css_class()

        result = \
            u"""
                <container name="{name}" id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}" order="{order}"
                    top="{top}" left="{left}" width="{width}" height="{height}">

                    <svg>
                        <rect x="0" y="0"width="{width}" height="{height}" fill="#000000" fill-opacity="0" />
                    </svg>

                    <htmltext width="{width}" height="{height}" overflow="visible">
                        {css_style}
                        <div class="{css_class}">
                            {table_data}
                        </div>
                    </htmltext>

                </container>
            """.format(
                id = self.id, name = self.name,
                visible =  self.visible, zindex = self.zindex,
                hierarchy = self.hierarchy, order = self.order,
                top = self.top, left = self.left,
                width = self.width, height = self.height,
                table_data = table_data,
                css_style = css_style,
                css_class = css_class)

        return VDOM_object.wysiwyg(self, contents=result)

def on_update(object, attributes):
    o = object
    mods = {}
    
    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, '').lower()
            
            if obj_value.isdigit() and attr_value.isdigit():
                mods[attr] = attr_value + "px"
                mods["ide_"+ attr] = attr_value
            elif obj_value.endswith("px") and (attr_value.isdigit() or "px" in attr_value):
                mods[attr] = attr_value.rstrip("px") + "px"
                mods["ide_"+ attr] = attr_value.rstrip("px")
            elif attr_value.isdigit() or "px" in attr_value:
                mods[attr] = attr_value if "px" in attr_value else obj_value
                mods["ide_"+ attr] = attr_value.rstrip("px")
            else:
                mods[attr] = attr_value
    attributes.update(mods)

#     users = """
# #%(id)s {

# }
# """
    # skin_mapping = {
    #     "0": users,
    #     "1": ""
    # }
#    if "skin" in attributes:
#    	skin = attributes["skin"]
#    	if skin in skin_mapping:
#    		attributes.update(style=skin_mapping[skin])
#    	else:
#    		attributes.update(skin="0")
#    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
#    	attributes.update(skin="0")
        
    return ""
    
def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]
        
        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_"+ attr] = obj_value.rstrip("px")