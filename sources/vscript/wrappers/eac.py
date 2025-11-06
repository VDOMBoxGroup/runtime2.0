from importlib import import_module
from .. import errors
from ..subtypes import generic, string
from .util import AutoCast, v_PropertySimple, v_PropertyReadOnly

EACObject = import_module('scripting.packages').EACObject


class v_eac(generic):

    def __init__(self, mail_obj=None):
        generic.__init__(self)
        self._eac_obj = EACObject() if \
                    (mail_obj is None or not mail_obj.eac_body) else \
                    EACObject.from_data(mail_obj.eac_token, mail_obj.eac_body)

    @AutoCast
    @v_PropertySimple
    def v_dynamic(self, value, retVal):
        if not retVal:
            self._eac_obj.dynamic = bool(value)
        else:
            return self._eac_obj.dynamic

    @AutoCast
    @v_PropertySimple
    def v_auth(self, value, retVal):
        if not retVal:
            if value in ['internal', 'external']:
                self._eac_obj.auth = value
            else:
                raise errors.illegal_assigment()
        else:
            return self._eac_obj.auth

    @AutoCast
    @v_PropertySimple
    def v_session_token(self, value, retVal):
        if not retVal:
            self._eac_obj.session_token = value
        else:
            return self._eac_obj.session_token

    @AutoCast
    @v_PropertySimple
    def v_login_container(self, value, retVal):
        if not retVal:
            self._eac_obj.login_container = value
        else:
            return self._eac_obj.login_container

    @AutoCast
    @v_PropertySimple
    def v_login_method(self, value, retVal):
        if not retVal:
            self._eac_obj.login_method = value
        else:
            return self._eac_obj.login_method

    @AutoCast
    @v_PropertySimple
    def v_get_container(self, value, retVal):
        if not retVal:
            self._eac_obj.get_container = value
        else:
            return self._eac_obj.get_container

    @AutoCast
    @v_PropertySimple
    def v_get_method(self, value, retVal):
        if not retVal:
            self._eac_obj.get_method = value
        else:
            return self._eac_obj.get_method

    @AutoCast
    @v_PropertySimple
    def v_get_data(self, value, retVal):
        if not retVal:
            self._eac_obj.get_data = value
        else:
            return self._eac_obj.get_data

    @AutoCast
    @v_PropertySimple
    def v_post_container(self, value, retVal):
        if not retVal:
            self._eac_obj.post_container = value
        else:
            return self._eac_obj.post_container

    @AutoCast
    @v_PropertySimple
    def v_post_method(self, value, retVal):
        if not retVal:
            self._eac_obj.post_method = value
        else:
            return self._eac_obj.post_method

    @AutoCast
    @v_PropertySimple
    def v_post_data(self, value, retVal):
        if not retVal:
            self._eac_obj.post_data = value
        else:
            return self._eac_obj.post_data

    @AutoCast
    @v_PropertySimple
    def v_api_server(self, value, retVal):
        if not retVal:
            self._eac_obj.api_server = value
        else:
            return self._eac_obj.api_server

    @AutoCast
    @v_PropertySimple
    def v_app_id(self, value, retVal):
        if not retVal:
            self._eac_obj.app_id = value
        else:
            return self._eac_obj.app_id

    @AutoCast
    @v_PropertySimple
    def v_events_data(self, value, retVal):
        if not retVal:
            self._eac_obj.set_events(value)
        else:
            return self._eac_obj.events_data

    @AutoCast
    def v_set_events(self, value):
        self._eac_obj.set_events(value)

    @AutoCast
    @v_PropertySimple
    def v_vdomxml_data(self, value, retVal):
        if not retVal:
            self._eac_obj.vdomxml_data = value
        else:
            return self._eac_obj.vdomxml_data

    @AutoCast
    @v_PropertySimple
    def v_eac_app_name(self, value, retVal):
        if not retVal:
            self._eac_obj.eac_app_name = value
        else:
            return self._eac_obj.eac_app_name

    @AutoCast
    @v_PropertySimple
    def v_eac_token(self, value, retVal):
        if not retVal:
            self._eac_obj.eac_token = value
        else:
            return self._eac_obj.eac_token

    @AutoCast
    @v_PropertySimple
    def v_eac_method(self, value, retVal):
        if not retVal:
            self._eac_obj.eac_method = value
        else:
            return self._eac_obj.eac_method

    @AutoCast
    @v_PropertySimple
    def v_item_plugin(self, value, retVal):
        if not retVal:
            self._eac_obj.item_plugin = value
        else:
            return self._eac_obj.item_plugin

    @AutoCast
    @v_PropertySimple
    def v_item_vdomxml(self, value, retVal):
        if not retVal:
            self._eac_obj.item_vdomxml = value
        else:
            return self._eac_obj.item_vdomxml

    @AutoCast
    @v_PropertySimple
    def v_layout(self, value, retVal):
        if not retVal:
            self._eac_obj.layout = value
        else:
            return self._eac_obj.layout

    @AutoCast
    @v_PropertySimple
    def v_widgets(self, value, retVal):
        if not retVal:
            self._eac_obj.widgets = value
        else:
            return self._eac_obj.widgets

    @AutoCast
    def v_add_tag(self, name, color):
        self._eac_obj.tags[name] = color

    @AutoCast
    def v_remove_tag(self, name):
        self._eac_obj.tags.pop(name, None)

    @AutoCast
    @v_PropertyReadOnly
    def v_tags(self):
        return list(self._eac_obj.tags.keys())

    @AutoCast
    def v_get_wholexml(self):
        return self._eac_obj.get_wholexml()

    @AutoCast
    def v_get_eacviewer_url(self, host, email):
        return self._eac_obj.get_eacviewer_url(host, email)
