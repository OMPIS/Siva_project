import os

def OS_validation():
    os_type = os.popen("uname -a").read().strip().split()[0]
    return os_type

os_name = OS_validation()

def Hardware_details(cmd):
    base_command = "dmidecode -t1"
    regex = "awk -F: '{print $2}'"
    output = os.popen(f"{base_command} | grep {cmd} | {regex}").read().strip()
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
    main_cmd = f"{base_cmd_path} | grep {cmd} | {regex}"
    id_output = os.popen(main_cmd).read().strip()
    unique_ids = list(set(id_output.split()))
    return unique_ids


def DELL_MEGACLI_ERROR_CHECKS(eid, slotid):
    base_cmd_path = f"/opt/MegaRAID/MegaCli/MegaCli64 -PDInfo -PhysDrv[{eid}:{slotid}] -aALL"
    error_counts, regex = ["Media Error Count", "Other Error Count"], "awk -F: '{print $2}'"
    for error_count in error_counts:
        main_cmd = f"{base_cmd_path} | grep '{error_count}' | {regex}"
        validation = int(os.popen(main_cmd).read().strip())
        if validation == 0:
            # print(f"[OK] No issues on the {error_count}; Enclouser ID: {eid}; SlotID: {slotid}")
            pass
        else:
            print(f"[CRITCICAL] Disk having {error_count}; Enclouser ID: {eid}; SlotID: {slotid}")
            hardware_issues = os.popen(f"{base_cmd_path}").read().strip()
            return hardware_issues


def DELL_MEMORY_CHECKS():
    base_cmd = f"omreport chassis memory"
    index_lst, regex = f"{base_cmd} | grep Index", "awk -F: '{print $2}'"
    index_count = os.popen(f"{index_lst} | {regex}").read().strip()
    unique_ids = list(set(index_count.split()))
    for unique_id in unique_ids:
        health_checks = f"{base_cmd} index={unique_id} | grep Health | {regex}"
        print(f"Health checks cmd: {health_checks}")
        index_output = os.popen(health_checks).read().strip()
        memory_check = f"{base_cmd} index={unique_id}"
        if index_output != "Ok":
            print(f"[CRITICAL] Memory Fault Detected for Index {unique_id}")
            fault_id = os.popen(f"{memory_check}").read().strip()
            print(f"{fault_id}")
        else:
            #print(f"[OK] Memory is fine {unique_id}")
            pass



# Basic Varibles
hwd_cmp = {
    "PowerEdge R650": "7.00",
    "PowerEdge R720xd": "2.65",
    "PowerEdge R730xd": "2.80",
    "PowerEdge R740xd": "7.00"
}

manufacture = Hardware_details("Manufacturer")
product = Hardware_details("'Product Name'")
dell_enclouse_ids = DELL_MEGACLI_ID("'Enclosure Device ID'")
dell_slot_ids = DELL_MEGACLI_ID("'Slot Number'")

print(
    f"OS: {os_name}; Manufacture: {manufacture}; DELL Enclouse ID's: {dell_enclouse_ids}; Dell Slot ID's: {dell_slot_ids}")


def Main(os_type, manufacture, product):
    if os_name == os_type:
        if manufacture.startswith(manufacture):
            if product.startswith(product):
                DELL_iDRAC(product, hwd_cmp[product])
                for dell_enclouse_id in dell_enclouse_ids:
                    for dell_slot_id in dell_slot_ids:
                        hardware_ouput = DELL_MEGACLI_ERROR_CHECKS(dell_enclouse_id, dell_slot_id)
                        print(hardware_ouput)

Main("Linux", "Dell", "PowerEdge")
DELL_MEMORY_CHECKS()
