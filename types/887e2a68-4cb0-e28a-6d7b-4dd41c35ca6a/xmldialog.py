#!/usr/bin/env python

import re

from xml.dom.minidom import parseString

from utils.csrf import create_csrf_token, csrf_token_arg_name


# RegExp to remove <script> section in XML
RE_REMOVE_SCRIPT = re.compile(r"(?si)<(script)[^<>]*>.*?</\1>")

# Placeholder for default value
_DEFAULT = []

# Boolean values map
BOOL_MAP = {"0": False, "false": False, "1": True, "true": True}

# Sort by key lambda function
sort_by_key = lambda pair: pair[0]

# Sort by value lambda function
sort_by_val = lambda pair: pair[1]

# Sorting map
SORT_MAP = {"0": "default", "1": sort_by_key, "2": sort_by_val, "key": sort_by_key, "value": sort_by_val}

# Sorting order map
SORT_ORDER_MAP = {"0": "default", "1": "asc", "2": "desc", "asc": "asc", "desc": "desc"}

# Components CSS classes map
COMPONENTS_CSS_MAP = {
    "heading": "heading",
    "textbox": "textbox",
    "password": "password",
    "dropdown": "dropdown",
    "radiobutton": "radio",
    "checkbox": "checkbox",
    "textarea": "textarea",
    "hypertext": "hypertext",
    "button": "button",
    "container": "container",
    "livesearch": "livesearch",
    "richtextarea": "richtextarea",
    "fileupload": "fileupload",
    "codeeditor": "codeeditor",
}


# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    """ """
    xmldata = attributes.get("xmldata")
    # if "xmldata" in param:
    if xmldata:
        # obj = application.objects.search(object_id)

        # attr = (param["xmldata"]["value"]).replace('<![CDATA[', '<!--[CDATA[')
        # obj.attributes.xmldata = attr.replace(']'+']>', ']]-->')
        attributes["xmldata"] = xmldata.replace("<![CDATA[", "<!--[CDATA[").replace("]]>", "]]-->")

    # return ""


def parse_int(value, default):
    """
    Parse str to int
    """
    try:
        return int(value)

    except Exception:
        return default


def to_bool(value, default):
    """
    Convert string value to boolean
    """
    return BOOL_MAP.get(value, default)


def escape_quote(text):
    """
    Quote escape
    """
    return text.replace('"', "&quot;")


def get_elem_attr(elem, attr, default):
    """
    Return attribute of element
    """
    value = elem.getAttribute(attr.lower()).strip()
    if not value:
        return default

    if isinstance(default, bool):
        value = BOOL_MAP.get(value, default)

    return value


def get_elem_attrs(elem):
    """
    Return dictionary of element attributes
    """
    return {attr.lower(): value for attr, value in elem.attributes.items()}


def get_elem_props(elem):
    """
    Return dictionary of element Property section
    """
    props = {}

    properties = None
    for child in elem.childNodes:
        if child.nodeType == child.ELEMENT_NODE and child.localName.lower() == "properties":
            properties = child
            break

    if not properties:
        return props

    is_property_node = lambda node: node.nodeType == node.ELEMENT_NODE and node.localName == "Property" and node.childNodes

    for node in properties.childNodes:
        if not is_property_node(node):
            continue

        name = get_elem_attr(node, "name", "").lower()
        if name == "options":
            data = [child for child in node.childNodes if child.nodeType == child.ELEMENT_NODE]

        else:
            data = node.childNodes[0].nodeValue.strip()

        if data and name:
            props[name] = data

    return props


def is_disabled(elem):
    """
    Check is element disabled or not
    """
    return """disabled="disabled\"""" if get_elem_attr(elem, "disabled", False) else ""


def is_readonly(elem):
    """
    Check is element readonly or not
    """
    return """readonly="readonly\"""" if get_elem_attr(elem, "readonly", False) else ""


def is_multiple(elem):
    """
    Check is element readonly or not
    """
    return """multiple="multiple\"""" if get_elem_attr(elem, "multiple", False) else ""


def is_visible(elem):
    """
    Check element's visibility
    """
    return "" if get_elem_attr(elem, "visible", True) else """style="display: none\""""


def is_fullsize(elem):
    """
    Check is element fullsize or not
    """
    return "fullsize" if get_elem_attr(elem, "fullsize", False) else ""


def get_elem_options(options):
    """
    Get Options section of elemet
    """
    if not options:
        return []

    result = []
    for option in options:
        key = get_elem_attr(option, "id", "")
        value = option.childNodes[0].nodeValue.strip()

        if key and value:
            result.append((key, value))

    return result


