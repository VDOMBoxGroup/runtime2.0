from scripting.legacy.id import id2link1
import json


class VDOM_chat(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        display = "none" if self.visible == "0" else self.displaying
        zindex = "%s" % self.zindex if int(self.zindex) != 0 else ""
        position = "%s" % self.positioning if self.positioning and self.positioning != "static" else ""

        styles = {
            "display": display,
            "z-index": zindex,
            "position": position,
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        id = "o_" + (self.id).replace("-", "_")
        css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='chat' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = ""

        variables = self.variables.strip()

        try:
            variables_json = json.loads(variables)
            variables = json.dumps(variables_json).replace("\n", "")
        except ValueError:
            print("Invalid JSON format")

        if self.avatar or self.avatar_externalurl:
            link = id2link1(self.avatar) if self.avatar else self.avatar_externalurl
            html_ava = """<div class="avatar"><img class="avatar_image" src="{url}" /></div>""".format(url=link)
        else:
            html_ava = """<div class="avatar"></div>"""

        agent_name = """<div class="agent_name">{name}</div>""".format(name=self.agent_name) if self.agent_name else ""

        result = """{css}
<div id="{id}" class="{classname} vdom_chat chat_holder" style="{style}" {debug_info} lang="{lang}">
    <div class="top_panel">
        {html_avatar}{agent_name}
        <div id="typing_message" class="typing_btn hide"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
        </div>
            <div class="chat_wrapper">
                <div id="chatbox" class="chatbox"></div>
                <div id="iframe_container" class="iframe_container hide"></div>
                <div class="ask_buttons">
                    <button type="button" id="ok_btn" class="ask_button ok hide" onclick="clickOKButton()">OK</button>
                    <button type="button" id="cancel_btn" class="ask_button no hide" onclick="clickCancelButton()">Cancel</button>
                    <button type="button" id="yes_btn" class="ask_button yes hide" onclick="clickYesButton()">YES</button>
                    <button type="button" id="no_btn" class="ask_button no hide" onclick="clickNoButton()">NO</button>
                    <button type="button" id="restart_btn" class="ask_button restart hide" onclick="showRestartDialog()"></button>
                </div>
            </div>
            <div id="sending_message_holder" class="sending_message_holder">
                <form class="sending_message">
                    <input type="text" id="message" required="" autocomplete="off" placeholder="Type something...">
                    <button type="button" id="restart_btn" class="restart_btn" onclick="showRestartDialog()"></button>
                    <button type="button" class="send_btn" onclick="sendMessage()"></button>
                </form>
            </div>
            <div id="form_container" class="form_container hide"></div>
            <div id="dialog_restart_chat" class="popup_blackout hide">
                <div class="popup_restart_chat">
                    <h2>Restart chat</h2>
                    <p>Start conversation again?</p>
                    <div class="win_buttons">
                        <button id="restart_chat_btn" class="send_form_btn" onclick="clickRestartButton()">Yes</button>
                        <button class="cancel_form_btn" onclick="hideRestartChatDialog()">Close</button>
                    </div>
                </div>
            </div>
        </div>""".format(
            id=id, css=css, classname=self.classname, style=style, debug_info=debug_info, lang=self.lang, html_avatar=html_ava, agent_name=agent_name
        )

        result += """<script>
        let isFirstStart = true;
        window.chatId = '{id}';
    
        window.userUri = '{ws_server}';
        window.hostUrl = '{url}';
        window.scenarioGuid = '{guid}';
        window.userEmail = '{email}';
        window.userVariables = '{variables}';
        window.userProject = '{project_guid}';
        window.userAccessToken = '{user_access_token}';
        """.format(
            ws_server=self.ws_server,
            url=self.url,
            guid=self.guid,
            email=self.email,
            variables=variables,
            project_guid=self.project_guid,
            user_access_token=self.user_access_token,
            id=(self.id).replace("-", "_"),
        )

        if self.onstart == "0":
            result += "</script>"
        else:
            result += """
            start('{ws_server}', '{url}', '{guid}', '{email}', '{variables}', '{project_guid}');
        </script>""".format(ws_server=self.ws_server, url=self.url, guid=self.guid, email=self.email, variables=variables, project_guid=self.project_guid)

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]
        image_id = "26dd9d86-01d9-f89e-46a7-3b4aebe6da44"
        result = get_empty_wysiwyg_value(self, image_id)
        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
    o = object
    modifications = {}

    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, "").lower()

            if obj_value.isdigit() and attr_value.isdigit():
                modifications[attr] = attr_value + "px"
                modifications["ide_" + attr] = attr_value
            elif obj_value.endswith("px") and (attr_value.isdigit() or "px" in attr_value):
                modifications[attr] = attr_value.rstrip("px") + "px"
                modifications["ide_" + attr] = attr_value.rstrip("px")
            elif attr_value.isdigit() or "px" in attr_value:
                modifications[attr] = attr_value if "px" in attr_value else obj_value
                modifications["ide_" + attr] = attr_value.rstrip("px")
            else:
                modifications[attr] = attr_value

    attributes.update(modifications)

    ws_ex = "wss://pitts.co/ws"

    url_ex = "vails-pitts.prosuite.technology"

    guid_ex = "ED216D6F-0106-8836-2468-351DF4E36926"

    email_ex = "example@gmail.com"

    variables_ex = """\
%7B"%24lang"%3A"fr"%2C"%24userName"%3A"Alex%20Ivanov"%2C"%24userFirstName"%3A"Alex"%2C"%24userLastname"%3A"Ivanov"%2C"%24userMobile"%3A"999999"%2C"%24userEmail"%3A"a.ivanov.d%40gmail.com"%2C"%24now"%3A"10%2F01%2F2024%2015%3A30"%2C"%24agentName"%3A"Alex"%2C"%24mode"%3A"DEV"%7D"""

    var_json = """\
{
    "lang": "fr",
    "userName": "Alex I",
    "userFirstName": "Alex",
    "userLastname": "I",
    "userMobile": "9999999999",
    "userEmail": "a.i.d@gmail.com",
    "now": "31/01/2026",
    "agentName": "Alex",
    "mode": "DEV"
}"""

    data_map = {"ws_ex": ws_ex, "url_ex": url_ex, "guid_ex": guid_ex, "email_ex": email_ex, "variables_ex": variables_ex, "empty": ""}

    if "skin_websocket" in attributes:
        skin_websocket = attributes["skin_websocket"]
        if skin_websocket == "1":
            attributes.update(ws_server=ws_ex, url=url_ex, guid=guid_ex, email=email_ex, variables=variables_ex)
        elif skin_websocket == "2":
            attributes.update(ws_server=ws_ex, url=url_ex, guid=guid_ex, email=email_ex, variables=var_json)
        else:
            attributes.update(ws_server="", url="", guid="", email="", variables="")

    if any(key in attributes for key in ["ws_server", "url", "guid", "email", "variables"]):
        if any(attributes.get(key) not in data_map.values() for key in ["ws_server", "url", "guid", "email", "variables"]):
            attributes.update(skin_websocket="3")

    users = """\
#%(id)s {

}
"""

    skin_mapping = {"0": users, "1": ""}
    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")

    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")