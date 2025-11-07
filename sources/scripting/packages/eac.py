"""
"""
from __future__ import absolute_import



from builtins import map

import json
from hashlib import md5
import urllib.parse
import urllib.request, urllib.parse, urllib.error
import email
import email.utils
import base64
from . import jlayout

from xml.dom.minidom import parseString
from xml.dom import getDOMImplementation



class FakeLogger(object):
    def debug(self, *args):
        args = ' '.join(map(repr,args))
        debug('[REMOTE_API CALL] '+args)


logger = FakeLogger()


def getText(nodelist):
    rc = []
    for node in nodelist:
        if isData(node):
            rc.append(node.data)
    return ''.join(rc)


def isData(node):
    return node.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE)


def append_cdata(doc, parent, data):
    start = 0
    while True:
        i = data.find("]]>", start)
        if i < 0: break
        parent.appendChild(doc.createCDATASection(data[start:i+2]))
        start = i + 2
    parent.appendChild(doc.createCDATASection(data[start:]))


def try_number(s):
    try:
        return int(s)
    except ValueError:
        pass

    try:
        return float(s)
    except ValueError:
        pass

    return s


class EACContent(object):

    class EACParseException(Exception):
        pass

    class CantParseRawWholeXMLError(EACParseException):
        pass

    class InvalidWholeXMLError(EACParseException):
        pass

    class InvalidAPIMethodPattern(EACParseException):
        pass

    class InvalidEventsDefinition(EACParseException):
        pass


    def __init__(self, wholexml):
        self.wholedata = self.parse_wholexml(wholexml)

    def _parse_api_section(self, api):
        """
        """
        result = dict(list(api.attributes.items()))
        result['methods'] = {}

        for child in api.childNodes:
            if isData(child):
                continue

            name = child.tagName.lower()
            result['methods'][name] = dict(list(child.attributes.items()))
            result['methods'][name]['pattern'] = ""

            pattern_el = child.getElementsByTagName("PATTERN")
            if not pattern_el:
                continue

            pattern = getText(pattern_el[0].childNodes).strip()
            if pattern:
                try:
                    pattern = json.loads(pattern)
                except:
                    if pattern == "{}":
                        pattern = {}
                    else:
                        raise self.InvalidAPIMethodPattern

            result['methods'][name]['pattern'] = pattern

        return result

    def _parse_item(self, item):
        result = {
            'plugin': '',
            'vdom': ''
        }
        vdomxml_el = item.getElementsByTagName("VDOMXML")
        if vdomxml_el:
            result['vdom'] = getText(vdomxml_el[0].childNodes)
        plugin_el = item.getElementsByTagName("PLUGIN")
        if plugin_el:
            result['plugin'] = plugin_el[0].attributes.get("id", "")
        return result

    def _parse_tags(self, tags):
        result = []
        for child in tags.childNodes:
            if isData(child):
                continue
            if child.tagName.lower() == "tag":
                result.append(dict(list(child.attributes.items())))
        return result

    def _parse_metadata_section(self, metadata):
        result = {
            'tags': '',
            'item': ''
        }
        tags_el = metadata.getElementsByTagName("TAGS")
        if tags_el:
            result['tags'] = self._parse_tags(tags_el[0])
        item_el = metadata.getElementsByTagName("ITEM")
        if item_el:
            result['item'] = self._parse_item(item_el[0])
        return result

    def _parse_layout_section(self, layout):
        result = {}
        for k,v in list(layout.attributes.items()):
            result[k] = try_number(v)

        if result['type'] == 'border':
            result['items'] = dict((k, None) for k in ['north', 'west', 'center', 'east', 'south'])
        else:
            result['items'] = []

        for child in layout.childNodes:
            if isData(child): continue

            widget_el = child.getElementsByTagName('WIDGET')
            widget = dict(list(widget_el[0].attributes.items())) if widget_el else None

            pane_config = {}
            for k,v in list(child.attributes.items()):
                pane_config[k] = try_number(v)

            pane_config['widget'] = widget

            if '-' in child.tagName:
                key = child.tagName.split('-', 1)[1].lower()
                result['items'][key] = pane_config
            else:
                result['items'].append(pane_config)

        return result

    def _parse_widgets_section(self, widgets_el):
        payload = getText(widgets_el.childNodes)

        try:
            return json.loads(base64.decodestring(payload))
        except:
            pass

        try:
            return json.loads(payload)
        except:
            pass

        return {}


    def parse_wholexml(self, wholexml):
        try:
            dom = parseString(wholexml)
        except Exception:
            raise
            raise self.CantParseRawWholeXMLError

        result_whole = {
            'global': '',
            'api': '',
            'events': '',
            'vdom': '',
            'metadata': {},
        }

        whole_el = dom.getElementsByTagName("WHOLEXML")

        if whole_el and whole_el[0].tagName.lower() != "wholexml":
            raise self.InvalidWholeXMLError

        whole_el = whole_el[0]
        result_whole['global'] = dict(list(whole_el.attributes.items()))

        api_el = whole_el.getElementsByTagName("API")
        if api_el:
            result_whole['api'] = self._parse_api_section(api_el[0])

        events_el = whole_el.getElementsByTagName("EVENTS")
        if events_el:
            result_whole['events'] = getText(events_el[0].childNodes)

        vdomxml_el = whole_el.getElementsByTagName("VDOMXML")
        if vdomxml_el:
            result_whole['vdom'] = getText(vdomxml_el[0].childNodes)

        metadata_el = whole_el.getElementsByTagName("METADATA")
        if metadata_el:
            result_whole['metadata'] = self._parse_metadata_section(metadata_el[0])

        layout_el = whole_el.getElementsByTagName("LAYOUT")
        if layout_el:
            result_whole['layout_xml'] = layout_el[0].toprettyxml()

        widgets_el = whole_el.getElementsByTagName("WIDGETS")
        if widgets_el:
            result_whole['widgets'] = self._parse_widgets_section(widgets_el[0])

        # update "vdom" and "events" values in result by compilation from layout / widgets
        if layout_el and widgets_el:
            layout_config = self._parse_layout_section(layout_el[0])
            widgets = result_whole['widgets']

            layout_data = jlayout.build_wholexml_data(layout_config, widgets)
            result_whole.update(layout_data)

        return result_whole

    def is_static(self):
        return self.wholedata['global']['Content'].lower() == 'static'

    def is_external(self):
        return self.wholedata['global']['Auth'].lower() == 'external'

    def is_internal(self):
        return self.wholedata['global']['Auth'].lower() == 'internal'