def make_div_row(html, elem, label):
    """
    Wraps HTML data to DIV
    """
    return (
        """<div class="row {fullsize} {classes}" {visibility}>"""
        """<label class="title">{label}</label>"""
        """<div class="item {elem_type}">{html}</div>"""
        """<br style="clear: both" />"""
        """</div>"""
    ).format(
        fullsize=is_fullsize(elem),
        classes=get_elem_attr(elem, "class", ""),
        visibility=is_visible(elem),
        label=label,
        elem_type=COMPONENTS_CSS_MAP[elem.localName.lower()],
        html=html,
    )


def render_heading(elem):
    """
    Render Heading component

    Example:

    <Heading id='headingName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 level='1 | 2 | 3 | 4 | 5 | 6'>

        <Properties>
            <Property name='text'><!--[CDATA[Heading text]]--></Property>
        </Properties>
    </Heading>
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    level = parse_int(attrs.get("level", "3"), 3)
    if not (6 >= level >= 1):
        level = 3

    return """<h{level} class="{classes}" id="{attr_id}" {visibility}>{text}</h{level}>""".format(
        attr_id=escape_quote(attrs.get("id", "")),
        classes=attrs.get("class", ""),
        level=level,
        text=props.get("text", ""),
        visibility=is_visible(elem),
    )


def render_textbox(elem):
    """
    Render TextBox component

    Example:

    <TextBox id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 fullsize='1 | 0 | true | false'
                 disabled='1 | 0 | true | false'
                 readonly='1 | 0 | true | false'>

        <Properties>
            <Property name='label'><!--[CDATA[Label]]--></Property>
            <Property name='defaultValue'><!--[CDATA[Test]]--></Property>
        </Properties>
    </TextBox>
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    html = """<input type="text" name="{attr_id}" value="{value}" {disabled} {readonly} />""".format(
        attr_id=escape_quote(attrs.get("id", "")), value=escape_quote(props.get("defaultvalue", "")), disabled=is_disabled(elem), readonly=is_readonly(elem)
    )

    return make_div_row(html, elem, props.get("label", ""))


def render_password(elem):
    """
    Render Password component

    Example:

    <Password id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 fullsize='1 | 0 | true | false'
                 disabled='1 | 0 | true | false'
                 readonly='1 | 0 | true | false'>

        <Properties>
            <Property name='label'><!--[CDATA[Label]]--></Property>
            <Property name='defaultValue'><!--[CDATA[Test]]--></Property>
        </Properties>
    </Password>
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    html = """<input type="password" name="{attr_id}" value="{value}" {disabled} {readonly} />""".format(
        attr_id=escape_quote(attrs.get("id", "")), value=escape_quote(props.get("defaultvalue", "")), disabled=is_disabled(elem), readonly=is_readonly(elem)
    )

    return make_div_row(html, elem, props.get("label", ""))


def render_dropdown(elem):
    """
    Render DropDown component

    Example:

    <DropDown id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 fullsize='1 | 0 | true | false'
                 disabled='1 | 0 | true | false'
                 sort='0 | 1 | 2 | key | value'
                 order='0 | 1 | 2 | asc | desc'
                 multiple='1 | 0 | true | false'>

        <Properties>
            <Property name='label'><!--[CDATA[Test]]--></Property>
            <Property name='rows'><!--[CDATA[10]]--></Property>
            <Property name='selected'><!--[CDATA[key1,key3]]--></Property>
            <Property name='disabled'><!--[CDATA[key1,key2]]--></Property>
            <Property name='options'>
                <option id='key2'>val2</option>
                <option id='key1'>val1</option>
                <option id='key3'>val3</option>
            </Property>
        </Properties>
    </DropDown>
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    rows = parse_int(props.get("rows", "0"), 0)
    options = get_elem_options(props.get("options", []))
    sort_type = SORT_MAP.get(attrs.get("sort", "0"), "default")
    sort_order = SORT_ORDER_MAP.get(attrs.get("order", "0"), "default")

    if sort_type != "default":
        options = sorted(options, key=sort_type)

        if sort_order == "desc":
            options = reversed(options)

    selected_keys = [key.strip() for key in props.get("selected", "").split(",")]
    disabled_keys = [key.strip() for key in props.get("disabled", "").split(",")]

    multiple = is_multiple(elem)
    if not multiple and len(selected_keys) > 1:
        selected_keys = selected_keys[-1:]

    options_html = []
    for key, value in options:
        selected = """selected="selected\"""" if key in selected_keys and (key not in disabled_keys) else ""
        disabled = """disabled="disabled\"""" if key in disabled_keys else ""

        options_html.append(
            """<option value="{key}" {selected} {disabled}>{value}</option>""".format(key=escape_quote(key), value=value, selected=selected, disabled=disabled)
        )

    html = """<select name="{attr_id}" {size} {multiple} {disabled}>{options}</select>""".format(
        attr_id=escape_quote(attrs.get("id", "")),
        size="""size="{}\"""".format(rows) if rows else "",
        multiple=multiple,
        disabled=is_disabled(elem),
        options="".join(options_html),
    )

    return make_div_row(html, elem, props.get("label", ""))


