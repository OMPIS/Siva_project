#!/usr/bin/python3

import os, paramiko, re


def Session(cmd):
    global ssh
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
    ssh.connect("10.89.161.153", username="root", timeout=15)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    remote_output = stdout.read().decode().strip()
    return remote_output
    # usage = re.search('\d+%', output).group()
    # var.append(int(re.search('\d+', usage).group()))


def OS_validation():
    cmd = "uname -a"
    #os_type = os.popen("uname -a").read().strip().split()[0]
    os_type = Session(cmd).split()[0]
    return os_type


os_name = OS_validation()


def Hardware_details(cmd):
    base_command = "dmidecode -t1"
    regex = "awk -F: '{print $2}'"
    cmd = f"{base_command} | grep {cmd} | {regex}"
    # output = os.popen(f"{base_command} | grep {cmd} | {regex}").read().strip()
    output = Session(cmd)
    return output


def DELL_iDRAC(version, verion_req):
    cmd = "racadm getversion | grep iDRAC | awk -F= '{print $2}'"
    # idrack_version = os.popen("racadm getversion | grep iDRAC | awk -F= '{print $2}'").read().strip()
    idrack_version = Session(cmd)
    if idrack_version.startswith(verion_req):
        print(f"[OK] iDRAC version under the requirement: {version}: {idrack_version}")
    else:
        print(f"[CRITICAL] iDRAC not under the requirement: {version}: {idrack_version}")


def DELL_MEGACLI_ID(cmd):
    base_cmd_path = "/opt/MegaRAID/MegaCli/MegaCli64 -PDList -aALL"
    regex = "awk -F: '{print $2}'"
    main_cmd = f"{base_cmd_path} | grep {cmd} | {regex}"
    id_output = Session(main_cmd)
    # id_output = os.popen(main_cmd).read().strip()
    unique_ids = list(set(id_output.split()))
    return unique_ids


def DELL_MEGACLI_ERROR_CHECKS(eid, slotid):  # This
    base_cmd_path = f"/opt/MegaRAID/MegaCli/MegaCli64 -PDInfo -PhysDrv[{eid}:{slotid}] -aALL"
    error_counts, regex = ["Media Error Count", "Other Error Count"], "awk -F: '{print $2}'"
    for error_count in error_counts:
        main_cmd = f"{base_cmd_path} | grep '{error_count}' | {regex}"
        # validations = [os.popen(main_cmd).read().strip()]
        validations = [Session(main_cmd)]
        for validation in validations:
            if validation == '0':
                # print(f"[OK] No issues on the {error_count}; Enclouser ID: {eid}; SlotID: {slotid}")
                pass
            else:
                print(f"[CRITCICAL] Disk having {error_count}; Enclouser ID: {eid}; SlotID: {slotid}")
                cmd = f"{base_cmd_path}"
                # hardware_issues = os.popen(f"{base_cmd_path}").read().strip()
                hardware_issues = Session(cmd)
                return hardware_issues
    if all(validation == '0' for validation in validations): print(f"[OK] All Disk slots are working fine.")


def DELL_MEMORY_CHECKS(component):
    if component is 'memory':
        frame, grep_char1, grep_char2 = 'chassis', 'Index', 'Index'
    if component is 'controller':
        frame, grep_char1, grep_char2 = 'storage', 'ID', 'controller'
    base_cmd = f"omreport {frame} {component}"
    index_lst, regex = f"{base_cmd} | grep ^{grep_char1}", "awk -F: '{print $2}'"
    index_count = os.popen(f"{index_lst} | {regex}").read().strip()
    unique_ids = list(set(index_count.split()))
    for unique_id in unique_ids:
        health_checks = f"{base_cmd} {grep_char2}={unique_id} | grep ^Status | {regex}"
        index_output = os.popen(health_checks).read().strip().split()
        final_check = f"{base_cmd} {grep_char2}={unique_id}"
        for index in index_output:
            if index != "Ok":
                print(f"[CRITICAL] {component} Fault Detected for {grep_char2}: {unique_id}")
                fault_id = os.popen(f"{final_check}").read().strip()
            else:
                pass
    if all(index == "Ok" for index in index_output): print(f"[OK] All {component} slots are working fine.")


# Basic Varibles
hwd_cmp = {
    "PowerEdge R650": "7.00",
    "PowerEdge R720xd": "2.65",
    "PowerEdge R730xd": "2.80",
    "PowerEdge R740xd": "7.00"
}

manufacture = Hardware_details("Manufacturer")
product_name = Hardware_details("'Product Name'")
dell_enclouse_ids = DELL_MEGACLI_ID("'Enclosure Device ID'")
dell_slot_ids = DELL_MEGACLI_ID("'Slot Number'")

# print(
#     f"OS: {os_name}; Manufacture: {manufacture}; Product: {product_name}; DELL Enclouse ID's: {dell_enclouse_ids}; Dell Slot ID's: {dell_slot_ids}")


def Main(os_type, manufacture, product):
    if os_name == os_type:
        print(f"OS: {os_name}")
        if manufacture.startswith(manufacture):
            print(f"Manufacture: {manufacture}")
            if product_name.startswith(product):
                print(f"product_name: {product_name}")
                DELL_iDRAC(product_name, hwd_cmp[product_name])
                for dell_enclouse_id in dell_enclouse_ids:
                    for dell_slot_id in dell_slot_ids:
                        hardware_ouput = DELL_MEGACLI_ERROR_CHECKS(dell_enclouse_id, dell_slot_id)
                        print(hardware_ouput)


Main("Linux", "Dell", "PowerEdge")
# DELL_MEMORY_CHECKS("memory")
# DELL_MEMORY_CHECKS("controller")
