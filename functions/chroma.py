import cv2
import numpy as np
import json


def modify_hue(img, hue_mod=None):
    # Thank you to fmw42 for this solution
    # https://stackoverflow.com/questions/62648862/how-can-i-change-the-hue-of-a-certain-area-with-opencv-python

    alpha = img[:, :, 3] # Extracts the alpha channel and the bgr channels from the image
    bgr = img[:, :, 0:3]

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV) # Converts the image to hsv and split it into individual channels
    h, s, v = cv2.split(hsv)

    if hue_mod is None:
        hnew = np.mod(h - h, 180).astype(np.uint8) # Subtracts the channel by itself, if HUE is 0 it essentially means red

    else:
        hnew = np.mod(h - hue_mod, 180).astype(np.uint8) # Subtracts the hue by the mod kinda self explainatory

    hsv_new = cv2.merge([hnew, s, v]) # Merges the new HUE with the saturation and value of the original image and then converts it back to bgr
    bgr_new = cv2.cvtColor(hsv_new, cv2.COLOR_HSV2BGR)

    bgra = cv2.cvtColor(bgr_new, cv2.COLOR_BGR2BGRA) # Gives bgra an alpha channel
    bgra[:, :, 3] = alpha # Inserts the original alpha channel
    
    return bgra


def chromatize(args: list) -> None: # I just pass args as a list because I dont want to use if statements to pass the correct amount or arguments. In debug mode at least
    image_path = './input\\pack\\{}'.format(args[0])

    with open('./input/pack/pack_settings.json', 'r+') as f: # Since chroma gets wack if its at different speeds we save it to a pack_settings json to use.
        data = json.load(f) # Loads the json file as a dictionary

        if 'chroma' in data: # Checks if the pack_settings.json already has a -> chroma <- key 
            frame_speed = int(data['chroma']['frame_speed']) # then yoinks the frame_speed value it got there in the lines below. 
            print('Read frame_speed: {} from pack_settings.json'.format(frame_speed))

        else:
            if len(args) > 1: # If the args list is long enough then we assign that value
                frame_speed = args[1]

            else: # Else we assign the default value
                frame_speed = 8

            data['chroma'] = {} # Assigns a new dict to the json. It would look like {"chroma": {}}
            data['chroma']['frame_speed'] = frame_speed # Assigns a value now it looks like {"chroma": {"frame_speed" : -> frame_speed <-}}

            f.seek(0) # Changes the steam pos
            f.truncate(0) # Clears the entire file because thats just how json work
            json.dump(data, f, indent=4) # Dumps the json back.

    if len(args) > 2:
        optifine = args[2]

    else:
        optifine = False

    if len(args) > 3:
        # Custom data for normal hearts is [[52, 0, 70, 8], 256, 'hearts.png']
        custom_data = args[3]

    else:
        custom_data = None

    # The args would look like this -> (image_path: str, frame_speed: int=8, optifine=False, custom_data=None) <- but since I like debug mode, this is how I gotta do
    print('\nImage path: {}'.format(image_path))
    print('Frame speed: {}'.format(frame_speed))
    print('Requires optifine: {}'.format(optifine))
    print('Custom data: {}'.format(custom_data))
    
    img = modify_hue(cv2.imread(image_path, -1))
    
    image_name = image_path.split('\\')[-1] # Like C:\items\diamond_sword.png split at -> \ <- results in [C:, items, diamond_sword.png] and index -> -1 <- is diamond_sword.png

    # So C:\item\sword.png split at -> \ <- and then its [C:, item, sword.png] when sliced [:-1] its basically
    parent_path = '\\'.join(image_path.split('\\')[:-1]) # Anything in front of front.png and then we join the [C:, item] with -> \ <- and it creates C:\item simple

    speeds_ranges = { # Since interpolation was creating post 1.8.9 optfine only things that do not require optifine can be intepolated an since it would
        1: (360, .5), # probably look a little weird I'll just keep using old method.
        2: (180, 1),  # Factors of 180 [1, 2, 3, 4, 5, 6, 9, 10, 12, 15, 18, 20, 30, 36, 45, 60, 90, 180] 
        3: (120, 1.5),# Only has 360 and 120 because I was WAY to lazy to figure out more multiples with floating point values
        4: (90, 2),   
        5: (60, 3),
        6: (45, 4),
        7: (36, 5),
        8: (30, 6),
        9: (20, 9),
        10: (18, 10),
        11: (15, 12)
    }

    mod = speeds_ranges[frame_speed][1] # Since many people use 1.9+. I may make a parameter to use interpolation in the future
    current_mod = mod 
    r = speeds_ranges[frame_speed][0] # r frames

    optifine_anim_path = './input/pack/assets/minecraft/mcpatcher/anim/'

    print('\nCreating an image with -> {} <- frames.'.format(r))
    print('And has -> {} <- hue mod per frame.'.format(mod))

    if custom_data is None: # Does all this code if its not a custom animation (Something that is a part of a greater image i.e. heart textures in icon.png)
        for frame in range(r):
            if frame == 0: # If the its the first frame, we assign chromas to an image
                chromas = modify_hue(img, current_mod)
            
            else:
                new_chroma = modify_hue(img, current_mod) # If its not the first frame, we concat an image vertically, since thats how minecraft does animations
                chromas = cv2.vconcat((new_chroma, chromas))

            current_mod += mod # Increases the mod since we are still modifying the hue of the original image

        if optifine:
            cv2.imwrite(f'{optifine_anim_path}{image_name}', chromas)

            with open(f'{optifine_anim_path}{image_name}.properties', 'w+') as f: # This is how optifine uses animations
                f.write('x=0\n' + # This is where the image starts on the x axis
                        'y=0\n' + # This is where the image starts on the y axis
                        'w={}\n'.format(img.shape[1]) + # This is where the image ends on the x axis
                        'h={}\n'.format(img.shape[0]) + # This is where the image ends on the y axis
                        'from={}\n'.format(f'./{image_name}') + # From the image in the -> anim <- folder animated to the image in the original location
                        'to={}'.format(image_path[30:])) # Example image_path = 'input/pack/assets/minecraft/textures/... image_path[30:] = textures/...

            print(f'Created {optifine_anim_path}{image_name}') # Becoming increasing lazier :(
            print(f'Created {optifine_anim_path}{image_name}.properties')
            
        else:
            cv2.imwrite(image_path, chromas)

            with open('{}\\{}.mcmeta'.format(parent_path, image_name), 'w+') as f: # This is how minecraft uses animations
                f.write('{ "animation": { } }')

            print('Overrided {}'.format(image_name))
            print('Created {}.mcmeta'.format(image_name))

    else: # This code will run if the custom_data parameter is passed
        coordinates = custom_data[0] # Another array of coordinates for the start and finish of the custom animation

        # Gets the scale of the image to 256, So if the image resolution was 256 then the scale would be 1
        scale = int(img.shape[0] / custom_data[1]) # This is important for the pixels inside. I still cannot figure out why they aren't linear with the scale.

        custom_name = custom_data[2]

        if scale == 1:
            x = coordinates[0] # Starting points
            y = coordinates[1]

            width = abs(coordinates[2] - x) # These cannot be intepreted at x and y coordinates. this is the distance between x and y
            height = abs(coordinates[3] - y) # So say x = 0 and width = 2 well then it would grab 2 pixels in front of the x pixel

        else:
            x = coordinates[0] * scale # Simply multiplies the coordinates with the scale so that it still gets the same target
            y = coordinates[1] * scale 

            width = abs(coordinates[2] - x) * scale + scale # I dont know why I have to add by the scale here, but I do, and I'm not going to ask
            height = abs(coordinates[3] - y) * scale + scale

        custom_img = img[y: height + y, x: width + x] # Slices the image, the reason I do the height + y is because those are the true ending coordinates.

        for frame in range(r):
            if frame == 0:
                chromas = modify_hue(custom_img, current_mod)
            
            else:
                new_chroma = modify_hue(custom_img, current_mod)
                chromas = cv2.vconcat((new_chroma, chromas))

            current_mod += mod

        cv2.imwrite(f'{optifine_anim_path}{custom_name}', chromas)

        with open(f'{optifine_anim_path}{custom_name}.properties', 'w+') as f:
            f.write('x={}\n'.format(x) +
                    'y={}\n'.format(y) +
                    'w={}\n'.format(width) +
                    'h={}\n'.format(height) +
                    'from={}\n'.format(f'./{custom_name}') +
                    'to={}'.format(image_path[30:]))

        print(f'Created {optifine_anim_path}{custom_name}')
        print(f'Created {optifine_anim_path}{custom_name}.properties')
