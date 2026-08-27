class VDOM_gantt(VDOM_object):
    def render(self, contents=""):
        WOID = (self.id).replace("-", "_")
        ID = "o_" + WOID

        DEBUG_INFO = {"objname": self.name, "objtype": "gantt", "js_lib": "dhtmlx gantt", "id": ID, "version": self.type.version}
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
          .%(id)s { %(styles)s }

          .%(id)s .week_end { background-color: #%(highlight_weekend)s; }

          .constraint-marker {
              position: absolute;
              -moz-box-sizing: border-box;
              box-sizing: border-box;
              width: 56px;
              height: 56px;
              margin-top: -11px;
              opacity: 0.4;
              z-index: 1;
              background: url(/56783af3-d460-f4e0-2a32-a2da24ae9e7f.svg);
              background-size: cover;
          }

          .constraint-marker.earliest-start { margin-left: -53px; }

          .constraint-marker.latest-end {
              margin-left: -3px;
              transform: rotate(180deg);
          }
        </style>""" % {"id": ID, "styles": STYLES_STRING_FORMAT, "highlight_weekend": self.highlightweekend}

        INIT_SCRIPT = """
          <script data-meta='init script'>
            window.gantt_%(id)s = null;
            $(document).ready(() => {
              gantt_%(id)s = Gantt.getGanttInstance();

              gantt_%(id)s.plugins({
                marker: true,
                auto_scheduling: true
              });

              if (%(show_today_marker)s) {
                const todayMarkerLabelFormat = gantt_%(id)s.date.date_to_str(gantt_%(id)s.config.task_date);
                gantt_%(id)s.addMarker({
                    id: 'today',
                    start_date: new Date(),
                    css: "today",
                    title: todayMarkerLabelFormat(new Date())
                });

                // Auto update today marker
                setInterval(function() {
                    const today = gantt_%(id)s.getMarker('today');
                    today.start_date = new Date();
                    today.title = todayMarkerLabelFormat(today.start_date);
                    gantt_%(id)s.updateMarker('today');
                }, 1000*60);
              }

              // Contrsaints
              gantt_%(id)s.config.auto_scheduling = %(auto_scheduling)s;

              gantt_%(id)s.addTaskLayer(function draw_deadline(task) {
                  var constraintType = gantt_%(id)s.getConstraintType(task);
                  var types = gantt_%(id)s.config.constraint_types;
                  if (constraintType != types.ASAP && constraintType != types.ALAP && task.constraint_date) {
                      var dates = gantt_%(id)s.getConstraintLimitations(task);

                      var els = document.createElement("div");

                      if (dates.earliestStart) {
                          els.appendChild(renderDiv(task, dates.earliestStart, 'constraint-marker earliest-start'));
                      }

                      if (dates.latestEnd) {
                          els.appendChild(renderDiv(task, dates.latestEnd, 'constraint-marker latest-end'));
                      }

                      els.title = gantt_%(id)s.locale.labels[constraintType] + " " + gantt_%(id)s.templates.task_date(task.constraint_date);

                      if (els.children.length) return els;
                }
                return false;
              });

              function renderDiv(task, date, className) {
                  var el = document.createElement('div');
                  el.className = className;
                  var sizes = gantt_%(id)s.getTaskPosition(task, date);
                  el.style.left = sizes.left + 'px';
                  el.style.top = sizes.top + 'px';
                  return el;
              }

              gantt_%(id)s.config.constraint_types = {
                  // As Soon As Possible
                  ASAP: "asap",
                  // As Late As Possible
                  ALAP: "alap",
                  // Start No Earlier Than
                  SNET: "snet",
                  // Start No Later Than
                  SNLT: "snlt",
                  // Finish No Earlier Than
                  FNET: "fnet",
                  // Finish No Later Than
                  FNLT: "fnlt",
                  // Must Start On
                  MSO: "mso",
                  // Must Finish On
                  MFO: "mfo"
              };


              gantt_%(id)s.config.start_date = new Date("%(start_date)s");
              gantt_%(id)s.config.end_date = new Date("%(end_date)s");

              gantt_%(id)s.config.start_on_monday = true;

              gantt_%(id)s.config.show_tasks_outside_timescale = true;

              gantt_%(id)s.config.duration_unit = "%(duration_unit)s";
              gantt_%(id)s.config.duration_step = %(duration_step)s;


              gantt_%(id)s.config.round_dnd_dates = %(round_dnd_dates)s;


              gantt_%(id)s.config.min_column_width = %(min_column_width)s;


              gantt_%(id)s.ext.zoom.init(%(zoom_config)s);


              gantt_%(id)s.config.work_time = %(work_time)s;
              gantt_%(id)s.config.correct_work_time = %(correct_work_time)s;


              const weekEndClassCalculation = (date) => {
                if(!gantt_%(id)s.isWorkTime({date, unit: 'day'})) {
                  return "week_end";
                }
              };
              gantt_%(id)s.templates.timeline_cell_class = (task, date) => weekEndClassCalculation(date);
              gantt_%(id)s.templates.scale_cell_class = weekEndClassCalculation;


              gantt_%(id)s.config.columns = %(columns)s;


              gantt_%(id)s.init("gantt_%(id)s");


              //----E2VDOM----
              const E2VDOMIdFormat = (id) => id.slice(2);

              gantt_%(id)s.attachEvent("onAfterTaskUpdate", function(id, item) {
                execEventBinded(E2VDOMIdFormat('%(id)s'), 'onAfterTaskUpdate', {id: id, value: JSON.stringify(item)});
              });

              gantt_%(id)s.attachEvent("onTaskClick", function(id, e) {
                  const task = gantt_%(id)s.getTask(id);
                  execEventBinded(E2VDOMIdFormat('%(id)s'), 'onTaskClick', {id: id, value: JSON.stringify(task)});
                  return true;
              });

              gantt_%(id)s.attachEvent("onTaskDblClick", function(id, e) {
                  const task = gantt_%(id)s.getTask(id);
                  execEventBinded(E2VDOMIdFormat('%(id)s'), 'onTaskDblClick', {id: id, value: JSON.stringify(task)});
                  return %(show_lightbox)s;
              });

              gantt_%(id)s.attachEvent("onAfterTaskDelete", function(id,item){
                  execEventBinded(E2VDOMIdFormat('%(id)s'), 'onAfterTaskDelete', {id: id, value: JSON.stringify(item)});
              });
            })
          </script>
        """ % {
            "id": ID,
            "start_date": self.startdate,
            "end_date": self.enddate,
            "columns": self.columns,
            "duration_unit": self.durationunit,
            "duration_step": self.durationstep,
            "round_dnd_dates": self.rounddnddates,
            "work_time": self.worktime,
            "correct_work_time": self.correctworktime,
            "min_column_width": self.mincolumnwidth,
            "zoom_config": self.zoom,
            "show_lightbox": self.showlightbox,
            "show_today_marker": self.showtodaymarker,
            "auto_scheduling": self.autoscheduling,
        }

        SET_DATA_SCRIPT = """<script>$(document).ready(()=>{gantt_%(id)s.parse(`%(data)s`);})</script>""" % {"id": ID, "data": self.data}

        TYPE_WRAPPER = """<div {debug_string} class='{id} {classname}'>{content}</div>"""

        TYPE_HTML = """<div id="gantt_{id}" style='width:100%; height:100%;'></div>""".format(id=ID)

        SCRIPTS = """{}{}""".format(INIT_SCRIPT, SET_DATA_SCRIPT)

        CONTENT = """{}{}{}""".format(STYLES_STRING, TYPE_HTML, SCRIPTS)

        RESULT = TYPE_WRAPPER.format(debug_string=DEBUG_INFO_STRING, classname=self.classname, id=ID, content=CONTENT)

        return VDOM_object.render(self, contents=RESULT)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        image_id = "b45e4301-fae1-98de-b355-a2ce418f89fb"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)