def render_radiobutton(elem):
    """
    Render RadioButton component

    Example:

    <RadioButton id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 fullsize='1 | 0 | true | false'
                 disabled='1 | 0 | true | false'
                 readonly='1 | 0 | true | false'
                 sort='0 | 1 | 2 | key | value'
                 order='0 | 1 | 2 | asc | desc'
                 breakline='1 | 0 | true | false'>

        <Properties>
            <Property name='label'><!--[CDATA[Test]]--></Property>
            <Property name='selected'><!--[CDATA[key1]]--></Property>
            <Property name='options'>
                <option id='key2'>val2</option>
                <option id='key1'>val1</option>
                <option id='key3'>val3</option>
            </Property>
        </Properties>
    </RadioButton>
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    disabled = is_disabled(elem)
    selected_key = props.get("selected", "").strip()
    options = get_elem_options(props.get("options", []))
    sort_type = SORT_MAP.get(attrs.get("sort", "0"), "default")
    sort_order = SORT_ORDER_MAP.get(attrs.get("order", "0"), "default")
    breakline = "<br/>" if to_bool(attrs.get("breakline", "0"), False) else ""

    if sort_type != "default":
        options = sorted(options, key=sort_type)

        if sort_order == "desc":
            options = reversed(options)

    elem_id = escape_quote(attrs.get("id", ""))
    options_html = []
    for key, value in options:
        selected = """checked="checked\"""" if key == selected_key else ""

        options_html.append(
            """<label><input autocomplete="off" type="radio" name="{attr_id}" value="{key}" {selected} {disabled} />&nbsp;{label}</label>{breakline}""".format(
                attr_id=elem_id, selected=selected, disabled=disabled, label=value, key=escape_quote(key), breakline=breakline
            )
        )

    return make_div_row("".join(options_html), elem, props.get("label", ""))


def render_checkbox(elem):
    """
    Render CheckBox component

    Example:

    <CheckBox id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 fullsize='1 | 0 | true | false'
                 disabled='1 | 0 | true | false'
                 sort='0 | 1 | 2 | key | value'
                 order='0 | 1 | 2 | asc | desc'
                 breakline='1 | 0 | true | false'>

        <Properties>
            <Property name='label'><!--[CDATA[Test]]--></Property>
            <Property name='selected'><!--[CDATA[key1,key2]]--></Property>
            <Property name='disabled'><!--[CDATA[key1,key3]]--></Property>
            <Property name='options'>
                <option id='key2'>val2</option>
                <option id='key1'>val1</option>
                <option id='key3'>val3</option>
            </Property>
        </Properties>
    </CheckBox>
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    disabled = is_disabled(elem)
    options = get_elem_options(props.get("options", []))
    sort_type = SORT_MAP.get(attrs.get("sort", "0"), "default")
    sort_order = SORT_ORDER_MAP.get(attrs.get("order", "0"), "default")
    breakline = "<br/>" if to_bool(attrs.get("breakline", "0"), False) else ""

    if sort_type != "default":
        options = sorted(options, key=sort_type)

        if sort_order == "desc":
            options = reversed(options)

    selected_keys = [key.strip() for key in props.get("selected", "").split(",")]
    disabled_keys = [key.strip() for key in props.get("disabled", "").split(",")]

    options_html = []
    elem_id = escape_quote(attrs.get("id", ""))

    for key, value in options:
        selected = """checked="checked\"""" if key in selected_keys else ""
        inactive = """disabled="disabled\"""" if disabled or key in disabled_keys else ""

        options_html.append(
            """<label><input autocomplete="off" type="checkbox" name="{attr_id}[{key}]" {selected} {disabled} />&nbsp;{label}</label>{breakline}""".format(
                attr_id=elem_id, selected=selected, disabled=inactive, label=value, key=escape_quote(key), breakline=breakline
            )
        )

    return make_div_row("".join(options_html), elem, props.get("label", ""))


