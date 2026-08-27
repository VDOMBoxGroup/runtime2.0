import json
import vobject
import datetime
from dateutil.relativedelta import *
import random


class VDOM_fullcalendar(VDOM_object):
    TF_DICT = {"1": "H:mm{ - H:mm}", "0": "h(:mm)tt{ - h(:mm)tt}"}
    VIEW_DICT = {"0": "month", "1": "agendaWeek", "2": "agendaDay"}
    DAY_LIST = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    MONTH_LIST = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    SHORT_MONTH_LIST = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    SHORT_DAY_LIST = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    FIRST_DAY_LIST = ["0", "1", "2", "3", "4", "5", "6", "7"]
    SLOTMINUTES = {"0": 5, "1": 10, "2": 15, "3": 20, "4": 25, "5": 30}
    TRUE_FALSE = {"0": "false", "1": "true"}
    VERSION = "version 20.00"
    DATE_MOD = "18.06.2012"

    RENDER_DIV = """<div id="%s" style="%s"></div>"""
    RENDER_SCRIPT = """
    $.curCSS = function (element, attrib, val) {$(element).css(attrib, val);};
    /*Fullcalendar. VDOM Type Version %(version)s. Last modified - %(date_mod)s*/
    $(function(){

        %(window_lazyloading_1)s

        $("#%(id_out)s").fullCalendar({

            header: {
                left: '',
                center: '',
                right: ''
            },

            weekMode: "liquid",
            axisFormat: "%(time_format)s",
            timeFormat: "%(time_format)s",
            monthNames: %(month_names)s,
            monthNamesShort: %(short_month_names)s,
            dayNames: %(day_names)s,
            dayNamesShort: %(short_day_names)s,
            editable: %(is_editable)s,
            selectable: %(is_selectable)s,
            firstDay: %(first_day)s,
            firstHour: %(first_hour)s,
            defaultView: "%(default_view)s",
            allDaySlot: %(is_allday_visible)s,
            allDayText: "%(allday_title)s",
            slotMinutes: %(minutes_interval)s,
            eventSources: %(event_sources)s,

            viewChanged: function( viewName, title ) {
                execEventBinded("%(id_woo)s", "viewChanged", {
                    title: title.replace("&#8212;"," - "),
                    view: viewName
                });
            },
            dateChanged: function( viewName, title, start, end %(lazyloading_1)s ){
                execEventBinded("%(id_woo)s", "dateChanged", {
                    start: Math.round(visStart.getTime() / 1000),
                    end: Math.round(visEnd.getTime() / 1000),
                    title: title.replace("&#8212;"," - "),
                    view: viewName,
                    timezoneOffset: visStart.getTimezoneOffset()
                });
                %(lazy_condition)s
                execEventBinded("%(id_woo)s", "getEvents", {
                    start: Math.round(%(lazyloading_start)s.getTime() / 1000),
                    end: Math.round(%(lazyloading_end)s.getTime() / 1000),
                    view: viewName,
                    timezoneOffset: %(lazyloading_start)s.getTimezoneOffset()
                });
                %(lazy_condition_1)s
            },

            select: function(startDate, endDate, allDay)
            {
                end = endDate.getTime() / 1000;
                start = startDate.getTime() / 1000;
                $("#%(id_out)s").fullCalendar('unselect');
                execEventBinded("%(id_woo)s", "daysSelected", {
                    start: start,
                    end: end,
                    allDay: allDay || 0,
                    timezoneOffset: startDate.getTimezoneOffset()
                });
            },

            eventClick: function(event) {
                execEventBinded("%(id_woo)s", "eventClick", { id:event.id, instance: event.instance });
            },

            eventDrop: function(event, dayDelta, minuteDelta, allDay)
            {
                start = event.start || 0;
                end = event.end === null ? start : event.end;
                execEventBinded("%(id_woo)s", "eventDrag", {
                    id: event.id,
                    start: Math.round( start.getTime() / 1000),
                    end: Math.round( end.getTime() / 1000),
                    instance: event.instance,
                    allDay: allDay || 0,
                    dayDelta: dayDelta || 0,
                    minuteDelta: minuteDelta || 0,
                    timezoneOffset: event.start.getTimezoneOffset()
                })
            },

            eventResize: function( event, dayDelta, minuteDelta )
            {
                start = event.start || 0;
                end = event.end === null ? start : event.end;
                execEventBinded("%(id_woo)s", "eventResize", {
                    id: event.id,
                    start: Math.round( start.getTime() / 1000),
                    end: Math.round( end.getTime() / 1000),
                    instance: event.instance,
                    dayDelta: dayDelta || 0,
                    minuteDelta: minuteDelta || 0,
                    timezoneOffset: event.start.getTimezoneOffset()
                })
            }
        });

        $("#%(id_out)s").fullCalendar( 'render' );
        $("#%(id_out)s").fullCalendar( 'gotoDate',  %(year)s, %(month)s, %(day)s);
    });
"""

    def render(self, contents=""):
        id_woo = (self.id).replace("-", "_")
        id_out = "o_" + id_woo

        # visibility
        visibility = "hidden" if self.visible == "0" else "visible"

        # timeFormat
        timeFormat = VDOM_fullcalendar.TF_DICT["1"] if self.time_format not in VDOM_fullcalendar.TF_DICT.keys() else VDOM_fullcalendar.TF_DICT[self.time_format]

        # view
        view = (
            VDOM_fullcalendar.VIEW_DICT["0"]
            if self.view not in VDOM_fullcalendar.VIEW_DICT not in VDOM_fullcalendar.VIEW_DICT.keys()
            else VDOM_fullcalendar.VIEW_DICT[self.view]
        )

        # default date
        default_date = self.display_date.split("-") if self.display_date else str(datetime.date.today()).split("-")

        # day names

        day_names = []
        if isinstance(self.day_names, (tuple, list)):
            day_names = self.day_names
        elif isinstance(self.day_names, str):
            day_names = self.day_names.split("|")

        if len(day_names) != 7:
            day_names = VDOM_fullcalendar.DAY_LIST

        # short day names
        short_day_names = []
        if isinstance(self.short_day_names, (tuple, list)):
            short_day_names = self.short_day_names
        elif isinstance(self.short_day_names, str):
            short_day_names = self.short_day_names.split("|")

        if len(short_day_names) != 7:
            short_day_names = VDOM_fullcalendar.SHORT_DAY_LIST

        # month names
        month_names = []
        if isinstance(self.month_names, (tuple, list)):
            month_names = self.month_names
        elif isinstance(self.month_names, str):
            month_names = self.month_names.split("|")

        if len(month_names) != 12:
            month_names = VDOM_fullcalendar.MONTH_LIST

        # short month names
        short_month_names = []
        if isinstance(self.short_month_names, (tuple, list)):
            short_month_names = self.short_month_names
        elif isinstance(self.short_month_names, str):
            short_month_names = self.short_month_names.split("|")

        if len(short_month_names) != 12:
            short_month_names = VDOM_fullcalendar.SHORT_MONTH_LIST

        # first_hour
        first_hour = int(self.first_hour)

        # first day in week
        first_day = int(self.first_day) if self.first_day in VDOM_fullcalendar.FIRST_DAY_LIST else 1

        # is calendar editable or not
        editable = VDOM_fullcalendar.TRUE_FALSE[self.editable] if self.editable in VDOM_fullcalendar.TRUE_FALSE.keys() else VDOM_fullcalendar.TRUE_FALSE["1"]

        # is calendar selecable or not
        selectable = (
            VDOM_fullcalendar.TRUE_FALSE[self.selectable] if self.selectable in VDOM_fullcalendar.TRUE_FALSE.keys() else VDOM_fullcalendar.TRUE_FALSE["1"]
        )

        # is all-day slot visible or not
        allday_visible = (
            VDOM_fullcalendar.TRUE_FALSE[self.all_day_visible]
            if self.all_day_visible in VDOM_fullcalendar.TRUE_FALSE.keys()
            else VDOM_fullcalendar.TRUE_FALSE["1"]
        )

        # allday slot text
        allday_title = self.all_day_title if self.all_day_title else "Allday"

        # slotminutes interval
        slotminutes = (
            VDOM_fullcalendar.SLOTMINUTES[self.slot_minutes]
            if self.slot_minutes in VDOM_fullcalendar.SLOTMINUTES.keys()
            else VDOM_fullcalendar.SLOTMINUTES["5"]
        )

        if self.lazyloading == "1":
            window_lazy, lazyloading_1, lazyloading_start, lazyloading_end = (
                "window.visible_start = window.visible_end = new Date(1); ",
                "",
                "window.visible_start",
                "window.visible_end",
            )
            lazy_condition = """if ( ( window.visible_start - start) && (window.visible_end - end ) )
                                        {window.visible_start = start; window.visible_end = end;"""
            lazy_condition_1 = "}"
        else:
            window_lazy, lazyloading_1, lazyloading_start, lazyloading_end, lazy_condition, lazy_condition_1 = (
                "",
                ",visStart, visEnd",
                "visStart",
                "visEnd",
                "",
                "",
            )

        style_params = {"zindex": self.zindex, "top": self.top, "left": self.left, "width": self.width, "height": self.height, "visibility": visibility}

        mainstyle = (
            """z-index:%(zindex)s;
                    position:absolute;
                    top: %(top)spx;
                    left: %(left)spx;
                    width: %(width)spx;
                    height: %(height)spx;
                    visibility: %(visibility)s;"""
            % style_params
        )
        import json

        render_params = {
            "version": VDOM_fullcalendar.VERSION,
            "date_mod": VDOM_fullcalendar.DATE_MOD,
            "id_out": id_out,
            "id_woo": id_woo,
            "time_format": timeFormat,
            "short_day_names": json.dumps(short_day_names),
            "day_names": json.dumps(day_names),
            "short_month_names": json.dumps(short_month_names),
            "month_names": json.dumps(month_names),
            "is_editable": editable,
            "is_selectable": selectable,
            "first_day": first_day,
            "default_view": view,
            "is_allday_visible": allday_visible,
            "allday_title": allday_title,
            "minutes_interval": slotminutes,
            "event_sources": self.parse_events(),
            "year": int(default_date[0]),
            "month": int(default_date[1]) - 1,
            "day": int(default_date[2]),
            "window_lazyloading_1": window_lazy,
            "lazyloading_1": lazyloading_1,
            "lazyloading_start": lazyloading_start,
            "lazyloading_end": lazyloading_end,
            "lazy_condition": lazy_condition,
            "lazy_condition_1": lazy_condition_1,
            "first_hour": first_hour,
        }
        # resource = application.resources.get_by_label(self.id, "renderscript")
        # if resource:
        # application.resources.delete(resource.id)
        # res_id = application.resources.create_temporary(self.id, "renderscript", VDOM_fullcalendar.RENDER_SCRIPT % render_params, "js", "renderscript")
        request.dyn_libraries[self.name] = '<script type="text/javascript" >%s</script>' % (VDOM_fullcalendar.RENDER_SCRIPT % render_params,)
        return VDOM_fullcalendar.RENDER_DIV % (id_out, mainstyle)

    def parse_events(self):
        event_sources = []
        if self.events:
            calendar = vobject.readOne(self.events)
            cal_list = []
            for event in calendar.vevent_list:
                startDate = getattr(event, "dtstart", vobject.base.ContentLine("DTSTART", "", str(datetime.date.today())))
                endDate = getattr(event, "dtend", vobject.base.ContentLine("DTEND", "", str(startDate.value)))
                summary = getattr(event, "summary", vobject.base.ContentLine("SUMMARY", "", "Event"))
                cal_list.append([startDate.value, endDate.value, summary.value])
                description = getattr(event, "description", vobject.base.ContentLine("DESCRIPTION", "", "Event"))
                color = getattr(event, "color", vobject.base.ContentLine("COLOR", "", "blue"))
                id = getattr(event, "id", vobject.base.ContentLine("ID", "", "-1"))
                allDay = getattr(event, "allday", vobject.base.ContentLine("ALLDAY", "", "false"))
                allDay = True if allDay.value == "true" else False
                textColor = getattr(event, "textcolor", vobject.base.ContentLine("textColor", "", "green"))
                borderColor = getattr(event, "bordercolor", vobject.base.ContentLine("bordercolor", "", "green"))
                if event.rruleset is None:
                    event_sources.append(
                        {
                            "events": [
                                {
                                    "id": id.value,
                                    "title": (summary.value).replace("&comma&", ","),
                                    "description": description.value,
                                    "start": startDate.value.strftime("%Y-%m-%d %H:%M:%S"),
                                    "end": endDate.value.strftime("%Y-%m-%d %H:%M:%S"),
                                    "allDay": allDay,
                                    "instance": "-1",
                                }
                            ],
                            "color": color.value,
                            "textColor": textColor.value,
                            "borderColor": borderColor.value,
                        }
                    )
                else:
                    instance = 1
                    for rev in event.rruleset:
                        event_sources.append(
                            {
                                "events": [
                                    {
                                        "title": (summary.value).replace("&comma&", ","),
                                        "description": description.value,
                                        "id": id.value,
                                        "start": rev.strftime("%Y-%m-%d %H:%M:%S"),
                                        "end": (rev + relativedelta(endDate.value, startDate.value)).strftime("%Y-%m-%d %H:%M:%S"),
                                        "allDay": allDay,
                                        "instance": instance,
                                    }
                                ],
                                "color": color.value,
                                "textColor": textColor.value,
                                "borderColor": borderColor.value,
                            }
                        )
                        instance += 1
        return json.dumps(event_sources)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        image_id = "5009cfe8-bd06-132e-eeef-a2a5acdc6ee1"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)