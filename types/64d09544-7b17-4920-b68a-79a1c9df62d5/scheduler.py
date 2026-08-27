class VDOM_scheduler(VDOM_object):
    def render(self, contents=""):
        WOID = (self.id).replace("-", "_")
        ID = "o_" + WOID

        DEBUG_INFO = {"objname": self.name, "objtype": "scheduler", "js_lib": "dhtmlx scheduler", "id": ID, "version": self.type.version}
        DEBUG_INFO_STRING = " ".join([str(key) + "='" + str(value) + "'" for key, value in DEBUG_INFO.items()])

        DISPLAY = lambda v: "none" if v == "0" else None
        SIZE_CONVERT = lambda v: str(v) + "px"
        STYLES = {
            "display": DISPLAY(self.visible),
            "position": self.positioning1,
            "z-index": self.zindex,
            "top": SIZE_CONVERT(self.top),
            "left": SIZE_CONVERT(self.left),
            "width": SIZE_CONVERT(self.width),
            "height": SIZE_CONVERT(self.height),
        }
        STYLES_STRING_FORMAT = ";".join([str(key) + ":" + str(value) for key, value in STYLES.items() if value])

        STYLES_STRING = """<style>.%(id)s { %(styles)s }</style>""" % {"id": ID, "styles": STYLES_STRING_FORMAT}
        STYLES_STRING = STYLES_STRING.replace(" ", "")

        SCRIPT_CONFIG = """<script data-meta='CONFIG'>$(document).ready(() => {%(js_code)s});</script>""" % {"js_code": self.schedulerconfig}

        TIMELINE_CONFIG = """<script data-meta='TIMELINE CONFIG'>$(document).ready(() => {%(js_code)s});</script>""" % {"js_code": self.timelineconfig}

        INIT_SCRIPT = """
          <script data-meta='scheduler init script'>
            $(document).ready(() => {
              scheduler.init("scheduler_%(id)s", new Date(), "timeline");
              scheduler.getView().setRange( new Date('%(start_date)s'), new Date('%(end_date)s') );

              scheduler.parse(`%(data)s`, "json");
            })
          </script>
        """ % {"id": ID, "data": self.data, "start_date": self.startdate, "end_date": self.enddate}

        HARDCODE_CONFIG = """
           <script data-meta='TYPE CONFIG'>
            $(document).ready(() => {
              //===============
              //Hard configuration (not editable in attrs)
              //===============
              const E2VDOMIdFormat = (id) => id.slice(2);

              scheduler.attachEvent("onParse", () => {execEventBinded(E2VDOMIdFormat('%(id)s'),'onParse');});

              scheduler.attachEvent("onTemplatesReady", () => {execEventBinded(E2VDOMIdFormat('%(id)s'),'onTemplatesReady');});

              scheduler.attachEvent("onClick", function (id, e) {
                const event = scheduler.getEvent(id);
                execEventBinded(E2VDOMIdFormat('%(id)s'), 'onClick', {id: id, value: JSON.stringify(event)});
                return true;
              });

              scheduler.attachEvent("onEventChanged", function(id, ev) {
                execEventBinded(E2VDOMIdFormat('%(id)s'), 'onEventChanged', {id: id, value: JSON.stringify(ev)});
              });

              scheduler.attachEvent("onEventDeleted", function(id, ev) {
                execEventBinded(E2VDOMIdFormat('%(id)s'), 'onEventDeleted', {id: id, value: JSON.stringify(ev)});
              });

              scheduler.attachEvent("onDblClick", function(id, e) {
                const event = scheduler.getEvent(id);
                execEventBinded(E2VDOMIdFormat('%(id)s'), 'onDblClick', {id: id, value: JSON.stringify(event)});
                return %(show_lightbox)s;
              });
            })
           </script>
        """ % {"id": ID, "show_lightbox": self.showlightbox}

        TYPE_WRAPPER = """<div {debug_string} class='{id} {classname}'>{content}</div>"""

        TYPE_HTML = """
          <div id="scheduler_{id}" class="dhx_cal_container" style='width:100%; height:100%;'></div>
            <div style="position: absolute; left: -9999px; top: -9999px;">
              <div class="dhx_cal_container">
                <div class="dhx_cal_scale_placeholder"></div>
                <div></div>
              </div>
          </div>
        """.format(id=ID)

        SCRIPTS = """{}{}{}{}""".format(SCRIPT_CONFIG, TIMELINE_CONFIG, HARDCODE_CONFIG, INIT_SCRIPT)

        CONTENT = """{}{}{}""".format(STYLES_STRING, TYPE_HTML, SCRIPTS)

        RESULT = TYPE_WRAPPER.format(debug_string=DEBUG_INFO_STRING, classname=self.cssclass, id=ID, content=CONTENT)

        return VDOM_object.render(self, contents=RESULT)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        image_id = "a0955637-e4dd-4cd1-933b-540c46acf37f"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)