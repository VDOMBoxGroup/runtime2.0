import json

class VDOM_smartfolder(VDOM_object):

    def render(self, contents=""):

        woid = u"" + (self.id).replace('-', '_')
        id = u"o_" + woid

        display = u"display:none;" if self.visible == "0" else u""

        # classname = u"""class="%s" """ % self.classname if self.classname else u""
        classname_item = 'sf-item'

        style_zindex = u"z-index:%s;" % self.zindex if int(self.zindex) != 0 else u""

        #style = u"""{display} {zind} position: {pos}; top: {top}px; left: {left}px; width: {width}px; height: {height}px; """\
        style = u"""{display} {zind} position: {pos}; top: {top}px; left: {left}px;"""\
            .format( display = display, zind = style_zindex, pos = self.position, 
                top = self.top, left = self.left)

        html_items = u""
        js_items_data = u""

        ### parse localization

        localization_default = {
            "button_edit":       "<img src='/fe305baa-4007-8454-be19-15f53fd82d22.res'>",
            "button_add":        "Add Smart Folder",
            "button_delete":     "Delete",
            "button_group":      "Group",
            "button_ungroup":    "Ungroup",
            "button_select":     "Select",
            "button_selectall":  "Select All",
            "button_selectnone": "Select None",
            "button_rules":      "Rules",
            "msg_1":             "Please enter name for new folder:",
            "msg_2":             "New Folder",
            "msg_3":             "Folder name is empty",
            "msg_4":             "Not allowed in select mode",
            "msg_5":             "No folder selected",
            "msg_6":             "Please enter new name:",
            "msg_7":             "Please enter name for new group:",
            "msg_8":             "New Group",
            "msg_9":             "Group name is empty",
            "msg_10":            "No items selected",
            "msg_11":            "Group is not specified",
            "msg_12":            "Sure delete?"
        }

        try:
            localization_user = json.loads(self.localization)
            localization = dict(localization_default, **localization_user)
        except Exception as e:
            localization = localization_default
            debug("Error [json.loads(localization) in smartfolder type]: %s" % str(e))

        ### javascript

        #if self.draggable == '1':
        #	js_drag = u"""
        #		vdom_sf_set_dnd('%(id)s', '%(woid)s', '%(class)s');
        #		""" % { "id": id, "woid": woid, "class": classname_item }
        #else:
        js_drag = ""

        js_base = u"""
$j('#%(id)s')
    %(js_items_data)s
;
$j("#%(id)s .items .%(class)s").bind('click dblclick', function(e){
    if (e.preventDefault) e.preventDefault(); else e.returnValue = false;
    var t = $j(this);
    if (e.type == 'dblclick') {
        %(id)s_doo = false;
        execEventBinded('%(woid)s', "itemdblclick", {"id":t.attr("index")});
    } else {
        setTimeout(function() {
            if (%(id)s_doo == true) {

var sfo = $j('#%(id)s'), x = sfo.data("sf"), i = $j(this).attr('index');
%(id)s_current_item = x[i];
$j('>.%(class)s', sfo).removeClass('selected');
$j(this).addClass('selected');


                execEventBinded('%(woid)s', "itemclick", {"id":t.attr("index")});
            }
        }, 250);
        %(id)s_doo = true;
    }
    return false;
});
$j("#%(id)s .items .%(class)s").hover(function(e){
    execEventBinded('%(woid)s', "itemmouseover", {"id":$j(this).attr("index")});
    return false;
},function(e){
    execEventBinded('%(woid)s', "itemmouseout", {"id":$j(this).attr("index")});
    return false;
});
""" % { "id": id, "woid": woid, "class": classname_item, "js_items_data": js_items_data }

        if self.testhtml != '':
            js_drag = ""
            js_add = ""
            testhtml = self.testhtml % { "id": id, "woid": woid, "class": classname_item }
        else:
            testhtml = ""
            js_add = u"""
/* // it in click, see upper
$j("#%(id)s .items .%(class)s").click(function(){
    var x = $j('#%(id)s').data("sf"), i = $j(this).attr('index');
    %(id)s_current_item = x[i];
    $j('#%(id)s>.%(class)s').removeClass('selected');
    $j(this).addClass('selected');
});
*/
/*
$j("#%(id)s>.controls div.control").click(function(){
    var t = $j(this);
    if (t.hasClass('add')) {
        var n = '';
        execEventBinded('%(woid)s', "newsmartfolder", {"name": n}, true);
    } else
    if (t.hasClass('edit')) {
        execEventBinded('%(woid)s', "rename", {}, true);
    } else
    if (t.hasClass('delete')) {
        var x = [];
        execEventBinded('%(woid)s', "delete", {"guids": x}, true);
    } else
    if (t.hasClass('group')) {
        var x = [], n = '';
        execEventBinded('%(woid)s', "group", {"groupname": n, "guids": x}, true);
    } else
    if (t.hasClass('ungroup')) {
        execEventBinded('%(woid)s', "ungroup", {}, true);
    }
    return false;
});
*/

$j("#%(id)s .controls .control, #%(id)s .item-panel .control, #%(id)s .item-panel a.edit").click(function(){
    var t = $j(this), sf = $j("#%(id)s");
    if (t.hasClass('add')) {
            execEventBinded('%(woid)s', "newsmartfolder", {"name": "%(msg_2)s"}, true);
    } else
    if (t.hasClass('edit')) {
            var o = sf.data('sf_current_item') || false;
            var arguments = o? {"guid": o.data('sf').guid, "name": o.data('sf').name}: {};
            execEventBinded('%(woid)s', "rename", arguments, true);

    } else
    if (t.hasClass('delete')) {
            var x = sf.data('sf_items_selected') || [];
            var arguments = {};
            if (x.length) {
                arguments = {"guidlist": x};
            } else {
                var o = sf.data('sf_current_item') || false;
                if (o) {
                    arguments = {"guidlist": [o.data('sf').guid]};
                }
            }
            execEventBinded('%(woid)s', "delete", arguments, true);
    } else
    if (t.hasClass('group')) {
        var x = sf.data('sf_items_selected') || [];
        execEventBinded('%(woid)s', "group", {"name": "%(msg_8)s", "guidlist": x}, true);
    } else
    if (t.hasClass('ungroup')) {

            var x = sf.data('sf_current_item') || [];
            var arguments = x.length? {"guid": x.data('sf').guid}: {};
            execEventBinded('%(woid)s', "ungroup", arguments, true);

    } else
    if (t.hasClass('rules')) {
        var x = sf.data('sf_items_selected') || [];
        if (x.length) {
            execEventBinded('%(woid)s', "rules", {"guidlist": x}, true);
        } else {
            var o = sf.data('sf_current_item') || false;
            if (o) {
                execEventBinded('%(woid)s', "rules", {"guidlist": [o.data('sf').guid]}, true);
            }
        }
    } else
    if (t.hasClass('select')) {
        $j('.sub', this).show(0);
    } else
    if (t.hasClass('selectall')) {
        var s = 'selected', sc = 'current';
        var ss = $j("#%(id)s .items .%(class)s:not(.noselect)");

        $j.each(ss, function(i, x){
            vdom_sf_selected_add(sf, $(x).attr('index'));
        });

        var t = sf.find('.sf-item');
        if (t.length == 1) sf.data('sf_current_item', t);
        t.addClass(s);
        t.addClass(sc);
        sf.addClass('has-current');

        vdom_sf_check_selected(sf);
        vdom_sf_check_panel(sf);


    } else
    if (t.hasClass('selectnone')) {
        vdom_sf_selected_remove_all(sf);
    }
    return false;
});

$j("#%(id)s .controls .select .sub").mouseleave(function(){
    $(this).hide(0);
});

$j("#%(id)s .controls .select .sub div").hover(function(){
    $(this).addClass('hovered');
},function(){
    $(this).removeClass('hovered');
});

$j("#%(id)s .items-wrap").click(function(){
    vdom_sf_selected_remove_all($j("#%(id)s"));
    return false;
});

$j("#%(id)s .controls .selectmode").click(function(){
    var t = $j(this), s = 'selectmode-selected', sf = $j("#%(id)s");
    if (t.hasClass(s)) {
        $j(sf).data({
            'sf_selectmode': 0,
            'sf_items_selected': []
        });
        $j(".items .%(class)s",sf).removeClass('selected').droppable('enable').draggable('enable');
        t.removeClass(s);
        $j(".items",sf).removeClass('selectmode');
    } else {
        $j(sf).data('sf_selectmode', 1);
        $j(".items .%(class)s",sf).droppable('disable').draggable('disable');
        var x = $j(".items .selected:first",sf).data('sf');
        if (typeof x !== 'undefined' && typeof x.guid !== 'undefined') vdom_sf_selected_add(sf, x.guid);
        t.addClass(s);
        $j(".items",sf).addClass('selectmode');
    }
    return false;
});

vdom_sf_init('%(id)s');

""" % {
            "msg_1":  localization['msg_1'],
            "msg_2":  localization['msg_2'],
            "msg_3":  localization['msg_3'],
            "msg_4":  localization['msg_4'],
            "msg_5":  localization['msg_5'],
            "msg_6":  localization['msg_6'],
            "msg_7":  localization['msg_7'],
            "msg_8":  localization['msg_8'],
            "msg_9":  localization['msg_9'],
            "msg_10": localization['msg_10'],
            "msg_11": localization['msg_11'],
            "msg_12": localization['msg_12'],
            "id":     id,
            "woid":   woid,
            "class":  classname_item }


        ### consolidate javascript

        js = u"""<script type="text/javascript">
%(id)s_doo = false;
%(id)s_current_item = null;

function vdom_sf_set_drag(sf) {
    vdom_sf_set_dnd(sf.attr('id'), '%(woid)s', '%(class)s');
}

function vdom_sf_check_panel(sf, t=null) {
    var pan = $j('.item-panel', sf);
    // if (vdom_sf_selected_count(sf) == 1 || sf.find('.has-current').length == 1)
    if (vdom_sf_selected_count(sf) == 1) {
        $j('.title-wrap', pan).show(0);
        $j('.info', pan).show(0);
        $j('.metas', pan).show(0);
        $j('.buttons .group', pan).hide(0);
        t = t || sf.find('.sf-item');
        if (t.hasClass('group')) {
            $j('.buttons .ungroup', pan).show(0);
        } else {
            $j('.buttons .ungroup', pan).hide(0);
        }
        set_panel_data(sf, t);


        pan.show(0);
    // } else if (vdom_sf_selected_count(sf) == 0 || sf.find('.has-current').length == 0)
    } else if (vdom_sf_selected_count(sf) > 1) {
        $j('.title-wrap', pan).hide(0);
        $j('.info', pan).hide(0);
        $j('.metas', pan).hide(0);
        $j('.buttons .ungroup', pan).hide(0);
        $j('.buttons .group', pan).show(0);
        pan.show(0);
    } else {
        $j('.item-panel', sf).hide(0);
        }
}


function set_panel_data(sf, t){
    if ($j('.%(class)s.'+'current', sf).length > 0) {
        sf.addClass('has-current');

        // set info for current item
        var d = t.data('sf');
        var pan = $j('.item-panel', sf);
        pan.removeClass('group folder');
        if (t.hasClass('group')) pan.addClass('group'); else pan.addClass('folder');

        $j('.title-wrap>.title', pan).text(d['name']);
        $j('>.info', pan).text(d['info']);
        var s = '';
        $j.each(d['metas'], function(index, meta){
            s += '<span class="metas type-'+ meta['type']+'"><b>'+meta['title']+'</b> '+ meta['value'] +'</span>'
        });
        $j('>.metas', pan).html(s);

    } else {
        sf.removeClass('has-current');
    }
}
function vdom_sf_set_handlers(sfid){
    vdom_sf_set_drag(sfid);

    %(id)s_doo = false;
    //$j(".items .%(class)s",sfid).on('click dblclick', function(e){
    $j(".items .%(class)s",sfid).bind('click dblclick', function(e){
        if (e.preventDefault) e.preventDefault(); else e.returnValue = false;
        var t = $j(this);
        var x = t.data("sf");
        if (e.type == 'dblclick') {
            %(id)s_doo = false;
            execEventBinded('%(woid)s', "itemdblclick", {"guid":x.guid});
        } else {
            setTimeout(function() {
                if (%(id)s_doo == true) {
                    // click
                    //execEventBinded('%(woid)s', "itemclick", {"id":t.attr("dataid")});
                    var s = 'selected', sc = 'current', sa;

                    var prev = $j(sfid.data('sf_current_item'));
                    var x_prev = prev.data("sf");

                    if (e.ctrlKey) {
                        if (x.noselect !== '1') {
                            if (t.hasClass(s)) {
                                t.removeClass(s);
                                vdom_sf_selected_remove(sfid, x.guid);
                            } else {
                                t.addClass(s);
                                vdom_sf_selected_add(sfid, x.guid);
                                //$j(sfid.data('sf_current_item')).addClass(s);
                                //vdom_sf_selected_add(sfid, $j(sfid.data('sf_current_item')).data('sf').guid);
                            }
                        } else {
                            t.stop().css("opacity", 0).animate({ opacity: 1 }, 1000);
                        }

                        if (!prev.data('first_selected')) {
                            if (!!x_prev) {
                                if (x_prev.noselect !== '1') {
                                    prev.addClass(s);
                                    vdom_sf_selected_add(sfid, x_prev.guid);
                                }
                            }
                        }
                        //x_prev.first_selected = true;
                        prev.data('first_selected', true)
                    }
                    else {
                        prev.data('first_selected', false);
                        vdom_sf_selected_remove_all(sfid);
                        vdom_sf_selected_add(sfid, x.guid);
                    }

                    sfid.data('sf_current_item', t);
                    t.parents('.items').find('.sf-item').removeClass(sc);
                    t.addClass(sc); t.addClass(s);

                    if ($j('.%(class)s.'+sc, sfid).length > 0) {
                        sfid.addClass('has-current');

                        // set info for current item
                        var d = t.data('sf');
                        var pan = $j('.item-panel', sfid);

                        pan.removeClass('group folder');
                        if (t.hasClass('group')) pan.addClass('group'); else pan.addClass('folder');

                        $j('.title-wrap>.title', pan).text(d['name']);
                        $j('>.info', pan).text(d['info']);
                        var s = '';
                        $j.each(d['metas'], function(index, meta){
                            s += '<span class="metas type-'+ meta['type']+'"><b>'+meta['title']+'</b> '+ meta['value'] +'</span>'
                        });
                        $j('>.metas', pan).html(s);
                    } else {
                        sfid.removeClass('has-current');
                    }

                    /*
                    if (sfid.data('sf_selectmode') == 0) {
                        sfid.data('sf_current_item', t);

                        t.parents('.items').find('.sf-item').removeClass(sc);
                        t.addClass(sc);

                        set_panel_data(sfid, t);

                    } else {
                        if (x.noselect !== '1') {
                            if (t.hasClass(s)) {
                                t.removeClass(s);
                                vdom_sf_selected_remove(sfid, x.guid);
                            } else {
                                t.addClass(s);
                                vdom_sf_selected_add(sfid, x.guid);
                            }
                        }
                    }
                    */


                    if (t.data('forselect') !== false) {
                        t.data('forselect').addClass('selected');
                        t.data('forselect', false);
                    }
                    vdom_sf_check_selected(sfid);
                    vdom_sf_check_panel(sfid, t);
                }
            }, 250);
            %(id)s_doo = true;
        }
        return false;
    });


    //$j(".pathway a",sfid).on('click',function(){
    $j(".pathway a",sfid).bind('click',function(){
        execEventBinded('%(woid)s', "pathclick", {"guid": $j(this).attr('guid')}, true);
        return false;
    });

}

function vdom_sf_check_selected(sf) {
    //sf.find(".controls .control.select span.count").text( $j(sf.data('sf_items_selected')).length );
    sf.find(".controls .control.select span.count").text( sf.find(".items-wrap .items>.selected").length );
}

function vdom_sf_selected_add(sf, guid){
    var sa = sf.data('sf_items_selected');
    var x = $j.inArray(guid, sa);
    if (x < 0) {
        sa.push(guid);
        sf.data('sf_items_selected', sa);
        vdom_sf_check_selected(sf);
    }
}

function vdom_sf_selected_remove(sf, guid){
    var sa = sf.data('sf_items_selected');
    var x = $j.inArray(guid, sa);
    if (x >= 0) {
        sa.splice(x,1);
        sf.data('sf_items_selected', sa);
        vdom_sf_check_selected(sf);
    }
}

function vdom_sf_selected_remove_all(sf){
    $j(".items .%(class)s", sf).removeClass('selected');
    $j(".items .%(class)s", sf).removeClass('current');
    sf.data('sf_items_selected', []);
    vdom_sf_check_selected(sf);
    $j('.item-panel', sf).hide(0);
}

function vdom_sf_selected_count(sf){
    return $j(sf.data('sf_items_selected')).length;
}

function vdom_sf_refresh(sfid){
    var sf = $j('#'+sfid);
    var p = sf.data('sf_path') || [], guid = '', ofs = 0;
    if (p.length) {
        guid = p[p.length-1];
    }
    sf.data('sf_current_item', null);
    vdom_sf_check_selected(sf);
    execEventBinded('%(woid)s', "requestdata", {"guid": guid}, true);
}


function vdom_sf_goto(path){
    execEventBinded('%(woid)s', "requestdata", {"guid": ''}, true);
}

function vdom_sf_disable(id){
    $j('#'+id+' .sf-disabled').fadeIn('fast');
}

function vdom_sf_enable(id){
    $j('#'+id+' .sf-disabled').fadeOut('fast');
}

function vdom_sf_load(id, path, total, data){
    var sf = $j('#'+id);
    sf.data('sf_path', path);
    sf.data('sf_items_count', total);
    sf.data('sf_current_item', null);

    vdom_sf_selected_remove_all(sf);
    sf.removeClass('has-current');
    $j(' .items .current', sf).removeClass('current');
    $j('.item-panel', sf).removeClass('group folder');

    if (typeof data === 'string') data = JSON.parse(data);
    if (typeof data === 'array' || typeof data === 'object') {
        var d = $j('<div></div>');
        $j.each(data, function(i,e){
            var a = {
                guid:      e['guid'] || 'no-guid',
                type:      e['type'] || 'no-type',
                name:      e['name'] || 'no-name',
                icon:      e['icon'] || '',
                nodelete:  e['nodelete'] || '',
                noedit:    e['noedit'] || '',
                nomove:    e['nomove'] || '',
                noselect:  e['noselect'] || '',
                info:      e['info'] || '',
                metas:     e['metas'] || []
            };
            if (typeof a['metas'] === 'string') a['metas'] = [JSON.parse(a['metas'])];

            var s = $j( '<div class="sf-item" index="'+a['guid']+'"><div class="img"><div></div></div><div class="name">'+a['name']+'</div><div class="type-'+a['type']+'"></div></div>' );
            if (a['nomove'] == '1') s.append('<div class="sf-item"><div class="name">'+a['name']+'</div><div class="type-'+a['type']+'"></div></div>' );
            if (a['nomove'] == '1') s.addClass('nomove');
            if (a['nodelete'] == '1') s.addClass('nodelete');
            if (a['noedit'] == '1') s.addClass('noedit');
            if (a['noselect'] == '1') s.addClass('noselect');
            if (a['type'] == 'group') s.addClass('group');
            //if (sf.data('sf_items_selected').indexOf(e['guid']) >= 0) s.addClass('selected');
            if ( $j.inArray(e['guid'], sf.data('sf_items_selected')) >= 0 ) s.addClass('selected');
            s.appendTo(d).data({
                'sf': a,
                'forselect': false
            });
        });
    }
    $j('.items',sf).html('').append($j('>div',d));

    d = [];
    if (typeof path === 'string') path = JSON.parse(path);
    if (typeof path === 'array' || typeof path === 'object') {
        $.each(path, function(i,e){
            if (i < path.length - 1) {
                d.push("<a href='#' guid='"+e['guid']+"'>"+e['name']+"</a>");
            } else {
                d.push("<span guid='"+e['guid']+"'>"+e['name']+"</span>");
            }
        });
    }
    $j('.pathway',sf).html(d.join(' &rsaquo; '));

    vdom_sf_check_selected(sf);

    vdom_sf_set_handlers(sf);
    //vdom_sf_set_drag(sf);
}

function vdom_sf_init(id,sel){
    var sf=$j('#'+id);
    sf.data({
        'sf_current_item': null,
        'sf_items_count': 0,
        'sf_items_selected': sel || []
    }).find('.items').html('');
    $j('.sf-disabled',sf).css({
        opacity: 0.7,
        width: '100%%',
        height: '100%%'
    });
    vdom_sf_set_handlers(sf);
}

$j(function(){
    %(js_base)s
    %(js_drag)s
    %(js_add)s
    execEventBinded('%(woid)s', "requestdata", {guid:''}, true);
});
</script>""" % { 
                "id":      id,
                "woid":    woid, 
                "js_drag": js_drag,
                "class":   classname_item, 
                "js_base": js_base, 
                "js_add":  js_add
            }

        ### styles

        css = u"""<style type='text/css'>
#%(id)s {
    background: #999;
    border: 1px solid #888;
    border-left: 1px solid #ddd;
    border-top: 1px solid #ddd;
    padding: 1px;
    width: %(width)spx;
}

#%(id)s .items-wrap {
    overflow: auto;
    background: #fff;
}
#%(id)s.has-current .items,
#%(id)s.has-current .items-wrap {
    height: %(height2)spx;
}

#%(id)s .item-panel {
    display: none;
    width: %(width)spx;
    height: 100px;
    overflow: hidden;
    background: #eee;
}
#%(id)s.has-current .item-panel {
    display: block;
    overflow: auto;
}
    #%(id)s .item-panel .title-wrap {
        padding: 4px;
        float: left;
    }
    #%(id)s .item-panel .title-wrap .title {
        font-size: 16px;
    }
    #%(id)s .item-panel .edit {
        margin: 2px;
        cursor: pointer;
    }
    #%(id)s .item-panel .buttons {
        float: right;
        padding: 2px;
    }

    #%(id)s .item-panel.folder,
    #%(id)s .item-panel.group {
        display: block;
    }

    #%(id)s .item-panel.folder .control.group,
    #%(id)s .item-panel.folder .control.ungroup,
    #%(id)s .item-panel.group .control.group {
        display: none;
    }

    #%(id)s .item-panel .info {
        clear: both;
        padding: 4px 4px 6px 4px;
    }

    #%(id)s .item-panel .metas span {
        background: #fff;
    border: 1px solid #BBBBBB;
    border-radius: 2px 2px 2px 2px;
    color: #000000;
    float: left;
    margin: 0 0 2px 2px;
    padding: 1px 4px 2px;
        font-size: 90%%;
    }
    #%(id)s .item-panel .metas b {
        color: #777;
        font-weight: normal;
    }

#%(id)s .items {
    height: %(height)spx;
    overflow: visible;
}
    #%(id)s .items .%(class)s {
        overflow: hidden; 
        width: %(itemwidth)spx;
        height: %(itemheight)spx;
        float: left;
        margin: 1px;
        border: 1px solid #fff;
        background: #fff;
        text-align: center;
        word-wrap: break-word;
    }
    #%(id)s .items .%(class)s-hover {
    }
        #%(id)s .items .%(class)s .img {
            width: 82px;
            height: 63px;
            overflow: hidden;
            margin: 0 auto 5px auto;
            background: url('/af216e40-488c-0e26-55ba-ef5e3778e9ff.res') center center no-repeat;
            position: relative;
        }
        #%(id)s .items .%(class)s .img div {
            position: absolute;
            left: 0;
            top: 0;
            width: 82px;
            height: 63px;
            overflow: hidden;
            margin: 0;
        }
        #%(id)s .items .selected .img div {
        }
        #%(id)s .items .%(class)s.group .img {
            background: url('/3c902e87-ac83-8708-63aa-ef5e42113d92.res') center center no-repeat;
        }
        #%(id)s .items .%(class)s.group .img div {
        }

#%(id)s .items .selected {
    color: #fff;
    background: #8ac;
}
#%(id)s .items .current {
    border: 1px dotted #333;
}

#%(id)s .items .%(class)s-hover {
    border-color: lime;
    -webkit-box-shadow: 0 0 4px green;
    -moz-box-shadow: 0 0 4px green;
    box-shadow: 0 0 4px green;
}
#%(id)s .pathway {
    padding: 4px 2px 6px 4px;
    color: #fff;
}
    #%(id)s .pathway a {
        color: #eee;
    }
    #%(id)s .pathway a:hover {
        color: #fff;
    }

#%(id)s .controls {
    padding: 1px;
}
    #%(id)s .item-panel .control,
    #%(id)s .controls .control {
        float: left;
        white-space: nowrap;
        cursor: pointer;
        background: #eee;
        border: 1px solid #666;
        border-left: 1px solid #ccc;
        border-top: 1px solid #ccc;
        padding: 4px 8px;
        margin: 0 3px 0 0;
        color: #555;
        /*box-shadow: 1px 1px 2px #333;*/
        -webkit-box-shadow: 1px 1px 5px -2px #333333
        -moz-box-shadow: 1px 1px 5px -2px #333333
        box-shadow: 1px 1px 5px -2px #333333
    }
    #%(id)s .item-panel .control:hover,
    #%(id)s .controls .control:hover {
        background: #fff;
        color: #000;
    }
    #%(id)s .item-panel .control:active,
    #%(id)s .controls .control:active {
        background: #fcc;
        -webkit-box-shadow: none;
        -moz-box-shadow: none;
        box-shadow: none;
        margin: 1px 2px -1px 1px;
    }

#%(id)s .select {
    position: relative;
    overflow: visible;
    z-index: 999;
}
    #%(id)s .select .sub {
        display: none;
        position: absolute;
        top: 0;
        left: 0;
        padding: 6px;
        border: 1px solid #ddd;
        overflow: hidden;
        background: #fff;
        -webkit-box-shadow: 4px 4px 8px rgba(0,0,0,0.5);
        -moz-box-shadow: 4px 4px 8px rgba(0,0,0,0.5);
        box-shadow: 4px 4px 8px rgba(0,0,0,0.5);
    }
    #%(id)s .select .sub:active {
        margin: 0;
    }
        #%(id)s .select .sub div {
            background: #fff;
            border: none;
            cursor: pointer;
            -webkit-box-shadow: none;
            -moz-box-shadow: none;
            box-shadow: none;
        }
        #%(id)s .select .sub .hovered {
            background: #eee;
        }

#%(id)s .sf-disabled {
    background: #fff;
    position: absolute;
    left: 0;
    top: 0;
}
#%(id)s .ui-state-disabled {
    opacity: 1;
}

</style>""" % {
            "id": id, "class": classname_item,
            "itemwidth": self.itemwidth, "itemheight": self.itemheight,
            "width": self.width,
            "height": self.height,
            "height2": int(self.height) - 100
        }

        ### parse settings

        tb_opt = {
                "show": 1,
                "buttons": {
                    "edit": {
                        "show": 1
                    },
                    "add": {
                        "show": 1
                    },
                    "delete": {
                        "show": 1
                    },
                    "group": {
                        "show": 1
                    },
                    "ungroup": {
                        "show": 1
                    }
                }
            }

        """
        if 'buttons' in tb_opt:
            b = tb_opt['buttons']
            tb_opt_b_edit          = int(b['edit']['show']) if 'edit' in b else 1
            tb_opt_b_add           = int(b['add']['show']) if 'add' in b else 1
            tb_opt_b_delete        = int(b['delete']['show']) if 'delete' in b else 1
            tb_opt_b_group         = int(b['group']['show']) if 'group' in b else 1
            tb_opt_b_ungroup       = int(b['ungroup']['show']) if 'ungroup' in b else 1
            tb_opt_b_edit_title    = b['edit']['title'] if 'edit' in b else 'Edit'
            tb_opt_b_add_title     = b['add']['title'] if 'add' in b else 'Add Smart Folder'
            tb_opt_b_delete_title  = b['delete']['title'] if 'delete' in b else 'Delete'
            tb_opt_b_group_title   = b['group']['title'] if 'group' in b else 'Group'
            tb_opt_b_ungroup_title = b['ungroup']['title'] if 'ungroup' in b else 'Ungroup'
        else:
        """
        tb_opt_b_edit = 1
        tb_opt_b_add = 1
        tb_opt_b_delete = 1
        tb_opt_b_group = 1
        tb_opt_b_ungroup = 1
        tb_opt_b_edit_title = u'Edit'
        tb_opt_b_add_title = u'Add Smart Folder'
        tb_opt_b_delete_title = u'Delete'
        tb_opt_b_group_title = u'Group'
        tb_opt_b_ungroup_title = u'Ungroup'

        tb_opt_show = int(tb_opt['show']) if "show" in tb_opt else 1

        # shide = u"style='display:none'"

        toolbar = u"""
            <div class='controls' %(chide)s>
                <div class='control add'><span class='icon'></span><span class='label'>%(button_add)s</span></div>
                <div class='control select'>
                    <span class='count'></span>
                    <span class='title'>%(button_select)s</span>
                    <div class='sub'>
                        <div class='control selectall'><span class='icon'></span><span class='label'>%(button_selectall)s</span></div>
                        <div class='control selectnone'><span class='icon'></span><span class='label'>%(button_selectnone)s</span></div>
                    </div>
                </div>
                <div style='clear:both'></div>
        </div>
        """ % {
            "chide":                  "",# if self.toolbar == "1" else shide,
            #"button_add_hide":        "" if tb_opt_b_add == 1 else shide,
            "button_add":             localization['button_add'],
            "button_select":          localization['button_select'],
            "button_selectall":       localization['button_selectall'],
            "button_selectnone":      localization['button_selectnone'],
            # "id":     id,
            # "class":  classname_item
        }

        ### pathway

        pathway_visible = u"style='display:none'" if self.pathway == "0" else u""
        pathway = u"<div class='pathway' " + pathway_visible + "></div>"

        ### debug info

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = u"objtype='smartfolder' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = u""

        ### out

        result = u"""
            {css}
            <div {debug_info} id="{id}" style="{style}">
                {toolbar}
                {pathway}
                <div class='items-wrap'>
                    <div class='items'>{items}</div>
                    <div class='sf-disabled' style='display:none'></div>
                </div>
                <div class='item-panel'>
                    <div class='buttons'>
                        <a class='control group'><span class='icon'></span><span class='label'>{button_group}</span></a>
                        <a class='control ungroup'><span class='icon'></span><span class='label'>{button_ungroup}</span></a>
                        <a class='control rules'><span class='icon'></span><span class='label'>{button_rules}</span></a>
                        <a class='control delete'><span class='icon'></span><span class='label'>{button_delete}</span></a>
                    </div>
                    <span class='title-wrap'>
                        <span class='title'></span>
                        <a class='edit'>{button_edit}</a>
                    </span>
                    <div class='info'></div>
                    <div class='metas'></div>
                </div>
            </div>
            {js}
            {testhtml}
            """.format(

                    button_edit = localization['button_edit'],
                    button_delete = localization['button_delete'],
                    button_group = localization['button_group'],
                    button_ungroup = localization['button_ungroup'],
                    button_rules = localization['button_rules'],

                    debug_info = debug_info, 
                    id = id, 
                    style = style, 
                    items = html_items, 
                    js = js, 
                    css = css, 
                    testhtml = testhtml, 
                    toolbar = toolbar, 
                    pathway = pathway )

        return VDOM_object.render(self, contents=result)


    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value
        
        image_id = "24e377d1-e9e2-f6ff-bb5a-16e4230f3b50"
        result = get_empty_wysiwyg_value(self, image_id)
        
        return VDOM_object.wysiwyg(self, contents=result)


# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    css = """
#%(id)s {
}
#%(id)s .items {
}
#%(id)s .items .%(class)s {
}
#%(id)s .items .%(class)s-hover {
}
#%(id)s .controls {
}
    #%(id)s .controls .control {
    }
    #%(id)s .controls .control {
    }
    #%(id)s .controls .control:hover {
    }
    #%(id)s .controls .control:active {
    }
"""

    # o = application.objects.search(object_id)
    o = object

    # if "skin" in param:
    if "skin" in attributes:
        # if param["skin"]["value"] == "1":
        if attributes["skin"] == "1":
            # o.set_attributes({"style": css})
            attributes.update(style=css)
        # # elif param["skin"]["value"] == "2":
        # elif attributes["skin"] == "2":
        # #	o.set_attributes({"style": eof_style})
        # o.attributes.update(style=eof_style)
    # if "style" in param and param["style"]["value"] and o.attributes.style != css:
    if "style" in attributes and attributes["style"] and o.attributes["style"] != css:
        # o.set_attributes({"skin": 0})
        attributes.update(skin="0")

    return ""