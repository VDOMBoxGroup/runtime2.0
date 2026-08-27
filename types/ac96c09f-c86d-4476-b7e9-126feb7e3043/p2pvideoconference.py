class VDOM_p2pvideoconference(VDOM_object):
    def render(self, contents=""):
        WOID = (self.id).replace("-", "_")
        ID = "o_" + WOID

        DEBUG_INFO = {"objname": self.name, "objtype": "p2pvideoconference", "js_lib": "Peer js, Socket.IO", "id": ID, "version": self.type.version}
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
        STYLES_STRING = """
          <style>
          .%(id)s
            {
              %(styles)s
            }
          </style>
        """ % {"id": ID, "styles": STYLES_STRING_FORMAT}
        STYLES_STRING = STYLES_STRING.replace(" ", "")

        SCRIPT = """
          <script defer>
            $(function() {
              const conferenceOptions = {
                autoConnect: %(auto_connect)s,
                socketIoHost: '%(host)s',
                socketIoPort: '%(port)s',
                peerJsHost: '%(peer_js_host)s',
                peerJsPort: '%(peer_js_port)s',
                peerJsPath: "/",
                userName: "%(user_name)s"
              };
              let delay = 1000;
              let tryInit = setTimeout(function costyl() {
                try {
                  window.connector_%(id)s = new $.P2PVideoConferenceConnector('%(id)s', '%(room_id)s', conferenceOptions);

                  clearTimeout(tryInit)
                } catch(err) {
                  console.warn(err);
                  console.warn("Error init conference, trying again...")
                  delay += 1000;
                  if (delay > 4000) {
                    clearTimeout(tryInit)
                  } else {
                    tryInit = setTimeout(costyl, delay);
                  }
                }
              }, delay);
            });
          </script>
        """ % {
            "id": ID,
            # "woid": WOID,
            "host": self.host,
            "port": self.port,
            "room_id": self.roomid,
            "peer_js_host": self.peerjshost,
            "peer_js_port": self.peerjsport,
            "user_name": self.username,
            "auto_connect": "true" if self.autoconnect == "1" else "false",
        }

        HTML = """<div {debug_string} class='{id} {classname}'></div>""".format(debug_string=DEBUG_INFO_STRING, classname=self.cssclass, id=ID)

        RESULT = """{}{}{}""".format(STYLES_STRING, HTML, SCRIPT)

        return VDOM_object.render(self, contents=RESULT)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        image_id = "a9cdfb15-cedd-a794-8a09-801025c6b9f4"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)