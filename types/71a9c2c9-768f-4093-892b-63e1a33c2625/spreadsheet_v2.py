import json


def check_data_on_valid_json(data):
    if data:
        try:
            json.loads(data)
        except Exception:
            raise Exception("Incorrect value in data %s" % data)
    else:
        data = "[]"
    return data


def handle_styles_number_value(value):
    if value.isdigit():
        return value + "px"
    else:
        return value


class VDOM_spreadsheet_v2(VDOM_object):
    def render(self, contents=""):
        WOID = (self.id).replace("-", "_")
        ID = "o_" + WOID

        DEBUG_INFO = {"objname": self.name, "objtype": "spreadsheet_v2", "js_lib": "kendo UI (spreadsheet)", "id": ID}
        DEBUG_INFO_STRING = " ".join([str(key) + "='" + str(value) + "'" for key, value in DEBUG_INFO.items()])

        STYLES = {
            "left": handle_styles_number_value(self.left),
            "top": handle_styles_number_value(self.top),
            "position": self.positioning1,
            "width": handle_styles_number_value(self.width),
            "height": handle_styles_number_value(self.height),
            "z-index": self.zindex,
        }
        STYLES_STRING_FORMAT = ";".join([str(key) + ":" + str(value) for key, value in STYLES.items()])
        STYLES_STRING = """
          <style>
          .%(id)s
            {
              %(styles)s
            }
          </style>
        """ % {"id": ID, "styles": STYLES_STRING_FORMAT}
        STYLES_STRING = STYLES_STRING.replace(" ", "")

        self.data = check_data_on_valid_json(self.data)
        SCRIPT = """
          <script>
          /*	const exportSpreadSheetAsJSON = (id) => {
                  const _json = JSON.stringify($(`#${id}`).data("kendoSpreadsheet").toJSON());
                  const woid = id.slice(2);
                  execEventBinded(woid, "getJSON", {"JSON": _json});
              }*/
          if (typeof %(id)s === 'undefined') {
              let %(id)s = null
          }
            $(function () {
              let dataSource;
              const dataUrl = '%(url)s';
              
              if(dataUrl) {
                  fetch(dataUrl)
                        .then(response => {
                            return response.json();
                        })
                        .then(data => {
                            dataSource = data;
                            initializeSpreadsheet(dataSource);
                        })
                        .catch(error => {
                            console.error("Error loading data:", error);
                        });
              } else {
                  dataSource = JSON.parse(%(data)s);
                  initializeSpreadsheet(dataSource);
              }
            function initializeSpreadsheet(dataSource) {
              $("#%(id)s").kendoSpreadsheet({
                  columns: %(columns_count)s,
                  rows: %(rows_count)s,
                  toolbar: %(show_toolbar)s,
                  excel: {
                    fileName: '%(filename)s'
                  },
                  pdf: {
                    fileName: '%(filename)s'
                  },
                  sheetsbar: %(sheetsbar)s,
                  sheets: dataSource
              }).data("kendoSpreadsheet").one("render", function (e) {
                         e.sender.sheets().forEach(function (sheet) {
                             sheet.range(0, 0, sheet._rows._count, sheet._columns._count).enable(%(editable)s);
                         })
                  }).refresh();
                }
              });
              %(id)s = $("#%(id)s").data("kendoSpreadsheet");
          </script>
        """ % {
            "id": ID,
            "url": self.url if self.url else "",
            "data": json.dumps(self.data),
            "columns_count": self.columns_count,
            "rows_count": self.rows_count,
            "show_toolbar": self.toolbar,
            "sheetsbar": self.sheetsbar,
            "filename": self.filename if self.filename else "Workbook",
            "editable": self.editable,
            # "listname": self.listname,
        }

        HTML = """
          <div {debug_string} class='{id} {classname}'></div>
        """.format(debug_string=DEBUG_INFO_STRING, classname=self.cssclass, id=ID)

        RESULT = """
          {}
          {}
          {}
        """.format(STYLES_STRING, HTML, SCRIPT)
        return VDOM_object.render(self, contents=RESULT)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        image_id = "a9cdfb15-cedd-a794-8a09-801025c6b9f4"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)