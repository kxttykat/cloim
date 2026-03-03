import os
import urllib.request
import subprocess
from colorama import init, Fore
from time import sleep

init()

images = {
    'Debian 13 Trixie': 'https://cdimage.debian.org/cdimage/cloud/trixie/latest/debian-13-generic-amd64.qcow2',
    'Ubuntu 24.04 Noble': 'https://cloud-images.ubuntu.com/minimal/releases/noble/release/ubuntu-24.04-minimal-cloudimg-amd64.img'
}

class Installer:
    def __init__(self):
        self.file = None

    def download(self):
        os.system('clear')
        print('''Which cloud image would you like to install?
Debian 13 Trixie: 1
Ubuntu 24.04 Noble: 2''')
        choice = input("Enter A Number: ")
        if choice == '1':
            os.system('clear')
            print(Fore.GREEN + 'Downloading...')
            self.file = urllib.request.urlretrieve(images["Debian 13 Trixie"], 
            "debian-13-generic-amd64.qcow2")
            os.system('clear')
            print(Fore.BLUE + f'Download has finished for {self.file[0]}!')
            sleep(3)
        elif choice == '2':
            os.system('clear')
            print(Fore.GREEN + 'Downloading...')
            self.file = urllib.request.urlretrieve(images["Ubuntu 24.04 Noble"], 
            "ubuntu-24.04-minimal-cloudimg-amd64.img")
            os.system('clear')
            print(Fore.BLUE + f'Download has finished for {self.file[0]}!')
            sleep(3)
        else:
            print(Fore.RESET + 'You did not specify an image! returning to menu...')
            sleep(3)
            download()

    def setup(self):
        os.system('clear')
        img_resize = input('Please specify a size to resize the image with(E.G: 8GB,16GB,32GB): ')
        try:
            subprocess.run(f'qemu-img resize {self.file[0]} {img_resize}',
            shell=True,
            text=True)
        except Exception as e:
            print(e)
        os.system('clear')
        pkgs = input(Fore.RESET + 'Do you want to install packages to this image?(y/N): ')
        if pkgs.lower() in ['y', 'yes']:
            os.system('clear')
            packages = input("Please enter packages to install(format: pkg1,pkg2,pkg3): ")
            try:
                subprocess.run(f"virt-customize -a {self.file[0]} --install {packages}", 
                shell=True,
                text=True)
                os.system('clear')
                print(Fore.BLUE + f'Packages have finished installing for {self.file[0]}')
            except Exception as e:
                print(e)
        else:
            print('exiting.')
            sleep(1)
            os.system('clear')
            print('exiting..')
            sleep(1)
            os.system('clear')
            print('exiting...')
        os.system('clear')
        print('Giving image new machine-id.')
        os.system('clear')
        sleep(1)
        print('Giving image new machine-id..')
        os.system('clear')
        sleep(1)
        os.system('clear')
        print(Fore.GREEN + 'Giving image new machine-id...')
        subprocess.run(f'virt-customize -a {self.file[0]} --run-command "truncate -s 0 /etc/machine-id"', 
        shell=True,
        text=True)
        os.system('clear')
        print(Fore.BLUE + 'Done!')

if __name__ == '__main__':
    installer = Installer()
    installer.download()
    installer.setup()
