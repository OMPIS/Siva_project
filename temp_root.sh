#!/usr/bin/env bash

# Original script information...

USERID='67396'
USER='temproot'
GRPID='100'
DESC='Temp Root User'
HOME_DIR="/home/$USER"

SUDOERS_LINE="temproot        ALL=(ALL) NOPASSWD:ALL"
SUDOERS_FILE=""
PASS=""

# Colored output functions
function print_green() { echo -e "\033[32m$1\033[0m"; }
function print_red() { echo -e "\033[31m$1\033[0m"; }
function print_info() { echo -e "\033[36m$1\033[0m"; }

# Password generation function
function pass_gen() {
  if [ -z "$PASS" ]; then
    PASS=$(tr -cd '[:alnum:]' < /dev/urandom | fold -w12 | head -1)
    print_info "Generated password: $PASS"
  fi
}

# Function to display usage instructions
function print_help() {
  print_info '''USAGE: ./temproot.sh <option>
    -t) <# of days> | Add temproot user for a period of days (1–45).
    -v)             | Validate temproot user.
    -r)             | Remove temproot user.
    -e) <# of days> | Extend temproot user for a period of days (1–45).
    -h)             | Display help.
  '''
}

# Main add_temproot function
function add_temproot() {
  # Ensure password is generated if not provided
  pass_gen
  
  # Additional add logic...
  print_info "Adding user $USER with a duration of $DAYS days and password: $PASS"
  # Note: Code for adding the user, setting permissions, etc.
}

# MAIN ###

# Initialize option variables
OPTION=""
DAYS=""

# Parse command-line options
while getopts ":t:e:vrh" OPT; do
  case "$OPT" in
    t) OPTION="add"; DAYS="$OPTARG";;
    v) OPTION="validate";;
    r) OPTION="remove";;
    e) OPTION="extend"; DAYS="$OPTARG";;
    h) print_help; exit 0;;
    \?) print_red "Invalid option: -$OPTARG"; exit 1;;
    :) print_red "Option -$OPTARG requires an argument."; print_help; exit 1;;
  esac
done

# Validate -t and -e options
if [ "$OPTION" == "add" ] || [ "$OPTION" == "extend" ]; then
  if [[ ! "$DAYS" =~ ^[0-9]+$ ]] || [ "$DAYS" -le 0 ] || [ "$DAYS" -gt 45 ]; then
    print_red "Error: The -t and -e options require a valid number of days (1–45)."
    print_help
    exit 1
  fi
fi

# Ensure script is run as root
if [ $UID != 0 ]; then
  print_red "Error: Script must be run as root."
  exit 1
fi

# Action based on option
case "$OPTION" in
  "add")
    if id "$USER" &>/dev/null; then
      print_red "User $USER already exists."
      exit 1
    else
      add_temproot
      # Add logging or any other action
    fi
    ;;
  "validate")
    # Call validation function
    ;;
  "remove")
    # Call removal function
    ;;
  "extend")
    # Call extension function
    ;;
  *)
    print_help
    exit 1
    ;;
esac
