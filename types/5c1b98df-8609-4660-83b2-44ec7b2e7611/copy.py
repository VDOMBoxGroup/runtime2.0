import re


def on_startup(object):
    source_object = object.application.objects.catalog.get(
        object.attributes["source_object"]
    )
    if source_object:
        source_object.attach(object)


def on_create(object):
    source_object = object.application.objects.catalog.get(
        object.attributes["source_object"]
    )
    if source_object:
        source_object.attach(object)


def on_delete(object):
    source_object = object.application.objects.catalog.get(
        object.attributes["source_object"]
    )
    if source_object:
        source_object.detach(object)


def on_update(object, attributes):
    if "source_object" in attributes:
        source_object = object.application.objects.catalog.get(
            object.attributes["source_object"]
        )
        if source_object:
            source_object.detach(object)
        source_object = object.application.objects.catalog.get(
            attributes["source_object"]
        )
        if source_object:
            source_object.attach(object)


def on_render(self, child):
    if self.top != "":
        child.top = self.top
    if self.left != "":
        child.left = self.left


def on_wysiwyg(self, child):
    child.top = 0
    child.left = 0


def on_compile(object, profile):
    source_object = object.application.objects.catalog.get(
        object.attributes["source_object"]
    )
    if source_object:
        profile.dynamic = 1
        profile.optimization_priority = source_object.type.optimization_priority
        with profile as entries:
            entries.new(source_object, on_render=on_render, on_wysiwyg=on_wysiwyg)


class VDOM_copy(VDOM_object):
    def check_cache(self):
        if self.source_object_cache != self.source_object:
            # reset copy position
            self.source_object_cache = self.source_object
            self.top = ""
            self.left = ""
            self.update("source_object_cache", "top", "left")

    def render(self, contents=""):
        self.check_cache()
        result = contents if self.visible == "1" else ""
        return VDOM_object.render(self, contents=result)

    def empty_copy(self):
        from scripting.legacy.wysiwyg import get_centered_image_metrics

        top = self.top if self.top else 10
        left = self.left if self.left else 10
        width = 100
        height = 100

        image_id = "4d6060c5-5acd-bd35-8f4c-0888ae0306f0"
        image_x = image_y = 0
        image_width = image_height = 50

        image_x, image_y, image_width, image_height = get_centered_image_metrics(
            image_width, image_height, width, height
        )

        designcolorvalue = "#" + self.designcolor if self.designcolor != "" else "none"

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                    top="{top}" left="{left}" width="{width}" height="{height}"
                    backgroundcolor="#EEEEEE" contents="static">
                    <svg>
                        <rect x="0" y="0" width="{width}" height="{height}" fill="{designcolorvalue}"/>
                        <image href="#Res({image_id})" x="{image_x}" y="{image_y}" width="{image_width}" height="{image_height}" />
                    </svg>
                </container>
            """.format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            designcolorvalue=designcolorvalue,
            top=top,
            left=left,
            width=width,
            height=height,
            image_id=image_id,
            image_width=image_width,
            image_height=image_height,
            image_x=image_x,
            image_y=image_y,
            name=self.name,
        )
        return result

    def wysiwyg(self, contents=""):
        self.check_cache()

        designcolorvalue = "#" + self.designcolor if self.designcolor != "" else "none"

        if self.source_object:
            object = application.objects.search(self.source_object)

            if object:
                height = height1 = height2 = ""

                if "ide_top" in object.attributes and object.attributes["ide_top"]:
                    top = self.top if self.top else object.attributes["ide_top"]

                    if "ide_left" in object.attributes:
                        left = self.left if self.left else object.attributes["ide_left"]

                    if object.attributes.get("ide_width"):
                        width = object.attributes["ide_width"]

                    if "ide_height" in object.attributes:
                        height = object.attributes["ide_height"]
                        height1 = """height="%s" """ % height
                        height2 = """height="%s" """ % str(int(height) + 2)

                else:
                    top = (
                        self.top
                        if self.top
                        else re.sub(r"\D", "", object.attributes["top"])
                    )
                    left = (
                        self.left
                        if self.left
                        else re.sub(r"\D", "", object.attributes["left"])
                    )

                    width = re.sub(r"\D", "", object.attributes["width"])

                    if "height" in object.attributes:
                        height = re.sub(r"\D", "", object.attributes["height"])
                        height1 = """height="%s" """ % height
                        height2 = """height="%s" """ % str(int(height) + 2)

                zindex = self.zindex

                contents_str = contents

                container_match = re.search(
                    r"<container(.*?)</container>", contents_str, re.DOTALL
                )
                if container_match:
                    container_str = container_match.group(0)

                    new_container_str = re.sub(
                        r'top="(.*?)"', 'top="0"', container_str, count=1
                    )
                    new_container_str = re.sub(
                        r'left="(.*?)"', 'left="0"', new_container_str, count=1
                    )
                    new_contents_str = re.sub(
                        re.escape(container_str),
                        new_container_str,
                        contents_str,
                        count=1,
                    )

                    contents = new_contents_str

                # if "zindex" in object.get_attributes():
                if "zindex" in object.attributes:
                    # zindex = object.get_attributes()["zindex"].value
                    zindex = object.attributes["zindex"]

                result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}"
                            top="{top}" left="{left}" width="{width2}" {height2} contents="static">
                            <svg>
                                <rect x="0" y="0" width="{width2}" {height2} fill="{designcolorvalue}"/>
                            </svg>
                            <container top="1" left="1" width="{width}" {height1} contents="static">
                                {contents}
                            </container>
                        </container>
                    """.format(
                    id=self.id,
                    vis=self.visible,
                    zind=zindex,
                    designcolorvalue=designcolorvalue,
                    width2=str(int(width) + 2),
                    height2=height2,
                    top=top,
                    left=left,
                    width=width,
                    height1=height1,
                    contents=contents,
                    name=self.name,
                )
            else:
                result = self.empty_copy()
        else:
            result = self.empty_copy()

        return VDOM_object.wysiwyg(self, contents=result)