class EACObject(object):

    def __init__(self):
        # global
        self.dynamic = True
        self.auth = 'internal'
        self.session_token = ''
        # api
        self.login_container = ''
        self.login_method = ''
        self.get_container = ''
        self.get_method = ''
        self.get_data = ''
        self.post_container = ''
        self.post_method = ''
        self.post_data = ''
        self.api_server = ''
        self.app_id = ''
        # events
        self.events_data = ''
        # vdomxml
        self.vdomxml_data = ''
        # metadata
        self.tags = {}  # name : color
        self.item_plugin = ''
        self.item_vdomxml = ''
        # general
        self.eac_app_name = ''
        self.eac_token = ''
        self.eac_method = ''
        # layout / widgets
        self.layout = ''
        self.widgets = ''


    @classmethod
    def from_data(cls, eac_token, payload):
        eac = cls()
        whole = EACContent(payload.encode('utf8')).wholedata
        # global
        glob = whole['global']
        eac.dynamic = (glob.get('Content', '').lower() == 'dynamic')
        eac.auth = glob.get('Auth', 'internal')
        eac.session_token = glob.get('SessionToken', '')
        # api
        api = whole['api']
        login = api['methods'].get('login', None)
        get = api['methods'].get('get', None)
        post = api['methods'].get('post', None)
        eac.login_container = login['container'] if login else ''
        eac.login_method = login['action'] if login else ''
        eac.get_container = get['container'] if get else ''
        eac.get_method = get['action'] if get else ''
        eac.get_data = get.get('pattern', '') if get else ''
        eac.post_container = post['container'] if post else ''
        eac.post_method = post['action'] if post else ''
        eac.post_data = post.get('pattern', '') if post else ''
        eac.api_server = api.get('server', '')
        eac.app_id = api.get('appID', '')
        # events
        eac.events_data = whole['events']
        # vdomxml
        eac.vdomxml_data = whole['vdom']
        # metadata
        tags = whole['metadata'].get('tags', [])
        item = whole['metadata'].get('item', {})
        eac.tags = {}  # name : color
        for t in tags:
            if t.get('name', None) and t.get('color', None):
                eac.tags[t['name']] = t['color']
        eac.item_plugin = item.get('plugin', '') if item else ''
        eac.item_vdomxml = item.get('vdom', '') if item else ''
        # general
        eac.eac_app_name = ''
        eac.eac_token = eac_token
        eac.eac_method = ''

        # layout / widgets
        eac.layout = whole.get('layout_xml', '')
        eac.widgets = whole.get('widgets', {})

        return eac

    def set_events(self, data):
        """data is dictionary or string (JSON)"""
        self.events_data = data

    def get_eacviewer_url(self, host, email):
        param = {
            'eac_token': self.eac_token,
            'session_token': self.session_token,
            'login_container': self.login_container,
            'login_action': self.login_method,
            'get_container': self.get_container,
            'get_action': self.get_method,
            'post_container': self.post_container,
            'post_action': self.post_method,
            'app_id': self.app_id,
            'server': self.api_server,
            'email': email,
            'pattern': self.get_data if isinstance(self.get_data, bytes) \
                        else json.dumps(self.get_data),
            'pattern_post': self.post_data if isinstance(self.post_data, bytes) \
                        else json.dumps(self.post_data),
            'vdomxml': self.vdomxml_data.encode('utf8') if isinstance(self.vdomxml_data, str) else self.vdomxml_data,
            'events': self.events_data,
            'static': '0' if self.dynamic else '1',
            'layout': self.layout,
            'widgets': self.widgets
        }

        for k in list(param.keys()):
            if not param[k]:
                param.pop(k)

        param = urllib.parse.urlencode(param)

        protocol = 'https'
        if '://' in host:
            protocol, host = host.split('://', 1)

        return urllib.parse.urlunparse((protocol, host, '/eacviewer', '', param, ''))

    def get_wholexml(self):
        dom_impl = getDOMImplementation()
        doc = dom_impl.createDocument(None, 'WHOLEXML', None)
        root = doc.documentElement
        # root attributes
        root.setAttribute('Content', 'dynamic' if self.dynamic else 'static')
        root.setAttribute('SessionToken', self.session_token)
        root.setAttribute('Auth', self.auth)
        # api
        api = doc.createElement('API')
        api.setAttribute('server', self.api_server)
        api.setAttribute('appID', self.app_id)
        root.appendChild(api)
        # login
        login = doc.createElement('LOGIN')
        login.setAttribute('container', self.login_container)
        login.setAttribute('action', self.login_method)
        api.appendChild(login)
        # get
        get = doc.createElement('GET')
        get.setAttribute('container', self.get_container)
        get.setAttribute('action', self.get_method)
        pattern = doc.createElement('PATTERN')
        get.appendChild(pattern)
        api.appendChild(get)
        if self.get_data:
            self.__append_cdata(doc, pattern, self.get_data)
        # post
        post = doc.createElement('POST')
        post.setAttribute('container', self.post_container)
        post.setAttribute('action', self.post_method)
        pattern = doc.createElement('PATTERN')
        post.appendChild(pattern)
        api.appendChild(post)
        if self.post_data:
            self.__append_cdata(doc, pattern, self.post_data)
        # events
        events = doc.createElement('EVENTS')
        root.appendChild(events)
        if self.events_data:
            self.__append_cdata(doc, events, self.events_data)
        # vdomxml
        vdomxml = doc.createElement('VDOMXML')
        root.appendChild(vdomxml)
        if self.vdomxml_data:
            self.__append_cdata(doc, vdomxml, self.vdomxml_data)
        # metadata
        metadata = doc.createElement('METADATA')
        root.appendChild(metadata)
        tags = doc.createElement('TAGS')
        metadata.appendChild(tags)
        for tag_name in self.tags:
            tag = doc.createElement('TAG')
            tag.setAttribute('name', tag_name)
            tag.setAttribute('color', self.tags[tag_name])
            tags.appendChild(tag)
        if self.item_plugin or self.item_vdomxml:
            item = doc.createElement('ITEM')
            metadata.appendChild(item)
            root.appendChild(metadata)
            plugin = doc.createElement('PLUGIN')
            plugin.setAttribute('id', self.item_plugin)
            item.appendChild(plugin)
            vdomxml = doc.createElement('VDOMXML')
            item.appendChild(vdomxml)
            if self.item_vdomxml:
                self.__append_cdata(doc, vdomxml, self.item_vdomxml)

        if self.layout:
            layout = parseString(self.layout).documentElement
            root.appendChild(layout)

        if self.widgets:
            widgets = doc.createElement('WIDGETS')

            payload = self.widgets
            if not isinstance(payload, bytes):
                payload = json.dumps(payload, indent=2)

            self.__append_cdata(doc, widgets, base64.encodestring(payload))
            root.appendChild(widgets)

        return root.toprettyxml(encoding='utf8')


    def __append_cdata(self, doc, elem, data):
        append_cdata(doc, elem,
            json.dumps(data, indent=2) if isinstance(data, dict) else data)


    def send(self, toemail, subject, body):
        from mailing.message import Message, MailAttachment

        message = Message()
        message.subject = subject
        message.body = body

        message.headers['EAC-Token'] = self.eac_token
        message.headers['EAC-Method'] = self.eac_method

        message.append(MailAttachment(data = self.get_wholexml(), filename='EAC.xml', content_type='TEXT', content_subtype='WHOLEXML'))

        message.to_email = toemail
        message.from_email = 'services@appinmail.io'

        return send_message(message)


class mailbox_config(dict):
    def get_opt(self, name):
        return self.get(name, None)


def send_message(message):
    from mailing.email1 import VDOM_email_manager

    settings = mailbox_config({
        "SMTP-SERVER-ADDRESS": 'mailserv.appinmail.io',
        "SMTP-SERVER-PORT": 465,
        "SMTP-SERVER-USER": '',
        "SMTP-SERVER-PASSWORD": '',
        "SMTP-OVER-SSL": 'starttls',
        "SMTP-SERVER-SENDER": 'System',
    })

    email_manager = VDOM_email_manager(config=settings, daemon=False)
    email_manager.send(message)
    return email_manager.work()
