import os
import shutil
import zipfile


def verify_folders():
    integral_folders = ['input', 'output'] # These are folders that need to exist or the software breaks
    current_folders = os.listdir() # Gets the current folders

    for folder in integral_folders:
        if not folder in current_folders: # Checks if the folder exists
            os.mkdir(folder)
            print('Created -> {} <- because could not find folder.'.format(folder))


def copy_pack(path: str, launch_mode: str) -> None:
    if path.endswith('.zip'): # Checks if the file is a .zip only checking .zips because Minecraft supports them
        if launch_mode == 'debug':
            if os.path.exists('./input/pack'): # Checks if a pack folder already exists if there isn't then it copies the pack. Only occurs in debug mode
                print('Not overriding files because in debug mode.')

            else:
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    print('Copying files.')
                    zip_ref.extractall('./input/pack')

        else:
            if os.path.exists('./input/pack'):
                print('Overriding files in folder -> input <-.')

            with zipfile.ZipFile(path, 'r') as zip_ref: # Uses zipfile module to unzip files
                print('Copying files.')
                zip_ref.extractall('./input/pack')

    else:
        if launch_mode == 'debug_mode':
            if os.path.exists('./input/pack'):
                print('Not overriding files because in debug mode.')

            else:
                print('Copying files.')
                shutil.copytree(path, './input/pack')

        else:
            if os.path.exists('./input/pack'):
                print('Overriding files in folder -> input <-.')

            print('Copying files.')
            shutil.copytree(path, './input/path') # Copy files using shutil

    if os.path.exists('./input/pack/assets/minecraft/mcpatcher'): # Ensures that the pack folder has a mcpatcher and anim folder used with optifine animations
        if not os.path.exists('./input/pack/assets/minecraft/mcpatcher/anim'):
            os.mkdir('./input/pack/assets/minecraft/mcpatcher/anim')
            print('Creating -> anim <- folder because pack did not already have one.')

    else:
        os.mkdir('./input/pack/assets/minecraft/mcpatcher')
        os.mkdir('./input/pack/assets/minecraft/mcpatcher/anim')
        print('Creating -> mcpatcher <- and -> anim <- folder because pack did not already have them.')
        

    if not os.path.exists('input/pack/pack_settings.json'):
        with open('input/pack/pack_settings.json', 'w+') as f:
            f.write('{}')

        print('Creating -> pack_settings.json <- for your convienience')
        return 
    
    
