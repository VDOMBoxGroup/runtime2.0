
def send_to_card_and_wait(message, key, timeout=1, delta=0.1):
    if VDOM_CONFIG["PRELICENSE"]:
        return VDOM_CONFIG["PRELICENSE"].get(key[2:])
    else:
        return system_options[key]


def get_system_attribute(part_type_attribute_id):
    return send_to_card_and_wait("getlicense 0 %s" % str(part_type_attribute_id), "0/%s" % str(part_type_attribute_id))
