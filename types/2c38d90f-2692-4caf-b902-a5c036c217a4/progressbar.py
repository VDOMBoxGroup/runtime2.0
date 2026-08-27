from scripting.legacy.id import id2link1


class VDOM_progressbar(VDOM_object):

    def render(self, contents=""):
        css1 = u" position:absolute; overflow:hidden; position:relative; left:{left}px; top:{top}px; ".format(
            left=self.left, top=self.top)
        css2 = u" position:absolute; left:0; top:0; "

        if self.visible == "0":
            css1 += u" display:none; "

        image1 = id2link1(self.image1)
        image2 = id2link1(self.image2)

        if self.skin == "1":
            css1 += u""" width:250px; height:26px; background:url("/361b54a5-a944-8020-ff02-e5d396cd8d04.res"); """
            css2 += u""" height:26px; background:url("/225ef69a-9a1c-e0e8-b240-4174ea3a4881.res"); """
        else:
            css1 += u""" width:{width}px; height:{height}px; background:url("{image}"); """.format(
                    width=self.width, height=self.height, image=image1)
            css2 += u""" height:{height}px; background:url("{image}"); """.format(
                    height=self.height, image=image2)

        val = self.get_current_value()

        css2 += u" width:{val}%; ".format(val=val)

        id = 'o_' + (self.id).replace('-', '_')

        result = u"""<div id="{id}" style='{css1}' min="{min}" max="{max}">
    <div style='{css2}'></div>
</div>""".format(id=id, css1=css1, css2=css2, min=min, max=max)

        return VDOM_object.render(self, contents=result)

    def get_current_value(self):
        min = int(self.min)
        max = int(self.max)
        val = int(self.value)
        if max < min:
            max = min
        if val < min:
            val = min
        if val > max:
            val = max

        if max == min:
            return 0

        val = (val * 100) / (max - min)
        return val

    def wysiwyg(self, contents=""):

        image_id1 = "361b54a5-a944-8020-ff02-e5d396cd8d04"
        image_id2 = "225ef69a-9a1c-e0e8-b240-4174ea3a4881"
        image_width = 250
        image_height = 26

        if self.skin == "0":	 # user defined skin
            if not self.image1 and not self.image2:
                from scripting.legacy.wysiwyg import get_empty_wysiwyg_value
                image_id = "3c36e7e5-2d35-51ae-d589-16c14c1237e3"
                result = get_empty_wysiwyg_value(self, image_id)
                return VDOM_object.wysiwyg(self, contents=result)
            else:
                image_id1 = self.image1
                image_id2 = self.image2
                image_width = int(self.width)
                image_height = int(self.height)

        progress_image = u""
        progress_width = (int(image_width) * self.get_current_value()) / 100

        if progress_width > 0:
            progress_image = u"""<image x="0" y="0" href="#Res({image2})" repeat="repeat" containerWidth="{width}" containerHeight="{height}"/>""".format(
                image2=image_id2, width=progress_width, height=image_height)

        result =\
            u"""<container name="{name}" id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}" order="{order}" top="{top}" left="{left}" width="{width}" height="{height}">
                <svg>
                    <image x="0" y="0" href="#Res({image1})" repeat="repeat" containerWidth="{width}" containerHeight="{height}"/>
                        {progress_image}
                    </svg>
                </container>""".format(
                id=self.id, visible=self.visible, zindex=self.zindex,
                hierarchy=self.hierarchy, order=self.order,
                top=self.top, left=self.left, name=self.name,
                width=image_width, height=image_height,
                image1=image_id1,
                progress_image=progress_image)

        return VDOM_object.wysiwyg(self, contents=result)