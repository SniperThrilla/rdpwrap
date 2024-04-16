import sys
import ctypes, os


def check_administrator() -> bool:
    """
    Check if the program has administrator rights.
    """
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

def read_file(path: str) -> str:
    """
    Reads the offsets.txt file provided and returns its contents.

    Args:
        path: Path of offsets.txt
    
    Returns:
        contents of offsets.txt
    """
    print(path)
    try:
        with open(path, 'r') as file:
            contents = file.read()
            if contents == None or contents == "\n":
                print("\033[91moffsets.txt was found but is empty... \
Have you run autofinder.bat yet?\033[0m")
    except FileNotFoundError:
        print("\033[91moffsets.txt was not found. Is the path set correctly?\
\033[0m")
        raise FileNotFoundError

    return contents

def disable_rdp_service() -> None:
    """
    Stops Remote Desktop Services so that rdpwrap.ini can be modified.
    """
    os.system(f'net stop "Remote Desktop Services"')

def enable_rdp_service() -> None:
    """
    Starts Remote Desktop Services so that RDP will work again.
    """
    os.system(f'net start "Remote Desktop Services"')


def modify_rdpwrap(offsets) -> None:
    """
    Modifies rdpwrap.ini with the new offsets in offsets.txt

    Args:
        offsets: Offsets from offsets.txt
    """
    with open('C:\\Program Files\\RDP Wrapper\\rdpwrap.ini', 'r+') as file:
        original_contents = file.read()

        sections = original_contents.split("\n\n")
        
        start_section = sections[:4]
        win_version_specifics = sections[4:]

        
        non_slint = [x for x in win_version_specifics if '-SLInit' not in x]
        slint = [x for x in win_version_specifics if '-SLInit' in x]
        """
        print(start_section)
        print("\n"*10)
        print(non_slint)
        print("\n"*10)
        print(slint)
        print("\n"*10)
        """

        non_slint_new, slint_new = offsets.split("\n\n")
        non_slint_new_ver = non_slint_new[1:].split(']')[0].split('.')
        slint_new_ver = slint_new[1:].split('-')[0].split('.')

        for index, version in enumerate(non_slint):
            version_split = version[1:].split(']')[0].split('.')
            if(len(version_split) != 4):
                continue
            if (int(non_slint_new_ver[0]) <= int(version_split[0])
                and int(non_slint_new_ver[1]) <= int(version_split[1])
                and int(non_slint_new_ver[2]) <= int(version_split[2])
                and int(non_slint_new_ver[3]) <= int(version_split[3])):
                if version_split == non_slint_new_ver:
                    print("\033[91mYour rdpwrap.ini already includes the new Non-SLInit offsets\033[0m")
                    print(f"\033[91mThe offset verson was {non_slint_new_ver}\033[0m")
                    break
                non_slint.insert(index, non_slint_new)
                print(f"{version_split} was found, inserting before it.")
                print(f"Inserted {non_slint_new}")
                break

        print("\n")

        for index, version in enumerate(slint[1:]):
            version_split = version[1:].split('-')[0].split('.')
            if(len(version_split) != 4):
                continue
            if (int(slint_new_ver[0]) <= int(version_split[0])
                and int(slint_new_ver[1]) <= int(version_split[1])
                and int(slint_new_ver[2]) <= int(version_split[2])
                and int(slint_new_ver[3]) <= int(version_split[3])):
                if version_split == slint_new_ver:
                    print("\033[91mYour rdpwrap.ini already includes the new SLInit offsets\033[0m")
                    print(f"\033[91mThe offset verson was {slint_new_ver}\033[0m")
                    break
                slint.insert(index + 1, slint_new)
                print(f"{version_split} was found, inserting before it.")
                print(f"Inserted {slint_new}")
                break
        
        file.seek(0)
        file.write("\n\n".join(start_section) + "\n\n" + "\n\n".join(non_slint) 
                   + "\n\n" + "\n\n".join(slint))

def main():
    """
    Main function.
    """
    if not check_administrator():
        print("\033[91mThe executable is not being run with administrator \
rights.\033[0m")
        print("\033[91mHere's some things to check:\033[0m")
        print("\033[91mDid you remember to run as administrator?\033[0m")
        print("\033[91mIs some antivirus enabled?\033[0m")
        raise PermissionError
    for arg in sys.argv:
        print(arg)

    path = os.getcwd()
    parent = os.path.dirname(path)
    contents = read_file(parent + "\offsets.txt")

    disable_rdp_service()

    modify_rdpwrap(contents)

    enable_rdp_service()



if __name__ == "__main__":
    main()