#!/usr/bin/env bash

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
    TMPR_PASS=$(tr -cd '[:graph:]' < /dev/urandom | fold -w12 | head -1 | tr '|' '$' | tr '(' 'd' | tr ')' 'f')
    echo "Generated password: $TMPR_PASS"
  else
    TMPR_PASS=$PASS
    echo "Using provided password: $TMPR_PASS"
  fi
}

function add_temproot() {
  pass_gen
  useradd -u $USERID -g $GRPID -c "$DESC" -d $HOME_DIR -s /bin/bash $USER
  echo "$USER:$TMPR_PASS" | chpasswd
  echo "$SUDOERS_LINE" >> /etc/sudoers
  print_green "$USER added with password $TMPR_PASS"
}

function rm_temproot() {
  userdel $USER
  sed -i "/^$USER/d" /etc/sudoers
  print_green "$USER removed"
}

function validate_temproot() {
  if id "$USER" &>/dev/null; then
    print_green "$USER exists"
  else
    print_red "$USER does not exist"
  fi
}

function extend_temproot() {
  pass_gen
  chage -E $(date -d "+$DAYS days" +%Y-%m-%d) $USER
  print_green "$USER password extended for $DAYS days"
}

function print_help() {
  print_info '''USAGE: ./temproot.sh <option>

        -t) <# of days> | Add temproot user for a period of days.
        -p) <password>  | Define password for temproot user.
        -v)             | Validate temproot user.
        -r)             | Remove temproot user.
        -e) <# of days> | Extend temproot user for a period of days.
        -h)             | Display help.
  '''
}

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

if [ $UID != 0 ]; then
   print_red "User has insufficient privileges. Must run as root."
   exit 1
fi

if [ "$OPTION" == "add" ]; then
  if ! (expr $DAYS + 0 &>/dev/null); then
    print_red "Number has to be passed after -t option. MAX is 45 days!!!"
    print_help
    exit 1
  elif [ "$DAYS" -ge 46 ]; then
    print_red "MAX is 45 Days!!!"
    print_help
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
  fi
  extend_temproot
  logger_entry "extended for $DAYS days"

else
  print_help
  exit 1
fi

exit 0