def render_textarea(elem):
    """
    Render TextArea component

    Example:

    <TextArea id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 fullsize='1 | 0 | true | false'
                 disabled='1 | 0 | true | false'
                 readonly='1 | 0 | true | false'>

        <Properties>
            <Property name='label'><!--[CDATA[Label]]--></Property>
            <Property name='defaultValue'><!--[CDATA[Test]]--></Property>
            <Property name='width'><!--[CDATA[400]]--></Property>
            <Property name='height'><!--[CDATA[500]]--></Property>
        </Properties>
    </TextArea>
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    width = parse_int(props.get("width", "0"), 0)
    height = parse_int(props.get("height", "0"), 0)

    style = """style="{width}{height}\"""".format(width="width: {}px;".format(width) if width else "", height="height: {}px;".format(height) if height else "")

    html = """<textarea name="{attr_id}" {disabled} {readonly} {style}>{value}</textarea>""".format(
        attr_id=escape_quote(attrs.get("id", "")), disabled=is_disabled(elem), readonly=is_readonly(elem), style=style, value=props.get("defaultvalue", "")
    )

    return make_div_row(html, elem, props.get("label", ""))


def render_hypertext(elem):
    """
    Render Hypertext component

    Example:

    <Hypertext id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 fullsize='1 | 0 | true | false'>

        <Properties>
            <Property name='value'><!--[CDATA[<span>blabla</span>]]--></Property>
        </Properties>
    </Hypertext>
    """
    props = get_elem_props(elem)
    return make_div_row(props.get("value", ""), elem, props.get("label", ""))


def render_button(elem):
    """
    Render Button component

    Example:

    <Button id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 disabled='1 | 0 | true | false'>

        <Properties>
            <Property name='label'><!--[CDATA[Label]]--></Property>
            <Property name='buttonAlign'><!--[CDATA[center | justify | left | right | start | end]]--></Property>
            <Property name='buttonImage'><!--[CDATA[/path/to/image.png]]--></Property>
        </Properties>
    </Button>
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    align = props.get("buttonalign", "").strip().replace("'", "&acute;")
    image = props.get("buttonimage", "").strip().replace("'", "&acute;")
    label = props.get("label", "").replace("'", "&acute;")

    if image:
        button = """<input type="image" alt="{label}" title="{label}" src="{img}" {disabled} />""".format(label=label, img=image, disabled=is_disabled(elem))

    else:
        button = """<input type="submit" value="{label}" {disabled} />""".format(label=label, disabled=is_disabled(elem))

    return (
        """<div class="row" {visible}>"""
        """<div id='{attr_id}' class="submit {classes}" style="text-align: {align}">"""
        """{button}"""
        """</div>"""
        """</div>"""
    ).format(visible=is_visible(elem), align=align, button=button, classes=attrs.get("class", ""), attr_id=escape_quote(attrs.get("id", "")))


def render_default_button():
    """
    Render default form button
    """
    return """<div class="submit"><input type="submit" /></div>"""


def render_container(elem):
    """
    Render Container component

    Example:

    <Container id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'>
        <Properties>
            <Property name='width'><!--[CDATA[400px | 100%]]--></Property>
            <Property name='height'><!--[CDATA[500px | 100%]]--></Property>
        </Properties>
        <Components>
            <Button>...
            <DropDown>...
            <Container>...
        </Components>
    </Container>
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    width = props.get("width", "")
    height = props.get("height", "")

    style = """style="{width}{height}{visibility}\"""".format(
        width="width: {};".format(width) if width else "",
        height="height: {};".format(height) if height else "",
        visibility="display: none;" if is_visible(elem) else "",
    )

    components = elem.getElementsByTagName("Components")
    components = render_components(components[0], elem.form_id) if components else ""

    return (
        """<div id="{attr_id}" class="row fullsize {classes}" {style}>"""
        """<div class="item">"""
        """{components}"""
        """</div>"""
        """</div>"""
    ).format(attr_id=escape_quote(attrs.get("id", "")), classes=attrs.get("classes", ""), style=style, components=components)


