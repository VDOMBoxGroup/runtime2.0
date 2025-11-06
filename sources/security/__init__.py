from __future__ import absolute_import

from .acl_manager import VDOM_acl_manager
from .user_manager import VDOM_user_manager


create_application	= 1
modify_application	= 2
delete_application	= 3
create_object		= 4
delete_object		= 5
modify_object		= 6
modify_structure	= 7
modify_acl		= 8
inherit			= 9
list_application	= 10
#modify_objects		= 10

all_access = [
	"",
	"Create application",
	"Modify application",
	"Delete application",
	"Create object",
	"Delete object",
	"Modify object",
	"Modify structure",
	"Modify ACL",
	"Inherit",
	"List"
#	"Modify objects inside"
]

access_to_server = [create_application, modify_application, delete_application, modify_acl]
access_to_application = [modify_application, delete_application, list_application, create_object, modify_object, delete_object, modify_structure, modify_acl, inherit]
access_to_container_object = [create_object, delete_object, modify_object, modify_acl, inherit]
access_to_simple_object = [delete_object, modify_object, modify_acl]
