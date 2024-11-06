#!/usr/bin/env bash

# SCRIPT_AUTHOR=Anton Takareuski
# NOTE: Modified / improved from add_temproot_user.sh by Vang Pha

# SCRIPT_DESCRIPTION=Script sets up temproot user for a period of time specified.
# SCRIPT_DATE=20160523
# SCRIPT_UPDATE=20170809
# SCRIPT_LANGUAGE=bash 2.0
# SCRIPT_PLATFORM=linux,solaris,aix
# SCRIPT_VERSION=4

USERID='67396'
USER='temproot'
GRPID='100'
DESC='Temp Root User'
HOME_DIR="/home/$USER"
SUDOERS_LINE="temproot        ALL=(ALL) NOPASSWD:ALL"
SUDOERS_FILE=""
PASS=""

#Colored output
function print_green() {
  echo -e "\033[32m$1\033[0m"
}

function print_red() {
  echo -e "\033[31m$1\033[0m"
}

function print_info() {
  echo -e "\033[36m$1\033[0m"
}

function logger_entry() {
  action="$1"
  if [ "$(uname)" == "Linux" ]; then
    logger "$USER user $action"
  elif [ "$(uname)" == "SunOS" ]; then
    logger -p user.alert "$USER user $action"
  elif [ "$(uname)" == "AIX" ]; then
    logger -p user.info "$USER user $action"
  else
    echo "Unsupported OS: $(uname -a)"
    exit 1
  fi
}

function pass_gen() {
  if [ -z "$PASS" ]; then
    # Generate a random password if -p was not provided
    if [ "$(uname)" == "Linux" ]; then
      TMPR_PASS=$(tr -cd '[:graph:]' < /dev/urandom | fold -w12 | head -1 | tr '|' '$' | tr '(' 'd' | tr ')' 'f')
    elif [ "$(uname)" == "SunOS" ]; then
      SRAND="$RANDOM$(date +%S)$RANDOM"
      TMPR_PASS=$(echo $SRAND | digest -v -a md5 | cut -d" " -f 2 | cut -c 1-10)
    elif [ "$(uname)" == "AIX" ]; then
      ARAND="$RANDOM$(date +%s)$RANDOM"
      TMPR_PASS=$(echo $ARAND | csum -h MD5 - | cut -d " " -f 1 | cut -c 1-10)
    else
      print_red "Unsupported OS: $(uname -a)"
      exit 1
    fi
    echo "Generated password: $TMPR_PASS"
  else
    TMPR_PASS=$PASS
    echo "Using provided password: $TMPR_PASS"
  fi

  if [ "$(uname)" == "Linux" ]; then
    if ! (cp -p /etc/shadow /etc/shadow.$(date +%Y%m%d)); then
      print_red "Failed to back up /etc/shadow"
      exit 1
    else
      PASS_CMD="echo '$USER:$TMPR_PASS' | chpasswd"
      if ! (eval $PASS_CMD &>/dev/null); then
        print_red "Failed to set $USER password. Try manually..."
      else
        print_green "$USER PASSWORD: $TMPR_PASS is valid for $DAYS day(s) on $(hostname)"
      fi
    fi
  elif [ "$(uname)" == "SunOS" ]; then
    SHASH=$(perl -e "print crypt('${TMPR_PASS}', 'salt'),'\n'")
    if ! (cp -p /etc/shadow /etc/shadow.$(date +%Y%m%d)); then
      print_red "Failed to back up /etc/shadow"
      exit 1
    else
      sed /^$USER/d /etc/shadow > /etc/shadow.tmp && mv /etc/shadow.tmp /etc/shadow
      if ! (echo "${USER}:${SHASH}:::::::" >> /etc/shadow); then
        print_red "Failed to set $USER password"
      else
        print_green "$USER PASSWORD: $TMPR_PASS is valid for $DAYS day(s) on $(hostname)"
      fi
    fi
  elif [ "$(uname)" == "AIX" ]; then
    if ! (cp -p /etc/security/passwd /etc/security/passwd.$(date +%Y%m%d)); then
      print_red "Failed to back up /etc/security/passwd"
      exit 1
    else
      if ! (echo "$USER:$TMPR_PASS" | chpasswd); then
        print_red "Failed to set $USER password"
      else
        pwdadm -c $USER
        print_green "$USER PASSWORD: $TMPR_PASS is valid for $DAYS day(s) on $(hostname)"
      fi
    fi
  else
    print_red "Unsupported OS: $(uname -a)"
  fi
}

function print_help() {
  print_info '''USAGE: ./temproot_3.0_beta.sh <option>

        -t) <# of days> | Add temproot user for a period of days.
        -p) <password>  | Define password for temproot user.
        -v)             | Validate temproot user.
        -r)             | Remove temproot user.
        -e) <# of days> | Extend temproot user for a period of days.
        -h)             | Display help.
  '''
}

### MAIN ###
while getopts ":t:p:e:vrh" OPT; do
   case "$OPT" in
      t)     OPTION="add"; DAYS=$OPTARG;;
      p)     PASS=$OPTARG;;
      v)     OPTION="validate";;
      r)     OPTION="remove";;
      e)     OPTION="extend"; DAYS=$OPTARG;;
      h)     print_help; exit 0;;
     \?)     print_red "Invalid option: -$OPTARG" >&2; exit 1;;
      :)     print_red "Option -$OPTARG requires an argument." >&2; print_help; exit 1;;
      "")    print_help;;
   esac
done

# Check for root privileges
if [ $UID != 0 ]; then
   print_red "User has insufficient privileges. Must run as root."
   exit 1
fi

# Check if SUDOERS file exists and AT job directory is identified here

# Options processing #
if [ "$OPTION" == "add" ]; then
  if ! (expr $DAYS + 0 &>/dev/null); then
    print_red "Number has to be passed after -t option. MAX is 45 days!!!"
    print_help
    exit 1
  else
    if [ "$DAYS" -ge 46 ]; then
      print_red "MAX is 45 Days!!!"
      print_help
      exit 1
    fi
  fi
  if (id $USER &>/dev/null); then
    print_red "$USER already exists..."
    exit 1
  fi
  add_temproot
  logger_entry added

elif [ "$OPTION" == "remove" ]; then
  if ! (who | grep $USER); then
    rm_temproot
    logger_entry removed
  else
    print_red "Open $USER session found..."
    exit 1
  fi

elif [ "$OPTION" == "validate" ]; then
  validate_temproot

elif [ "$OPTION" == "extend" ]; then
  if ! (expr $DAYS + 0 &>/dev/null); then
    print_red "Number has to be passed after -e option. MAX is 45 days!!!"
    print_help
    exit 1
  elif [ "$DAYS" -ge 46 ]; then
    print_red "MAX is 45 Days!!!"
    print_help
    exit 1
  else
    extend_temproot
    logger_entry "extended for $DAYS days"
  fi

else
  print_help
  exit 1
fi

exit 0
