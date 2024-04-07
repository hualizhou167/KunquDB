# provided data
- `KunquDB.csv` is our meta annotatin dataset, formatted in CSV file, structured per dialogue line, containing all annotations.
- `id_to_video.json` is a mapping from the video ID to the video name.
- `perfm_role_chars_gender.csv` is structured by performer, with character names and corresponding role type.

# source data
The [book purchase](http://www.awpub.com/front/book/10-858) grants access to the digital source video data in a supplementary disc. You're advised to organize it as follows:
```
raw/Kunopera/
│
├── Audio/
│
├── Begining/
│
├── BeginingXP/
│
└── Video/
    ├── -01本戲精選/
    │   ├── video01.mp4
    │   └── video02.mp4
    ├── -02折子戲精粹/
    │   ├── video001.mp4
    │   └── video002.mp4
    └── -03教學資料粹存/

```

# pipeline
The source data should be located under the `raw` directory, while the processed data will be placed under `data`.
1. Run `script/segment_video.py` to segment the video.
2. Run `script/extract_audio_from_video.sh` to extract audio from video.
3. Run `script/batch_spleeter.py` to isolate background music using Spleeter.
4. Run `script/downsample_16k.sh` to downsample to 16kHz.