def render_livesearch(elem):
    """
    Render LiveSearch component

    Example:

    <LiveSearch id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 fullsize='1 | 0 | true | false'
                 disabled='1 | 0 | true | false'
                 readonly='1 | 0 | true | false'>
        <Properties>
            <Property name='label'><!--[CDATA[LiveSearch]]--></Property>
            <Property name='sourceURI'><!--[CDATA[/blabla/livesearch]]--></Property>
            <Property name='sourceEvent'><!--[CDATA[something or empty]]--></Property>
            <Property name='sourceData'><!--[CDATA[["key1", "key2", "key3", "key4"] | [{label: '', value: ''}, {label: '', value: ''}]]]--></Property>
        </Properties>
    </LiveSearch>

    If sourceEvent presented: callback 'liveSearch' will be executed, so do not forget register it.
    Params are:
        textarea - textarea object
        term - search query

    You need return data in format presented in sourceData
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    html = """<div id="xml-dialog-lvs-{attr_id}-data">{sourceData}</div><input id="xml-dialog-lvs-{attr_id}" name="{attr_id}" {disabled} {readonly} sourceuri="{sourceURI}" sourceevent="{sourceEvent}" value="{value}" />""".format(
        attr_id=escape_quote(attrs.get("id", "")),
        value=escape_quote(props.get("defaultvalue", "")),
        disabled=is_disabled(elem),
        readonly=is_readonly(elem),
        sourceURI=escape_quote(props.get("sourceuri", "")),
        sourceEvent=escape_quote(props.get("sourceevent", "")),
        sourceData=props.get("sourcedata", "").replace("&", "&amp;").replace("<", "&lt;"),
    )

    return make_div_row(html, elem, props.get("label", ""))


def render_richtextarea(elem):
    """
    Render RichTextAreat component

    Example:

    <RichTextArea id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 disabled='1 | 0 | true | false'
                 readonly='1 | 0 | true | false'>
        <Properties>
            <Property name='label'><!--[CDATA[Rich Text Area]]--></Property>
            <Property name='defaultValue'><!--[CDATA[default value]]--></Property>
            <Property name='height'><!--[CDATA[500]]--></Property>
        </Properties>
    </RichTextArea>
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    html = """<textarea id="xml-dialog-rte-{attr_id}" name="{attr_id}" {disabled} {readonly} eheight="{height}">{value}</textarea>""".format(
        attr_id=escape_quote(attrs.get("id", "")),
        value=escape_quote(props.get("defaultvalue", "")),
        disabled=is_disabled(elem),
        readonly=is_readonly(elem),
        height=props.get("height", ""),
    )

    return make_div_row(html, elem, props.get("label", ""))


def render_fileupload(elem):
    """
    Render FileUpload component

    Example:

    <FileUpload id='uploadName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 fullsize='1 | 0 | true | false'>

        <Properties>
            <Property name='label'><!--[CDATA[Label]]--></Property>
        </Properties>
    </FileUpload>
    """
    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    code = """<script type="text/javascript">
        var max_fileupload_size = 15 * 1024 * 1024;
        var fileupload_next = 1;
        var fileupload_progress = 0;
        var update_selected_files = function() {{
            var val = "";
            $(".{attr_id}-guid").each(function(i) {{
                if (val != "") val = val + ",";
                val = val + $(this)[0].value;
            }});
            $("#{attr_id}")[0].value = val;
        }}
        var add_uploaded_file = function(filename, guid) {{
                var newelem = '<input type="text" id="{attr_id}_' + fileupload_next + '_name" name="{attr_id}_' + fileupload_next + '_name" readonly="readonly" disabled="disabled" />';
                var newelement = $(newelem);
                newelement[0].value = filename;
                var removebtn = '<button id="{attr_id}_remove_' + fileupload_next + '" class="{attr_id}-remove-me">x</button></div><div id="{attr_id}_div">';
                var removebutton = $(removebtn);
                var guidelem = '<input type="hidden" id="{attr_id}_' + fileupload_next + '" name="{attr_id}_' + fileupload_next + '" class="{attr_id}-guid" disabled="disabled" />';
                var guidelement = $(guidelem);
                guidelement[0].value = guid;
                $("#{attr_id}_input").before(newelement);
                $(newelement).after(guidelement);
                $(guidelement).after(removebutton);
                fileupload_next = fileupload_next + 1;
                $(".{attr_id}-remove-me").click(function(e) {{
                    e.preventDefault();
                    var fieldnum = this.id.substring("{attr_id}".length + 8);
                    $(this).remove();
                    $("#{attr_id}_" + fieldnum + "_name").remove();
                    $("#{attr_id}_" + fieldnum).remove();
                    update_selected_files();
                }});
                update_selected_files();
        }}
        var fileupload_started = function() {{
            if (fileupload_progress == 0) $('input[type="submit"]', $("#{form_id}")).attr("disabled", true);
            fileupload_progress = fileupload_progress + 1;
        }}
        var fileupload_ended = function() {{
            if (fileupload_progress > 0) fileupload_progress = fileupload_progress - 1;
            if (fileupload_progress == 0) {{
                $("#{attr_id}_progress")[0].innerHTML = "";
                $('input[type="submit"]', $("#{form_id}")).attr("disabled", false);
            }}
        }}
        var init_file_upload = function() {{
            $("#{form_id}").fileUploadUI({{
                url: "/upload.py",
                dataType: "json",
                dropZone: $("#{form_id}"),
                autoUpload: true,
                replaceFileInput: false,
                onComplete: function (event, files, index, xhr, handler) {{
                    var resp = xhr.response.trim();
                    if (xhr.status == 200 && resp.length == 36) add_uploaded_file(files[0].name, resp);
                    else {{
                        if (xhr.status != 200) alert("Upload error: " + xhr.statusText);
                        else alert("Upload error");
                    }}
                    fileupload_ended();
                }},
                onSend: function (event, files, index, xhr, handler) {{
                    if (!xhr.upload && handler.progressbar) handler.progressbar.progressbar("value", 100);
                    if (event.target.type == "file") event.target.value = "";
                    if (files[0].size <= max_fileupload_size) fileupload_started();
                    else alert("File is too big");
                }},
                onError: function (event, files, index, xhr, handler) {{
                }},
                onProgressAll: function (event, list) {{
                    if (fileupload_progress > 0) {{
                        var percent = parseInt(event.loaded / event.total * 100, 10);
                        $("#{attr_id}_progress")[0].innerHTML = "Uploading " + fileupload_progress + " file(s)... " + percent + "%";
                    }}
                }},
                onProgress: function (progressEvent, files, index, xhr, settings) {{
                    if (files[0].size > max_fileupload_size) xhr.abort();
                }},
            }});
        }}
        $(document).ready(function(){{
            init_file_upload();
        }});
    </script>""".format(attr_id=escape_quote(attrs.get("id", "")), form_id=escape_quote(elem.form_id))

    html = """<div id="{attr_id}_div"><input id="{attr_id}_input" name="{attr_id}_input" type="file"/><div id="{attr_id}_progress"></div><input id="{attr_id}" name="{attr_id}" type="hidden"/></div>""".format(
        attr_id=escape_quote(attrs.get("id", ""))
    )

    return make_div_row(html, elem, props.get("label", "")) + code


