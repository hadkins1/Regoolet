import os
import sys
from pyparsing import line
from rich.console import Console
from rich.theme import Theme


# setting console theme
custom_theme = Theme({"success": "#00ff00", "warning": "#ffff00", "error": "bold #ff0000", "hint": "bold #00afff", "info": "#00d7d7", "title": "#d700ff", "text": "italic #ff5faf"})
console = Console(theme=custom_theme)


# read file line by line
def read_file(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
    return lines


# write file line by line
def write_file(file_name, lines):
    with open(file_name, 'w') as f:
        f.write("[Rule]\n")
        for line in lines:
            f.write(line)


# read .list files in a folder recursively
def read_folder_recursively(folder_name):
    files = []
    for file in os.listdir(folder_name):
        if os.path.isdir(folder_name + "/" + file):
            files.extend(read_folder_recursively(folder_name + "/" + file))
        elif file.endswith(".list"):
            files.append(folder_name + "/" + file)
    return files


def start_with_one_of_tokens(line, tokens):
    for token in tokens:
        if line.startswith(token):
            return True
    return False


def l2m(file, policy, output):
    excludeTokens = ["#", " ", " ", "\n"]
    surgeTokens = ["DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-SET", "IP-CIDR", "IP-CIDR6", "GEOIP", "PROCESS-NAME", "USER-AGENT", "URL-REGEX", "IN-PORT", "DEST-PORT", "SRC-IP", "PROTOCOL", "AND"]

    if not file.endswith(".list"):
        console.print(f"[error] File {file} is not a .list file![/error]")
        return

    console.print(f"converting .list file: [info]{file}[/info]")
    lines = read_file(file)
    for i, l in enumerate(lines):
        l = l.replace(" ", "").split("//")[0]
        if not start_with_one_of_tokens(l, excludeTokens):
            if not start_with_one_of_tokens(l, surgeTokens):
                if l.startswith("."):
                    lines[i] = l.replace(".", "DOMAIN-SUFFIX,", 1)
                else:
                    lines[i] = "DOMAIN," + l
            lines[i] = lines[i].replace("\n", "") + "," + policy + "\n"
    write_file(output, lines)
    console.print(f"[success]converted .list file to: [/success][info]{output}[/info]")


def l2m_with_folder(dir_path, policy):
    if not os.path.isdir(dir_path):
        console.print(f"[error] {dir_path} is not a folder![/error]")
        return

    files = read_folder_recursively(dir_path)
    for file in files:
        if os.path.getsize(file) == 0:
            console.print(f"[warning] File {file} is empty![/warning]")
            continue
        l2m(file, policy, file.replace(".list", ".sgmodule"))


def main():

    if len(sys.argv) < 3:
        console.print(f"[error] Usage: {sys.argv[0]} <input_file> <policy>[/error]")
        return

    if not os.path.exists(sys.argv[1]):
        console.print(f"[error] File {sys.argv[1]} does not exist![/error]")
        return
    
    if os.path.getsize(sys.argv[1]) == 0:
        console.print(f"[warning] File {sys.argv[1]} is empty![/warning]")
        return
    
    if os.path.isdir(sys.argv[1]):
        l2m_with_folder(sys.argv[1], sys.argv[2])
    else:
        l2m(sys.argv[1], sys.argv[2], sys.argv[1].replace(".list", ".sgmodule"))


main()
