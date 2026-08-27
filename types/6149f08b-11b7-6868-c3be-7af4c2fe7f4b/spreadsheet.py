class VDOM_spreadsheet(VDOM_object):
    def render(self, contents=""):  # runtime
        id = "o_" + (self.id).replace("-", "_")

        result = """<div id="{id}" objname="{objname}" objtype="{objtype}" style="left:{left}px; top: {top}px; position:absolute; width:{width}px; height: {height}px; {display}"></div>""".format(
            id=id,
            objname=self.name,
            objtype="spreadsheet",
            left=self.left,
            top=self.top,
            width=self.width,
            height=self.height,
            display="" if self.visible == "1" else "display:none",
        )
        result += """
        <script>
          $(document).ready(() => {
              $('[objtype=spreadsheet]').empty();
              $('iframe.k-spreadsheet-clipboard-paste').remove();
              window.spreadsheet_object = $("#%(id)s").kendoSpreadsheet();
              var b64data = '%(spreadsheet_content)s';
              function createBlobFromBase64(s) {
                  var byteCharacters = atob(s);
                  var byteNumbers = new Array(byteCharacters.length);
                  for (var i = 0; i < byteCharacters.length; i++) {
                      byteNumbers[i] = byteCharacters.charCodeAt(i);
                  }
                  var byteArray = new Uint8Array(byteNumbers);
                  return new Blob([byteArray], {type: 'application/octet-stream'});
              }
              if (b64data) {
                setTimeout(() => {$('[objtype=spreadsheet]').data('kendoSpreadsheet').fromFile(createBlobFromBase64(b64data))}, 10);
              }
          })
        </script>
        """ % dict(id=id, spreadsheet_content=self.content)

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        image_id = "18e2b159-f1f6-529c-e4e8-7af4c3033b41"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)