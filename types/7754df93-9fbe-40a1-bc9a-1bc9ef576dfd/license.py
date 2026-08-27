class VDOM_license(VDOM_object):
    def render(self, contents=""):
        return self.licensetext or ""

    def wysiwyg(self, contents=""):
        result = '<container name="%s" id="%s" visible="%s" zindex="%s" hierarchy="%s" order="%s"><svg>%s</svg></container>' % (
            self.name,
            self.id,
            self.visible,
            self.zindex,
            self.hierarchy,
            self.order,
            contents,
        )
        return VDOM_object.wysiwyg(self, contents=result)

    def check_license(self, license_type=None):
        key = "-".join((application.id, license_type or self.licensekey))
        if key in system_options and system_options["key"]:
            return True
        else:
            return False


def check_license(license_type=0):
    key = "-".join((application.id, license_type))
    if key in system_options and system_options["key"]:
        return True
    else:
        return False