#!/usr/bin/python3

"""
Author: Hafidh Zouahi (gh_zouahi@esi.dz)
Category: Misc
Difficulty: Medium
"""

import os
import random
import readline
import time
from termcolor import colored
from base64 import b64encode

intro_message = """\
.-------------------------------------------------------------------------------------.
| ___  ____                  _____ _                                      __   _____  |
| |  \/  (_)                /  ___| |                                    /  | |  _  | |
| | .  . |_  ___ _ __ ___   \ `--.| |_ ___  _ __ __ _  __ _  ___  __   __`| | | |/' | |
| | |\/| | |/ __| '__/ _ \   `--. \ __/ _ \| '__/ _` |/ _` |/ _ \ \ \ / / | | |  /| | |
| | |  | | | (__| | | (_) | /\__/ / || (_) | | | (_| | (_| |  __/  \ V / _| |_\ |_/ / |
| \_|  |_/_|\___|_|  \___/  \____/ \__\___/|_|  \__,_|\__, |\___|   \_/  \___(_)___/  |
|             \033[97;1mB y\033[0m  \033[32;1mH a c k T h e B o x\033[0m  \033[97;1mL a b s\033[0m        __/ |                          |
|                                                     |___/                           |
`-----------------------.                                   .-------------------------'
                        |  Welcome to your online temporary |
                        |            Micro Storage          |
                        `-----------------------------------'

                                   \033[91;1m\!/\033[0m \033[33;5;1mWARNING\033[0m \033[91;1m\!/\033[0m
   \033[1;31;103mYour storage only lasts during the ongoing session, once the session killed, all\033[0m
                  \033[1;31;103myour files will be gone. Use this service responsibly.\033[0m
                                 \033[33;1m---------o---------\033[0m
"""

def print_inf(string, end='\n'):
    print(colored('[*] ' + string, 'blue'), end=end)

def print_err(string, end='\n'):
    print(colored('[-] ' + string, 'red'), end=end)

def print_gud(string, end='\n'):
    print(colored('[+] ' + string, 'green'), end=end)

def rand_dirname(length=32):
    charset = "0123456789abcdef"
    dirname = ""
    while len(dirname) < length:
        dirname += random.choice(charset)

    return dirname

def check_filename(filename):
    return all(i in WHITELIST for i in filename)

def empty_files():
    return all(len(open(f).read()) == 0 for f in files)

def menu():
    print("1 => Upload a new file ({} file(s) remaining)             ".format(MAX_FILES - len(files)))
    print("2 => List your uploaded files ({} file(s) uploaded so far)".format(len(files)))
    print("3 => Delete a file                                        ")
    print("4 => Print file content                                   ")
    print("5 => Compress and download all your files                 ")
    print("0 => Quit (you will lose your files!)                     ")

MAX_LEN = 4096
MAX_FILES = 10
BASE_DIR = "/home/storage/"
TAR_FILE = "archive.tar"
CLEAN_EXIT = False
WHITELIST = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_=+. "

# Setup storage directory
dirname = BASE_DIR + rand_dirname()
os.mkdir(dirname)
os.chmod(dirname, mode=0o777)
os.chdir(dirname)

files = []

print(intro_message)

while True:
    menu()

    try:
        choice = input(">>> Choose an option: ")
        
        if choice == "1":
            print_inf("Enter your file name: ", end='')
            filename = input()

            if not check_filename(filename):
                print_err("No no no, you're trying to hack us, good bye.")
                CLEAN_EXIT = True
                exit(0)

            elif len(filename) > 32:
                print_err("File name is too long.")

            elif len(files) >= MAX_FILES:
                print_err("You have exceeded the number of allowed files.")

            elif filename in files:
                print_err("File already exists.")

            else:
                print_inf("Start typing your file content: (send 'EOF' when done)")
                content = ''

                while len(content) < MAX_LEN and content.strip()[-3:] != "EOF":
                    content += input() + "\n"
                
                content = content.strip()[:-3]
                open(filename, 'wb').write(content.encode())
                print_gud("Your file \"{}\" has been saved. ({} bytes written)".format(filename, len(content)))
                files.append(filename)
            
        elif choice == "2":
            print_inf("Fetching your uploaded files...")

            if len(files) == 0:
                print_err("You have no files.")

            for f in range(len(files)):
                print_inf("{}. {}".format(f, files[f]))

        elif choice == "3":
            print_inf("Enter the file identifier: (0 - {})".format(MAX_FILES - 1))
            file_id = input('>>> ')

            if not file_id.isdigit():
                print_err("Hummm??")
                continue

            file_id = int(file_id)

            if file_id < len(files):
                print_inf("Deleting \"{}\"...".format(files[file_id]))
                os.remove(files[file_id])
                files.remove(files[file_id])
                print_gud("File deletion completed.")
            else:
                print_err("No such file.")

        elif choice == "4":
            print_inf("Enter the file identifier: (0 - {})".format(MAX_FILES - 1))
            file_id = input('>>> ')

            if not file_id.isdigit():
                print_err("Hummm??")
                continue

            file_id = int(file_id)

            if file_id < len(files):
                content = open(files[file_id]).read()
                if len(content) == 0:
                    print_err("Your file is empty, nothing to show.")
                    continue
                print(content)
            else:
                print_err("No such file.")

        elif choice == "5":
            if not len(files):
                print_err("You have no files.")
                continue
            elif empty_files():
                print_err("Your files are empty, nothing to download.")
                continue

            os.system("tar -cf {} * 2>/dev/null".format(TAR_FILE))
            time.sleep(2)
            archive = b64encode(open(TAR_FILE, 'rb').read()).decode()
            os.remove(TAR_FILE)
            print_gud("Your base64 encoded archive:")
            print(archive)

        elif choice == "0":
            print_inf("Quitting...")
            CLEAN_EXIT = True
            exit(0)

        else:
            print_err("No such option.")

    except:
        if not CLEAN_EXIT:
            print()
            print_err("That wasn't supposed to happen o.O")
        os.chdir("..")
        os.system("rm -rf {} 2>/dev/null".format(dirname))
        exit(0)