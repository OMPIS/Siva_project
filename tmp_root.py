import os
import subprocess
import random
import string

###
USERID, USER, GRPID = '67396', 'temproot', '100'
DESC, HOME_DIR = 'Temp Root User', f"/home/{USER}"
SUDOERS_LINE = "temproot ALL=(ALL) NOPASSWD:ALL"
USER_AGE = '45'


###
def OS_validation():
    cmd = "uname -a"
    os_type = os.popen(f"{cmd}").read().strip().split()[0]
    return os_type


def Executing_User():
    cmd = "whoami"
    execute_user = os.popen(f"{cmd}").read().strip().split()[0]
    return execute_user


def Generate_password(length=8):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def Change_password(username, new_password, user_age):
    try:
        subprocess.run(['passwd', username], input=f'{new_password}\n{new_password}\n', universal_newlines=True, check=True)
        subprocess.run(['chage', '-M', user_age, username], check=True)
        print(f"Password for user '{username}' changed successfully. {new_password}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to change password: {e}")


def Create_user(username, password, uid, gid, description, home_dir, user_age):
    try:
        subprocess.run(['useradd', '-u', str(uid), '-g', str(gid), '-d', home_dir, '-c', description, username], check=True)
        subprocess.run(['chpasswd'], input=f'{username}:{password}', universal_newlines=True, check=True)
        subprocess.run(['chage', '-M', user_age, username], check=True)
        print(f"User '{username}'; Password: {password} created successfully with UID {uid}, GID {gid}, and home directory '{home_dir}'.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create user: {e}")


def User_validation(user_name):
    pass_file = "/etc/passwd"
    validate = os.popen(f"cat {pass_file} | grep {user_name}").read().strip()
    random_password = Generate_password(8)
    if len(validate) > 0:
        print(f"[INFO] {user_name} User Exists")
        Change_password(user_name, random_password, USER_AGE)
    else:
        print(f"[INFO] Creating User: {user_name} ")
        Create_user(user_name, random_password, USERID, GRPID, DESC, HOME_DIR, USER_AGE)


os_name = OS_validation()
execute_user = Executing_User()
if os_name == "Linux":
    if execute_user == "root":
        User_validation(USER)
    else:
        print(f"[WARNING] please execute using root user")
else:
    print(f"[WARNING] hostname is not Linux Machine")
