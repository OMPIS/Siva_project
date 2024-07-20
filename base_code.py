import os

def OS_validation():
    os_type = os.popen("uname -a").read().strip().split()[0]
    return os_type


os_name = OS_validation()


def Hardware_details(cmd):
    output = os.popen(f"dmidecode -t1 | grep {cmd}").read().strip()
    return output


manufacture = Hardware_details("Manufacturer | awk -F: '{print $2}'")
product = Hardware_details("Product Name | awk -F: '{print $2}'")


def DELL_iDRAC(version, verion_req):
    idrack_version = os.popen("racadm getversion | grep iDRAC | awk -F= '{print $2}'").read().strip()
    if idrack_version.startswith(verion_req):
        print(f"[OK] iDRAC version under the requirement: {version}: {idrack_version}")
    else:
        print(f"[CRITICAL] iDRAC not under the requirement: {version}: {idrack_version}")


def DELL_MEGACLI_ID(cmd):
    base_cmd_path = "/opt/MegaRAID/MegaCli/MegaCli64 -PDList -aALL"
    regex = "awk -F: '{print $2}'"
    id_output = os.popen(f"{base_cmd_path} | grep {cmd} | {regex}")
    unique_ids = list(set(id_output.split()))
    return unique_ids


if os_name == "Linux":
    if "Dell" in manufacture:
        DELL_iDRAC("PowerEdge R720xd", "2.65")
        DELL_iDRAC("PowerEdge R730xd", "2.80")
        DELL_iDRAC("PowerEdge R740xd", "7.00")
        dell_enclouse_id = DELL_MEGACLI_ID("Enclosure Device ID")
        dell_slot_id = DELL_MEGACLI_ID("Slot Number")
        print(f"Dell slot id: {dell_slot_id}")
        print(f"Dell enclouse id: {dell_slot_id}")
