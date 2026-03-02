import urllib.request
import subprocess
import re
import os
from time import sleep

# testing code server

images = {
    'Ubuntu 24.04': 'https://cloud-images.ubuntu.com/minimal/releases/noble/release/',
    'Ubuntu 22.04': 'https://cloud-images.ubuntu.com/minimal/releases/jammy/release/'
}

def img_ext(base_url):
    with urllib.request.urlopen(base_url) as response:
        html = response.read().decode('utf-8')
        match = re.search(r'href="([^"]*amd64\.img)"', html)
        if match:
            return base_url + match.group(1)
        else:
            return None

def setup():
    img_options = {
        '1': 'Ubuntu 24.04',
        '2': 'Ubuntu 22.04'
    }
    print('''What image would you like to select?
[1] Ubuntu 24.04
[2] Ubuntu 22.04''')
    img = input('Enter Number: ')
    selected_image = img_options.get(img)
    if selected_image:
        os.system('clear')
        url = img_ext(images[selected_image])
        filename = url.split('/')[-1]
        print('Downloading...')
        urllib.request.urlretrieve(url, filename)
        os.system('clear')
        print('Done!')
        sleep(2)
        configure(filename)
    else:
        os.system('clear')
        print('unrecognized input...')
        sleep(2)
        os.system('clear')
        setup()

def configure(filename):
    os.system('clear')
    print(f'Starting configuration on {filename}...')
    sleep(3)
    os.system('clear')
    os.system(f'mv {filename}.img {filename}.qcow2')
    print(filename + ' has been configured!')
    sleep(3)
    os.system('clear')
    img_resize = input('What would you like to resize the images disk to (Gigabytes): ')
    os.system(f'qemu-img resize {filename} {img_resize}G')
    print('libguestfs-tools must be installed for some parts of the configuration. Do u want to install it?')
    libguestfs = input('(Y/N): ')
    if libguestfs.lower() in ['y', 'yes']:
        try:
            os.system('clear')
            subprocess.run(['apt', 'install', 'libguestfs-tools', '-y'], check=True)
        except subprocess.CalledProcessError as err:
            print(f'unable to install libguestfs-tools: {err}')
            return
    else:
        print('libguestfs-tools is a requirement. exiting script...')
        return
    try:
        subprocess.run(['virt-customize', '-a', filename, '--run-command', '"sudo echo > /etc/machine id; sudo ln -sf /etc/machine-id /var/lib/dbus/machine-id"'], check=True)
    except subprocess.CalledProcessError as err:
        print(f'An error occured with the machine ID: {err}')
        return
    vmid = input('Enter Virtual Machine ID: ')
    try:
        subprocess.run(['qm', 'set', f'{vmid}', '--serial0', 'socket', '--vga', 'serial0'], check=True)
    except subprocess.CalledProcessError as err:
        print(f'Invalid virtual machine ID: {err}')
        return

    root_pwd = input('Would you like to set a root password? (Y/N): ')
    if root_pwd.lower() in ['y', 'yes']:
        try:
            pwd = input('What would you like the root password to be: ')
            subprocess.run(['virt-customize', '-a', filename, '--root-password', f'password:{pwd}'], check=True)
        except subprocess.CalledProcessError as err:
            print(f'An error occurred with the root password: {err}')
            return
    else:
        pass
    print('Setting a timezone for the image (ex: Europe/London, America/New_York')
    try:
        timezone = input('What timezone would you like the image to be in: ')
        subprocess.run(['virt-customize', '-a', filename, '--timezone', timezone], check=True)
    except subprocess.CalledProcessError as err:
        print(f'An error occured with the timezone: {err}')
        return
    ssh_config = input('Would you like to configure SSH? (Y/N):')
    if ssh_config.lower() in ['y', 'yes']:
        try:
            subprocess.run(['virt-edit', filename, '/etc/sshd_config.d/60_cloudimg-settings.conf'], check=True)
            subprocess.run(['virt_edit', filename, '/etc/ssh/sshd_config.d/sshd_config'], check=True)
        except subprocess.CalledProcessError as err:
            print(f'An error occurred with the ssh configuration: {err}')
            return
    pkgs = input('Would you like to install any external packages? (Y/N):')
    if pkgs.lower() in ['y', 'yes']:
        try:
            pkgs = input('What packages would you like to install on the image: ')
            pkgs = ','.join(pkgs.replace(',', ' ').split()) # unsure if this is doing it's intended behaviour
            subprocess.run([f'virt-customize', '-a', '{filename}', f'--install {pkgs}'], check=True)
        except subprocess.CalledProcessError as err:
            print(f'Invalid packages: {err}')
            return
    else:
        pass
    finished = input('Would you like to finish the install and import the image into the VM? (Y/N):')
    if finished.lower() in ['y', 'yes']:
        try:
            drive_name = input('What drive does ur VMs disk sit on (example: local-lvm: ')
            subprocess.run(['qm', 'importdisk', vmid, filename, drive_name, '--format', 'qcow2'], check=True)
        except subprocess.CalledProcessError as err:
            print(f'An error occurred with the drive name: {err}')
            return
    else:
        print('exiting script... you can always import it later!')

if __name__ == '__main__':
    setup()