def render_codeeditor(elem):
    """
        Render CodeEditor component

        Example:

    <CodeEditor id='inputName'
                 class='css class'
                 visible= '1 | 0 | true | false'
                 disabled='1 | 0 | true | false'
                 readonly='1 | 0 | true | false'>
        <Properties>
            <Property name='label'><!--[CDATA[Code Editor Label]]--></Property>
            <Property name='value'><!--[CDATA[default value]]--></Property>
            <Property name='width'><!--[CDATA[360]]--></Property>
            <Property name='height'><!--[CDATA[130]]--></Property>
            <Property name='syntax'><!--[CDATA[python]]--></Property>
        </Properties>..
    </CodeEditor>
    """

    attrs = get_elem_attrs(elem)
    props = get_elem_props(elem)

    style = """overflow: visible; width: {width}px; height: {height}px; padding: 2px 5px 2px 5px; font: 14px tahoma""".format(
        width=props.get("width", ""), height=props.get("height", "")
    )
    style_area = """width:{width}px; height:{height}px""".format(width=props.get("width", ""), height=props.get("height", ""))

    html = """
<style type="text/css">#{id} .CodeMirror-scroll {{ height: {height}px; }}</style>
<div id="{id}" style="{style}">
    <textarea name="{name}" style="{style_area}">{value}</textarea>
</div>
<script type="text/javascript">$(document).bind('dialog.loaded', function(){{
    if (typeof window.{id}_codeeditor !== 'undefined') {{
        window.{id}_codeeditor.toTextArea();
        delete(window.{id}_codeeditor);
    }}
    window.{id}_codeeditor = CodeMirror.fromTextArea($('#{id}>textarea').get(0), {{
        mode: '{mode}',
        lineNumbers: true,
        styleActiveLine: true,
        onCursorActivity: function() {{ window.{id}_codeeditor.matchHighlight("CodeMirror-matchhighlight"); }}
    }})
    $('#{id}').parents('form:first').submit(function(){{
        window.{id}_codeeditor.save()
    }})
    window.{id}_codeeditor.refresh()
}});</script>
""".format(
        id="xml_dialog_ce_" + escape_quote(attrs.get("id", "")),
        name=escape_quote(attrs.get("id", "")),
        mode=props.get("syntax", ""),
        style=style,
        style_area=style_area,
        value=str(props.get("value", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"),
        # width=props.get("width", ""),
        height=props.get("height", ""),
    )
    return html


# return make_div_row(html, elem, props.get("label", ""))


COMPONENTS_MAP = {
    "heading": render_heading,
    "textbox": render_textbox,
    "password": render_password,
    "dropdown": render_dropdown,
    "radiobutton": render_radiobutton,
    "checkbox": render_checkbox,
    "textarea": render_textarea,
    "hypertext": render_hypertext,
    "button": render_button,
    "livesearch": render_livesearch,
    "container": render_container,
    "fileupload": render_fileupload,
    "richtextarea": render_richtextarea,
    "codeeditor": render_codeeditor,
}


def render_components(components, form_id):
    """
    Render XML components to HTML
    """
    result = []

    for elem in components.childNodes:
        if elem.nodeType != elem.ELEMENT_NODE:
            continue

        render = COMPONENTS_MAP.get(elem.localName.lower(), None)
        if render:
            elem.form_id = form_id
            result.append(render(elem))

    return "".join(result)


# try:
#     parent_class = VDOM_object

# except Exception as ex:
#     parent_class = object

#     VDOM_CONFIG_1 = {
#         "ENABLE-PAGE-DEBUG": "1",
#         "DEBUG": "1"
#     }


class VDOM_xmldialog(VDOM_object):
    """
    XML Dialog class
    """

    def exception_to_str(self, error, is_wysiwyg=False):
        """
        Exception to string
        """
        err_str = ""

        if is_wysiwyg or VDOM_CONFIG_1["ENABLE-PAGE-DEBUG"] == "1":
            err_str = """<p style="color:#ff0000;"><b>Error:</b> {0}</p>""".format(error)

        else:
            if VDOM_CONFIG_1["DEBUG"] == "1":
                err_str = """<!--<p>Error: {0}</p>-->""".format(error)

        return err_str

    def xml_to_html(self, is_wysiwyg=False):
        """
        Conver XML data to HTML
        """
        if not self.xmldata:
            return ""

        try:
            xml_data = self.xmldata.encode("utf8")

        except Exception as ex:
            raise
            return self.exception_to_str(ex, is_wysiwyg=is_wysiwyg)

        xml_data = xml_data.replace("<!--[CDATA[", "<![CDATA[").replace("]]-->", "]" + "]>")

        if is_wysiwyg:
            # if WYSIWYG render - remove <script></script> from XML
            xml_data = RE_REMOVE_SCRIPT.sub("", xml_data)

        try:
            dom = parseString(xml_data)

        except Exception as ex:
            raise
            return self.exception_to_str(ex, is_wysiwyg=is_wysiwyg)

        form_id = "xml_form_" + (self.id).replace("-", "_")

        components = dom.getElementsByTagName("Components")

        try:
            output = render_components(components[0], form_id) if components else ""

        except Exception as ex:
            raise
            return self.exception_to_str(ex, is_wysiwyg=is_wysiwyg)

        if not dom.getElementsByTagName("Button"):
            output += render_default_button()
        csrftoken = '<input type="hidden" name="%s" value="%s">' % (csrf_token_arg_name, create_csrf_token())
        return self.parse_dialog_title(
            dom
        ), """<form id="{}" action="" method="post" enctype="multipart/form-data" class="xml-dialog-form">{} {}</form>""".format(form_id, output, csrftoken)

    def parse_dialog_title(self, elem):
        """
        Parse title value from DOM
        """
        default_title = self.title

        vdomf = elem.getElementsByTagName("VDOMFormContainer")
        if not vdomf:
            return default_title

        props = get_elem_props(vdomf[0])
        return props["label"] if "label" in props else default_title

    def render(self, contents=""):
        """
        VDOM Object render
        """
        idn = (self.id).replace("-", "_")
        oid = "o_" + idn

        show = "false" if self.show == "0" else "true"
        modal = "false" if self.modal == "0" else "true"

        render_result = self.xml_to_html()
        if isinstance(render_result, (list, tuple)):
            title, html = render_result

        else:
            title, html = "", render_result

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='xmldialog' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = ""

        result = """
<div style='display:none' %(debug_info)s><div id='%(id)s'>%(data)s</div></div>
<script type='text/javascript'>$(function(){
    $.widget("ui.dialog", $.extend({}, $.ui.dialog.prototype, {
        _title: function(title) {
            if (!this.options.title) {
                title.html("&#160;");
            } else {
                title.html(this.options.title);
            }
        }
    }));

    dialog = $("#%(id)s")
    var dialogScripts = $("#%(id)s").find("script");
    dialogScripts.remove();
    $("#%(id)s").data('ev','1');
    $("#%(id)s:ui-dialog").dialog("destroy");
    $("#%(id)s").dialog({
        title: "%(title)s",
        width: %(width)s,
        height: %(height)s,
        modal: %(modal)s,
        draggable: !%(modal)s,
        resizable: false,
        autoOpen: %(show)s,
        open: function(e,u) {
            var dialog = $("#%(id)s");
            if (dialog.data('ev')=='1') execEventBinded('%(idn)s', "show", {});

            vdom_xd_create_richtextarea(dialog);
            vdom_xd_create_livesearch(dialog);

            $.datepicker.setDefaults($.datepicker.regional['fr']);
            $('#%(id)s input.date, #%(id)s .date input').datepicker('destroy').datepicker({
                dateFormat: 'dd/mm/yy', showButtonPanel: true
            }).blur();
        },
        close: function(e,u) {
            $('#ui-datepicker-div,#ColorDropdown_selector').fadeOut();
            if ($("#%(id)s").data('ev')=='1') execEventBinded('%(idn)s', "hide", {});
        }
    });
    
    $("#%(id)s form.xml-dialog-form").on('submit',function(e){
        function escapeXml(s) {
            return s.replace(/[<>&'"]/g, function (c) {
                switch (c) {
                    case '<': return '&lt;';
                    case '>': return '&gt;';
                    case '&': return '&amp;';
                    case "'": return '&apos;';
                    case '"': return '&quot;';
                }
            });
        }
        e.preventDefault;
        for (var i in window["xmlDialogTinyEditors"])
            window["xmlDialogTinyEditors"][i].post();

        var x=[], a=$(this).serializeArray();
        for (var k of a) if(typeof k.name !== 'undefined' && typeof k.value !== 'undefined') x[escapeXml(k.name)]=k.value;
        execEventBinded('%(idn)s', "submit", x);
        return false;
    });
    
    $(document).trigger('dialog.loaded')
    var dialogContainer = document.getElementById('%(id)s');
    dialogScripts.each(function() { dialogContainer.appendChild(this); });
});</script>""" % {
            "data": html,
            "id": oid,
            "idn": idn,
            "width": self.width,
            "height": self.height,
            "title": title.replace('"', "&quot;"),
            "show": show,
            "modal": modal,
            "debug_info": debug_info,
        }

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        """
        WYSIWYG render
        """
        dialog_width = int(self.width) if int(self.width) >= 150 else 150
        dialog_height = int(self.height) if int(self.height) >= 50 else 50

        render_result = self.xml_to_html(True)
        if isinstance(render_result, (list, tuple)):
            title, html = render_result

        else:
            title, html = "", render_result

        title = title.replace('"', "&quot;")

        result = """<container name="{name}" id="{id}" hierarchy="{hierarchy}" order="{order}" 
                            top="{top}" left="{left}" width="{width}" height="{height}" overflow="visible">
                    <svg>
                        <rect x="0" y="0" rx="7" ry="5" width="{width}" height="{height}" fill="#eeeeee"/>
                        <rect x="3" y="3" rx="7" ry="5" width="{rect_width}" height="30" fill="#333333"/>
                        <line x1="{line_x1}"  y1="14" x2="{line_x2}"   y2="22" style="stroke:#eeeeee; stroke-width:3;"/>
                        <line x1="{line_x1}"  y1="22" x2="{line_x2}"   y2="14" style="stroke:#eeeeee; stroke-width:3;"/>
                        <text x="13" y="22" width="{title_width}" fill="#eeeeee" font-size="14">{dlg_title}</text>
                    </svg>
                    
                    <htmltext top="35" left="10" width="{content_width}" height="{content_height}">
                        <div>{xmldata}</div>
                    </htmltext>
                </container>
            """.format(
            id=self.id,
            hierarchy=self.hierarchy,
            order=self.order,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            rect_width=dialog_width - 6,
            line_x1=dialog_width - 20,
            line_x2=dialog_width - 12,
            title_width=dialog_width - 25,
            content_height=dialog_height - 40,
            content_width=dialog_width - 20,
            xmldata=html,
            dlg_title=title,
            name=self.name,
        )

        return VDOM_object.wysiwyg(self, contents=result)


# if __name__ == "__main__":

#     xml_dialog = VDOM_xmldialog()
#     xml_dialog.title = "Default title"
#     xml_dialog.id = "9f1c05cd-fee2-6055-2ef4-16fae6375ed7"
#     xml_dialog.show = "1"
#     xml_dialog.modal = "1"
#     xml_dialog.width = "300"
#     xml_dialog.height = "300"
#     xml_dialog.top = "0"
#     xml_dialog.left = "0"
#     xml_dialog.hierarchy = "0"
#     xml_dialog.order = "0"
#     xml_dialog.name = "xmldialog"

#     xml_dialog.xmldata = \
# u"""<?xml version='1.0' encoding='utf-8'?>
# <VDOMFormContainer>
#     <Properties>
#         <Property name='label'><!--[CDATA[Default Email Composer]]--></Property>
#     </Properties>
#     <Components>
#     <RichTextArea id='inputName'
#                  class='css class'
#                  visible= '1 | 0 | true | false'
#                  fullsize='1 | 0 | true | false'
#                  disabled='1 | 0 | true | false'
#                  readonly='1 | 0 | true | false'>
#         <Properties>
#             <Property name='label'><!--[CDATA[Rich Text Area]]--></Property>
#             <Property name='defaultValue'><!--[CDATA[default value]]--></Property>
#         </Properties>
#     </RichTextArea>
#     </Components>
# </VDOMFormContainer>"""

#     print xml_dialog.wysiwyg('', '')
#     print xml_dialog.render('', '')