class VDOM_formbuilder(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        language = {
            "en-US": "a0947d68-b7b4-b1f2-d796-223e6390a140",
            "fr-FR": "9d081008-f519-bdaa-d75c-223e83c99ec1",
            "ru-RU": "030f2cb3-a62a-5c52-24d6-223e93bcfdff",
        }
        overflow = {"0": "auto", "1": "hidden", "2": "scroll", "3": "visible"}
        current_language = language.get(self.language, "a0947d68-b7b4-b1f2-d796-223e6390a140")

        woid = (self.id).replace("-", "_")
        id = "o_" + woid

        styles = {
            "z-index": "%s" % self.zindex if int(self.zindex) != 0 else "",
            "display": "none" if self.visible == "0" else self.displaying,
            "position": "%s" % self.positioning if self.positioning != "static" else "",
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "overflow": overflow.get(self.overflow, ""),
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='formbuilder' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = ""

            # JS FOR HIERARCHY SELECT
        request.dyn_libraries[self.name] = """<script>
          /*!
          * Generated using the Bootstrap Customizer (https://getbootstrap.com/docs/3.4/customize/)
          */

          /*!
          * Bootstrap v3.4.1 (https://getbootstrap.com/)
          * Copyright 2011-2020 Twitter, Inc.
          * Licensed under the MIT license
          */
          if ($.formBuilderModulesEnserted === true) {throw new Error("Module is already exists")}
          if("undefined"==typeof jQuery)throw new Error("Bootstrap's JavaScript requires jQuery");+function(t){"use strict";var e=t.fn.jquery.split(" ")[0].split(".");if(e[0]<2&&e[1]<9||1==e[0]&&9==e[1]&&e[2]<1||e[0]>3)throw new Error("Bootstrap's JavaScript requires jQuery version 1.9.1 or higher, but lower than version 4")}(jQuery),+function(t){"use strict";function e(e){var r=e.attr("data-target");r||(r=e.attr("href"),r=r&&/#[A-Za-z]/.test(r)&&r.replace(/.*(?=#[^\s]*$)/,""));var o="#"!==r?t(document).find(r):null;return o&&o.length?o:e.parent()}function r(r){r&&3===r.which||(t(n).remove(),t(a).each(function(){var o=t(this),n=e(o),a={relatedTarget:this};n.hasClass("open")&&(r&&"click"==r.type&&/input|textarea/i.test(r.target.tagName)&&t.contains(n[0],r.target)||(n.trigger(r=t.Event("hide.bs.dropdown",a)),r.isDefaultPrevented()||(o.attr("aria-expanded","false"),n.removeClass("open").trigger(t.Event("hidden.bs.dropdown",a)))))}))}function o(e){return this.each(function(){var r=t(this),o=r.data("bs.dropdown");o||r.data("bs.dropdown",o=new i(this)),"string"==typeof e&&o[e].call(r)})}var n=".dropdown-backdrop",a='[data-toggle="dropdown"]',i=function(e){t(e).on("click.bs.dropdown",this.toggle)};i.VERSION="3.4.1",i.prototype.toggle=function(o){var n=t(this);if(!n.is(".disabled, :disabled")){var a=e(n),i=a.hasClass("open");if(r(),!i){"ontouchstart"in document.documentElement&&!a.closest(".navbar-nav").length&&t(document.createElement("div")).addClass("dropdown-backdrop").insertAfter(t(this)).on("click",r);var d={relatedTarget:this};if(a.trigger(o=t.Event("show.bs.dropdown",d)),o.isDefaultPrevented())return;n.trigger("focus").attr("aria-expanded","true"),a.toggleClass("open").trigger(t.Event("shown.bs.dropdown",d))}return!1}},i.prototype.keydown=function(r){if(/(38|40|27|32)/.test(r.which)&&!/input|textarea/i.test(r.target.tagName)){var o=t(this);if(r.preventDefault(),r.stopPropagation(),!o.is(".disabled, :disabled")){var n=e(o),i=n.hasClass("open");if(!i&&27!=r.which||i&&27==r.which)return 27==r.which&&n.find(a).trigger("focus"),o.trigger("click");var d=" li:not(.disabled):visible a",s=n.find(".dropdown-menu"+d);if(s.length){var p=s.index(r.target);38==r.which&&p>0&&p--,40==r.which&&p<s.length-1&&p++,~p||(p=0),s.eq(p).trigger("focus")}}}};var d=t.fn.dropdown;t.fn.dropdown=o,t.fn.dropdown.Constructor=i,t.fn.dropdown.noConflict=function(){return t.fn.dropdown=d,this},t(document).on("click.bs.dropdown.data-api",r).on("click.bs.dropdown.data-api",".dropdown form",function(t){t.stopPropagation()}).on("click.bs.dropdown.data-api",a,i.prototype.toggle).on("keydown.bs.dropdown.data-api",a,i.prototype.keydown).on("keydown.bs.dropdown.data-api",".dropdown-menu",i.prototype.keydown)}(jQuery);

          !function (a) { "use strict"; function b(a, b) { a.offsetHeight + a.scrollTop < b.offsetTop + b.offsetHeight ? a.scrollTop = b.offsetTop + b.offsetHeight - a.offsetHeight : a.scrollTop > b.offsetTop && (a.scrollTop = b.offsetTop) } var c = function (b, c) { this.$element = a(b), this.options = a.extend({}, a.fn.hierarchySelect.defaults, c), this.$button = this.$element.children("button"), this.$selectedLabel = this.$button.children(".selected-label"), this.$menu = this.$element.children(".dropdown-menu"), this.$menuInner = this.$menu.children(".inner"), this.$searchbox = this.$menu.find("input"), this.$hiddenField = this.$element.children("input"), this.previouslySelected = null, this.init() }; c.prototype = { constructor: c, init: function () { this.setWidth(), this.setHeight(), this.initSelect(), this.clickListener(), this.buttonListener(), this.searchListener() }, initSelect: function () { var a = this.$menuInner.find("li[data-default-selected]:first"); if (a.length) this.setValue(a.data("value")); else { var b = this.$menuInner.find("li:first"); this.setValue(b.data("value")) } }, setWidth: function () { if ("auto" === this.options.width) { var a = this.$menu.width(); this.$element.css("min-width", a + 2 + "px") } else this.options.width ? this.$element.css("width", this.options.width) : this.$element.css("min-width", "42px") }, setHeight: function () { this.options.height && (this.$menu.css("overflow", "hidden"), this.$menuInner.css({ "max-height": this.options.height, "overflow-y": "auto" })) }, getText: function () { return this.$selectedLabel.text() }, getValue: function () { return this.$hiddenField.val() }, setValue: function (a) { var b = this.$menuInner.children('li[data-value="' + a + '"]:first'); this.setSelected(b) }, enable: function () { this.$button.removeAttr("disabled") }, disable: function () { this.$button.attr("disabled", "disabled") }, setSelected: function (a) { if (a.length) { var b = a.children("a").text(), c = a.data("value"); this.$selectedLabel.html(b), this.$hiddenField.val(c), this.$menuInner.find(".active").removeClass("active"), a.addClass("active"), this.$element.trigger("change") } }, moveUp: function () { var a = this.$menuInner.find("li:not(.hidden,.disabled)"), c = this.$menuInner.find(".active"), d = a.index(c); void 0 !== a[d - 1] && (this.$menuInner.find(".active").removeClass("active"), a[d - 1].classList.add("active"), b(this.$menuInner[0], a[d - 1])) }, moveDown: function () { var a = this.$menuInner.find("li:not(.hidden,.disabled)"), c = this.$menuInner.find(".active"), d = a.index(c); void 0 !== a[d + 1] && (this.$menuInner.find(".active").removeClass("active"), a[d + 1] && (a[d + 1].classList.add("active"), b(this.$menuInner[0], a[d + 1]))) }, selectItem: function () { var a = this, b = this.$menuInner.find(".active"); b.hasClass("hidden") || b.hasClass("disabled") || (setTimeout(function () { a.$button.focus() }, 0), b && this.setSelected(b), this.$button.dropdown("toggle")) }, clickListener: function () { var b = this; this.$element.on("show.bs.dropdown", function () { var c = a(this), d = a(window).scrollTop(), e = a(window).height(), f = c.offset().top - d, g = c.outerHeight(), h = e - f - g, i = b.$menu.outerHeight(!0); h < i && f > i && c.toggleClass("dropup", !0); var j = b.$menuInner.find(".active"); j && setTimeout(function () { var a = j[0], b = j[0].parentNode; b.scrollTop <= a.offsetTop && b.scrollTop + b.clientHeight > a.offsetTop + a.clientHeight || (a.parentNode.scrollTop = a.offsetTop) }, 0) }), this.$element.on("shown.bs.dropdown", function () { b.previouslySelected = b.$menuInner.find(".active"), b.$searchbox.focus() }), this.$element.on("hidden.bs.dropdown", function () { b.$element.toggleClass("dropup", !1) }), this.$menuInner.on("click", "li a", function (c) { c.preventDefault(); var d = a(this), e = d.parent(); e.hasClass("disabled") ? c.stopPropagation() : b.setSelected(e) }) }, buttonListener: function () { var a = this; this.options.search || this.$button.on("keydown", function (b) { switch (b.keyCode) { case 9: a.$element.hasClass("open") && b.preventDefault(); break; case 13: a.$element.hasClass("open") && (b.preventDefault(), a.selectItem()); break; case 27: a.$element.hasClass("open") && (b.preventDefault(), b.stopPropagation(), a.$button.focus(), a.previouslySelected && a.setSelected(a.previouslySelected), a.$button.dropdown("toggle")); break; case 38: a.$element.hasClass("open") && (b.preventDefault(), b.stopPropagation(), a.moveUp()); break; case 40: a.$element.hasClass("open") && (b.preventDefault(), b.stopPropagation(), a.moveDown()) } }) }, searchListener: function () { function b(a) { for (var b = a, c = b.data("level"); "object" == typeof b && b.length > 0 && c > 1;)c-- , b = b.prevAll('li[data-level="' + c + '"]:first'), b.hasClass("hidden") && (b.toggleClass("disabled", !0), b.removeClass("hidden")) } var c = this; if (!this.options.search) return void this.$searchbox.parent().toggleClass("hidden", !0); this.$searchbox.on("keydown", function (a) { switch (a.keyCode) { case 9: a.preventDefault(), a.stopPropagation(), c.$menuInner.click(), c.$button.focus(); break; case 13: c.selectItem(); break; case 27: a.preventDefault(), a.stopPropagation(), c.$button.focus(), c.previouslySelected && c.setSelected(c.previouslySelected), c.$button.dropdown("toggle"); break; case 38: a.preventDefault(), c.moveUp(); break; case 40: a.preventDefault(), c.moveDown() } }), this.$searchbox.on("input propertychange", function (d) { d.preventDefault(); var e = c.$searchbox.val().toLowerCase(), f = c.$menuInner.find("li"); 0 === e.length ? f.each(function () { var b = a(this); b.toggleClass("disabled", !1), b.toggleClass("hidden", !1) }) : f.each(function () { var d = a(this); -1 != d.children("a").text().toLowerCase().indexOf(e) ? (d.toggleClass("disabled", !1), d.toggleClass("hidden", !1), c.options.hierarchy && b(d)) : (d.toggleClass("disabled", !1), d.toggleClass("hidden", !0)) }) }) } }; var d = function (b) { var d, e = Array.prototype.slice.call(arguments, 1), f = this.each(function () { var f = a(this), g = f.data("HierarchySelect"), h = "object" == typeof b && b; g || f.data("HierarchySelect", g = new c(this, h)), "string" == typeof b && (d = g[b].apply(g, e)) }); return void 0 === d ? f : d }, e = a.fn.hierarchySelect; a.fn.hierarchySelect = d, a.fn.hierarchySelect.defaults = { width: "auto", height: "208px", hierarchy: !0, search: !0 }, a.fn.hierarchySelect.Constructor = c, a.fn.hierarchySelect.noConflict = function () { return a.fn.hierarchySelect = e, this } }(jQuery);
          $.formBuilderModulesEnserted = true;
        </script>"""
        # CSS FOR HIERARCHY SELECT
        HIERARCHY_STYLES = """
          /*!
          * Generated using the Bootstrap Customizer (https://getbootstrap.com/docs/3.4/customize/)
          */
          /*!
          * Bootstrap v3.4.1 (https://getbootstrap.com/)
          * Copyright 2011-2019 Twitter, Inc.
          * Licensed under MIT (https://github.com/twbs/bootstrap/blob/master/LICENSE)
          */
          /*! normalize.css v3.0.3 | MIT License | github.com/necolas/normalize.css */
          %(id)s .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            border: 0;
          }
          %(id)s .sr-only-focusable:active,
          %(id)s .sr-only-focusable:focus {
            position: static;
            width: auto;
            height: auto;
            margin: 0;
            overflow: visible;
            clip: auto;
          }
          %(id)s .caret {
            display: inline-block;
            width: 0;
            height: 0;
            margin-left: 2px;
            vertical-align: middle;
            border-top: 4px dashed;
            border-top: 4px solid \9;
            border-right: 4px solid transparent;
            border-left: 4px solid transparent;
          }
          %(id)s .dropup,
          %(id)s .dropdown {
            position: relative;
          }
          %(id)s .dropdown-toggle:focus {
            outline: 0;
          }
          %(id)s .dropdown-menu {
            position: absolute;
            top: 100%%;
            left: 0;
            overflow: visible !important;
            z-index: 1000;
            width: 100%%;
            display: none;
            float: left;
            min-width: 160px;
            padding: 5px 0;
            margin: 2px 0 0;
            text-align: left;
            list-style: none;
            background-color: #ffffff;
            -webkit-background-clip: padding-box;
            background-clip: padding-box;
            border-radius: 4px;
            -webkit-box-shadow: 0 6px 12px rgba(0, 0, 0, 0.175);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.175);
          }
          %(id)s .dropdown-menu .divider {
            height: 1px;
            margin: 9px 0;
            overflow: hidden;
            background-color: #e5e5e5;
          }
          %(id)s .dropdown-menu > li > a {
            display: block;
            padding: 3px 20px;
            text-decoration: none;
            clear: both;
            font-weight: 400;
            line-height: 1.42857143;
            color: #333333;
            white-space: nowrap;
          }
          %(id)s .dropdown-menu > li > a:hover,
          %(id)s .dropdown-menu > li > a:focus {
            color: #262626;
            text-decoration: none;
            background-color: #f5f5f5;
          }
          %(id)s .dropdown-menu > .disabled > a,
          %(id)s .dropdown-menu > .disabled > a:hover,
          %(id)s .dropdown-menu > .disabled > a:focus {
            color: #777777;
          }
          %(id)s .open > .dropdown-menu {
            display: block;
          }
          %(id)s .hidden {
              display: none;
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu {
            box-sizing: border-box;
            min-width: 100%%;
            z-index: 1035
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu.inner {
            border: 0 none;
            border-radius: 0;
            box-shadow: none;
            float: none;
            margin: 0;
            padding: 0;
            position: relative
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu li {
            position: relative
          }

          %(id)s .hierarchy-select.btn-group .hs-searchbox {
            padding: 4px 8px
          }

          %(id)s .hierarchy-select.btn-group .hs-searchbox>input.form-control {
            margin-bottom: 0;
            width: 100%%
          }

          %(id)s .hierarchy-select.btn-group>.dropdown-toggle {
            padding-right: 25px;
            width: 100%%
          }

          %(id)s .hierarchy-select.btn-group>.dropdown-toggle:focus {
            outline: thin dotted #333 !important;
            outline-offset: -2px
          }

          %(id)s .hierarchy-select.btn-group>.dropdown-toggle>.selected-label {
            display: inline-block;
            overflow: hidden;
            text-align: left;
            width: 100%%
          }

          %(id)s .hierarchy-select.btn-group>.dropdown-toggle>.caret {
            margin-top: -2px;
            position: absolute;
            right: 12px;
            top: 50%%;
            vertical-align: middle
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu li[data-level='2']>a {
            padding-left: 40px
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu li[data-level='3']>a {
            padding-left: 60px
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu li[data-level='4']>a {
            padding-left: 80px
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu li[data-level='5']>a {
            padding-left: 100px
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu li[data-level='6']>a {
            padding-left: 120px
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu li[data-level='7']>a {
            padding-left: 140px
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu li[data-level='8']>a {
            padding-left: 160px
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu li[data-level='9']>a {
            padding-left: 180px
          }

          %(id)s .hierarchy-select.btn-group .dropdown-menu li[data-level='10']>a {
            padding-left: 200px
          }

          %(id)s .has-error .hierarchy-select.btn-group>button,
          %(id)s .has-error .hierarchy-select.btn-group>button:active,
          %(id)s .has-error .hierarchy-select.btn-group>button:focus,
          %(id)s .has-error .hierarchy-select.btn-group>button:hover {
            border-color: #a94442
          }

          %(id)s .has-error .hierarchy-select.btn-group.open>button,
          %(id)s .has-error .hierarchy-select.btn-group.open>button:active,
          %(id)s .has-error .hierarchy-select.btn-group.open>button:focus,
          %(id)s .has-error .hierarchy-select.btn-group.open>button:hover {
            border-color: #a94442
          }

          %(id)s .has-error .hierarchy-select.btn-group .form-control {
            border-color: #ccc
          }

          %(id)s .has-error .hierarchy-select.btn-group .form-control:focus {
            border-color: #66afe9;
            box-shadow: 0 1px 1px rgba(0, 0, 0, 0.075) inset, 0 0 8px rgba(102, 175, 233, 0.6)
          }
        """ % {"id": "#{}".format(id)}

        css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

        result = """
      <style>{hierarchy_styles}</style>
      {css}
      <div {debug_info} id="{id}" style="{style}" name="{name}" class="{classname}"></div>  	
        <script>jQuery(function($) {{		
            var fields = [
              {{
                label: "Select hierarchy",
                attrs: {{
                  type: "selecthierarchy"
                }},
                icon: `<svg width="18" height="16" viewBox="0 0 18 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path fill-rule="evenodd" clip-rule="evenodd" d="M16.0017 1.84352H1.02948V4.98139H16.0017V1.84352ZM0.02948 0.843518V5.98139H17.0017V0.843518H0.02948Z" fill="black" />
                          <path fill-rule="evenodd" clip-rule="evenodd" d="M11.0093 5.94227H1.11832V14.8242H11.0093V5.94227ZM0.02948 4.94227V15.8242H12.0981V4.94227H0.02948Z" fill="black" />
                          <path d="M12.903 2.77744H15.2121V3.96088H12.903V2.77744Z" fill="black" />
                          <path d="M10.9724 1.70945H12.0981V5.15748H10.9724V1.70945Z" fill="black" />
                          <path d="M2.22314 6.9765H6.00274V8.45739H2.22314V6.9765Z" fill="black" />
                          <path d="M3.94348 9.48811H8.91973V10.969H3.94348V9.48811Z" fill="black" />
                          <path d="M3.94348 11.9991H8.91973V13.48H3.94348V11.9991Z" fill="black" />
                        </svg>`
              }},
              {{
                label: "Image",
                attrs: {{
                  type: "image"
                }},
                icon: `<div style='position: relative; padding-left: 26px;'><span style='font-size: 25px;float: left;top: -10px;left: -5px;position: absolute;'>🖻</span><div>`
              }}
            ];
            var templates = {{
              selecthierarchy: function(fieldData) {{
                return {{
                  field: '<span id="' + fieldData.name + '">',
                  onRender: function() {{
                    const btn_group = $(
                      `<div class="btn-group hierarchy-select" data-resize="auto" data-id="${{fieldData.name}}"></div>`
                    );

                    const dropdown_toogle = $(
                      `<button type="button" class="btn dropdown-toggle" data-toggle="dropdown"></button>`
                    );
                    const selected_label = $(
                      `<span class="selected-label pull-left"> </span>`
                    );
                    const cared = $(`<span class="caret"></span>`);
                    const sr_only = $(`<span class="sr-only">Toggle Dropdown</span>`);
                    dropdown_toogle.append(selected_label);
                    dropdown_toogle.append(cared);
                    dropdown_toogle.append(sr_only);
                    
                    btn_group.append(dropdown_toogle);

                    const dropdown_menu = $(`<div class="dropdown-menu open"></div>`);

                    const hs_searchbox = $(`<div class="hs-searchbox"></div>`);
                    const searchbox_input = $(
                      `<input type="text" class="form-control" autocomplete="off">`
                    );
                    hs_searchbox.append(searchbox_input);

                    dropdown_menu.append(hs_searchbox);

                    const dropdown_menu_inner = $(
                      `<ul class="dropdown-menu inner" role="menu"></ul>`
                    );

                    if (fieldData.value) data = JSON.parse(fieldData.value);
                    else data = []
                    data.forEach(el => {{
                      const item = $(
                        `<li data-value="${{el.data_value}}" data-level="${{el.data_level}}" class="level-${{el.data_level}}">`
                      );
                      const item_link = $(`<a href="#">${{el.display_value}}</a>`);
                      item.append(item_link);
                      dropdown_menu_inner.append(item);
                    }});

                    dropdown_menu.append(dropdown_menu_inner);

                    btn_group.append(dropdown_menu);
                    
                    const hidden_input = $(`<input class="hidden hidden-field" name="${{fieldData.name}}" readonly aria-hidden="true" type="hidden" />`);
                    btn_group.append(hidden_input);

                    $(document.getElementById(fieldData.name)).append(btn_group);
                    $(`[data-id='${{fieldData.name}}']`).hierarchySelect({{
                      hierarchy: true,
                      search: true,
                      width: 250
                    }});
                  }}
                }};
              }},
              image: function(fieldData) {{
                return {{
                  field: '<span id="' + fieldData.name + '">',
                  onRender: function() {{
                    if (fieldData.value) data = JSON.parse(fieldData.value)
                    else data = {{}}
                    const width = data.width;
                    const height = data.height;
                    const id = `data-id='${{fieldData.name}}'`;
                    const src = data.src;
                    const styles = 
                    `
                      img[${{id}}] 
                      {{
                          width: ${{width}};
                          height: ${{height}};
                      }}
                    `
                    $(document.getElementById(fieldData.name)).html(`<style>${{styles}}</style><img ${{id}} src='${{src}}'/>`);
                  }}
                }};
              }}
            }};
        $('#{id}').formBuilder({{fields: fields, templates: templates, dataType: '{datatype}',formData: `{contents}`, disableInjectedStyle: true, i18n: {{
    locale: '{language}',
    location: '/',
    extension: '.lang',
    }},
        onSave: function(evt, formData){{execEventBinded($(evt.currentTarget).parents('.form-builder').parent()[0].id.substring(2), 'save', {{'data':JSON.stringify(formData)}})}}  }}); }});</script>
      """.format(
            debug_info=debug_info,
            id=id,
            # woid=woid,
            style=style,
            name=self.name,
            css=css,
            contents=self.data or "[]" if self.datatype == "json" else "'<form-template></form-template>'",
            classname=" ".join([self.classname, "vdom_formbuilder"]).strip(),
            datatype=self.datatype,
            language=current_language,
            hierarchy_styles=HIERARCHY_STYLES,
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        image_id = "54e7f8ab-64f1-b113-029e-1703a76c6fa4"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
    o = object
    mods = {}

    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, "").lower()

            if obj_value.isdigit() and attr_value.isdigit():
                mods[attr] = attr_value + "px"
                mods["ide_" + attr] = attr_value
            elif obj_value.endswith("px") and (attr_value.isdigit() or "px" in attr_value):
                mods[attr] = attr_value.rstrip("px") + "px"
                mods["ide_" + attr] = attr_value.rstrip("px")
            elif attr_value.isdigit() or "px" in attr_value:
                mods[attr] = attr_value if "px" in attr_value else obj_value
                mods["ide_" + attr] = attr_value.rstrip("px")
            else:
                mods[attr] = attr_value

    attributes.update(mods)

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