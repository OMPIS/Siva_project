import os


def OS_validation():
    os_type = os.popen("uname -a").read().strip().split()[0]
    return os_type


os_name = OS_validation()


def Hardware_details(cmd):
    output = os.popen(f"dmidecode -t1 | grep {cmd}").read().strip()
    return output


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

def DELL_MEGACLI_ERROR_CHECKS(eid, slotid):
    base_cmd_path = f"/opt/MegaRAID/MegaCli/ -PDInfo -PhysDrv[{eid}:{slotid}] -aALL"
    error_counts, regex = ["Media Error Count", "Other Error Count"], "awk -F: '{print $2}'"
    for error_count in error_counts:
        validation = os.popen(f"{base_cmd_path} | grep '{error_count}' | {regex}").read().strip()
        print(validation)



#Basic Varibles
hwd_cmp = {
    "PowerEdge R650": "7.00",
    "PowerEdge R720xd": "2.65",
    "PowerEdge R730xd": "2.80",
    "PowerEdge R740xd": "7.00"
}

manufacture = Hardware_details("Manufacturer | awk -F: '{print $2}'")
product = Hardware_details("'Product Name' | awk -F: '{print $2}'")
dell_enclouse_ids = DELL_MEGACLI_ID("'Enclosure Device ID'")
dell_slot_ids = DELL_MEGACLI_ID("'Slot Number'")
print(f"Dell slot id: {dell_slot_ids}")
print(f"Dell enclouse id: {dell_slot_ids}")

# if os_name == "Linux":
#     if "Dell" in manufacture:
#         print(f"OS name: {os_name}")
#         print(f"Manufacture: {manufacture}")
#         if product.startswith("PowerEdge"):
#             DELL_iDRAC(product, hwd_cmp[product])
#             for dell_enclouse_id in dell_enclouse_ids:
#                 for dell_slot_id in dell_slot_ids:
#                     print(f"eid: {dell_enclouse_id}, sid: {dell_slot_id}")
#                     DELL_MEGACLI_ERROR_CHECKS(dell_enclouse_id, dell_slot_id)




