import os
import json

# Functions imports
import functions.chroma as chroma
import functions.setup as setup


def debug_loader(settings : dict):
    debug_settings = settings['debugSettings'] # Gets the debug settings.

    functions = {
        'chroma' : chroma.chromatize
    }

    print('Loading into debug mode.')
    print('Calling {} function.'.format(debug_settings['debugFunction']))

    setup.copy_pack(debug_settings['debugPack'], 'debug')
    functions[debug_settings['debugFunction']](debug_settings['debugParameters']) 


def loader():
    f = open('./settings.json', 'r+')
    settings = json.load(f)

    launch_functions = {
        'debug' : debug_loader # Reference to the function.
    }

    setup.verify_folders()

    print('Loading settings.')

    launch_functions[settings['launchMode']](settings) # I use java and javascript style in the dict because its json.


if __name__ == '__main__':
    loader()