"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""

KEY_STEP = '1. In the ComfyUI menu, open **Extensions**, then **KIE**, then **KIE Settings**, and save your key.\n'
RECOVER_NOTE = (
    'KIE has no cancel. If you cancel the run, ComfyUI stops waiting, but KIE still makes the video and bills it. '
    'Collect it with **video-03-recover-a-video**.'
)

WORKFLOW_TEXTS = {
    'image-01-design-a-host': {
        'input': (
            KEY_STEP + '2. Describe your host in **Host**: how they look and what they wear.\n'
            '3. Press **Run**. Both images go to `image/kie`.'
        ),
        'design': (
            'Nano Banana Pro draws the host from the waist up. `aspect_ratio` is set to `custom` and `3:4`, so the '
            'picture is a portrait. A setting left at `default` sends nothing, and the model uses its own value.\n\n'
            'To draw with another model, open **Design** and type another `model`, its ID on kie.ai/market.'
        ),
        'design_description': 'Draws the host and saves the image.',
        'turn': (
            '**File: Add** passes the link of the host image to the next model as `image_input`, the input where Nano '
            'Banana Pro takes the images to edit. Nothing goes up again. Nano Banana Pro then draws the same person '
            'waving.\n\n'
            'Change the prompt in **Turn** to pose the host another way.'
        ),
        'turn_description': 'Draws the same host waving and saves the image.',
    },
    'image-02-cut-out-a-product': {
        'input': (
            KEY_STEP + '2. Describe the product in **Product**.\n'
            '3. Press **Run**. The enlarged photo and the transparent cut-out go to `image/kie`.'
        ),
        'photo': (
            'Qwen Image draws the product photo. `guidance_scale` and `num_inference_steps` are set to `custom`: a '
            'higher guidance follows the prompt more closely, and more steps take longer and often look finer. '
            '`negative_prompt` keeps text and people out. `image_size` goes in `arguments`, under the name Qwen '
            'gives it.\n\n'
            'To start from your own photo, add **Load Image** and connect it to the `files` input of **Upscale**. The '
            'node uploads it for the model.'
        ),
        'photo_description': 'Draws the product photo.',
        'upscale': (
            '**File: Add** gives Recraft Crisp Upscale the photo as `image`, its only input. It enlarges the photo and '
            'keeps the edges sharp, with no settings to choose.'
        ),
        'upscale_description': 'Enlarges the product photo and saves it.',
        'cut_out': (
            'Recraft removes the background and returns a PNG with a clear background. **Image: Generate** gives each '
            'image a mask from its transparency. **Get Item From List** takes the image and its mask, and **Join '
            'Image with Alpha** puts the transparency back, so the saved PNG keeps a clear background.'
        ),
        'cut_out_description': 'Cuts out the product and saves it with a clear background.',
    },
    'image-03-make-a-poster-series': {
        'input': (KEY_STEP + '2. Describe the poster in **Brief**.\n3. Press **Run**. Four posters go to `image/kie`.'),
        'model': (
            '**Model: Info** shows what KIE says a model takes: each input by the name KIE gives it, its choices, and '
            'its limits. It sends no task and bills nothing. **Info** shows FLUX 3 Klein. A setting it lists can go '
            'in a named setting of the node, or in `arguments`.'
        ),
        'series': (
            'FLUX 3 Klein draws four versions of the poster. `num_images` is set to `custom` and `4`, and `seed` to '
            '`custom` and a fixed number, so a run with the same brief repeats the same four posters. KIE bills each '
            'poster.'
        ),
        'series_description': 'Draws four posters and saves them.',
    },
    'audio-01-voice-a-script': {
        'input': (
            KEY_STEP + '2. Write what the host says in **Script**.\n3. Press **Run**. The voice goes to `audio/kie`.'
        ),
        'speak': (
            'ElevenLabs Turbo 2.5 reads the script aloud. The script goes in `text`, the input where ElevenLabs '
            'takes its words, and `voice` names the voice by its ElevenLabs ID. **Model: Info** lists the voices and '
            'every other input it takes, such as `speed`, which goes in `arguments`.'
        ),
        'speak_description': 'Reads the script aloud and saves the voice.',
    },
    'audio-02-write-a-song': {
        'input': (
            KEY_STEP + '2. Describe the song in **Song**: its style, its mood, and what it is about.\n'
            '3. Press **Run**. Suno makes two versions, and both go to `audio/kie`.'
        ),
        'compose': (
            'Suno writes the lyrics and the music from **Song**. `arguments` holds the inputs Suno needs by its own '
            'names: `"custom_mode": false` lets Suno write the lyrics, and `"model"` picks the Suno version. `voice` '
            'is empty, because Suno takes no voice ID.'
        ),
        'compose_description': 'Writes the song and saves both versions.',
    },
    'video-01-animate-a-photo': {
        'input': (KEY_STEP + '2. Describe your host in **Host**.\n3. Press **Run**. The video goes to `video/kie`.'),
        'portrait': (
            'Z-Image draws the host in a vertical frame. This image becomes the first frame of the video. `files` '
            'passes its link on to **Animate**, so nothing goes up again.'
        ),
        'portrait_description': 'Draws the host.',
        'animate': (
            '**File: Add** gives Wan 3.0 the host as `first_frame_url`. Wan starts on the host and makes a five-second '
            'video at 480P. `resolution` is set to `custom`, because Wan makes 1080P by default. Wan names its sound '
            'switch `audio`, so `"audio": false` goes in `arguments`.\n\n' + RECOVER_NOTE
        ),
        'animate_description': 'Turns the host into a video and saves it.',
    },
    'video-02-show-a-product-with-a-voice': {
        'input': (
            KEY_STEP + '2. Describe the product in **Product**, and write what the host says in **Line**.\n'
            '3. Press **Run**. The video goes to `video/kie`.'
        ),
        'photo': (
            'Qwen Image draws the product, as in **image-02-cut-out-a-product**. `files` passes its link on to '
            '**Film**.'
        ),
        'voice': (
            'ElevenLabs Turbo 2.5 reads the line aloud. `files` passes the link of the clip on to **Film**, so it '
            'does not go up again.'
        ),
        'voice_description': 'Reads the line aloud.',
        'film': (
            'Two **File: Add** nodes give Wan 3.0 the product as `reference_image_urls` and the voice as '
            '`reference_audio_urls`. Both inputs take a list, and the node sends a list even for one file. Wan then '
            'shows a host who holds the product and says the line.\n\n' + RECOVER_NOTE
        ),
        'film_description': 'Films the product with the voice and saves the video.',
    },
    'video-03-recover-a-video': {
        'recover': (
            'KIE has no cancel. A video task that ran on after a cancel, or past the request timeout, keeps a record '
            'on this computer for 14 days.\n\n'
            '1. Choose the task in **Task: Download**. Press R to list tasks recorded later.\n'
            '2. Press **Run**. The video goes to `video/kie`, and the record goes away.\n\n'
            'Collecting a task is free.'
        ),
    },
    'chat-01-write-a-product-listing': {
        'input': (
            KEY_STEP + '2. Load a product photo in **Front View**.\n'
            '3. Put a PDF or text file with the product facts in the input folder of ComfyUI, and choose it in '
            '**Spec**. Press R to list a file you just added.\n'
            '4. Press **Run**. The listing goes to `text/kie` as JSON.'
        ),
        'listing': (
            'GPT 6 Luna reads the photo and the spec, and writes a listing as JSON. `json_schema` holds the shape of '
            'the answer: a name, a schema, and `strict`, sent as written. Only GPT models read a PDF; a text file '
            'goes to any model.'
        ),
        'listing_description': 'Writes the listing as JSON from the photo and the spec.',
    },
    'chat-02-write-a-host-script': {
        'input': (
            KEY_STEP + '2. Load a product photo in **Front View**.\n3. Press **Run**. The script goes to `text/kie`.'
        ),
        'facts': (
            'Gemini 3.8 Flash lists what a shopper can see in the photo. `reasoning_effort` is set to `low`, so it '
            'answers quickly. Its `conversation` output carries the question and the answer on to the next step.'
        ),
        'facts_description': 'Lists the facts a shopper can see in the photo.',
        'host_script': (
            'GPT 6 Luna continues the same conversation and writes a 30-second script from those facts. '
            '`system_prompt` tells it to write as a warm live-shopping host. A conversation can move between models '
            'and formats; each Chat: Ask sends every earlier turn.'
        ),
        'host_script_description': 'Writes the host script from the facts.',
    },
}

__all__ = ['WORKFLOW_TEXTS']
