import subprocess
import multiprocessing
import pandas as pd
import json
import os
import time
# from datetime import datetime, timedelta
from functools import partial


def map_id_to_name(json_fn):
    with open(json_fn, "r", encoding="utf-8") as f:
        id_to_name = json.load(f)
    return id_to_name


def format_time(time_str):
    # "0 days 00:00:05.519000" or "0 days 00:00:46"
    # Convert the time string to timedelta object
    time_delta = pd.to_timedelta(time_str)
    # Extract hours, minutes, seconds, and milliseconds
    hours = time_delta.components.hours
    minutes = time_delta.components.minutes
    seconds = time_delta.components.seconds
    milliseconds = time_delta.components.milliseconds
    # Format the time string
    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
    return formatted_time


def ffmpeg_video(input_file, output_file, start_time, end_time):
    # ffmpeg -i "$input_file" -ss "$start_time" -to "$end_time" -c:v copy -c:a copy "$output_file"
    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        input_file,
        "-ss",
        start_time,
        "-to",
        end_time,
        "-c:v",
        "copy",
        "-c:a",
        "copy",
        # "-loglevel",
        # "quiet",
        output_file,
    ]
    # '-vn',  '-ar', 48000,  '-ac', 2, '-y'
    print(" ".join(ffmpeg_cmd))
    try:
        subprocess.run(ffmpeg_cmd)
    except subprocess.CalledProcessError as e:
        print("Error:", e)


def seg_one_play(id_to_name, raw_dir, output_dir, video_id, group_data):
    source_fn = os.path.join(
        raw_dir,
        "-02折子戲精粹" if len(video_id) == 3 else "-01本戲精選",
        f"{id_to_name[video_id]}.mp4",
    )
    cur_seg_root = os.path.join(output_dir, f"play#{video_id}")
    os.makedirs(cur_seg_root, exist_ok=True)

    import traceback  # 导入用于输出异常堆栈信息的模块
    for _, row in group_data.iterrows():
        output_fn = os.path.join(cur_seg_root, f"{row['wav_id'].zfill(4)}.mp4")
        try:
            ffmpeg_video(
                source_fn,
                output_fn,
                format_time(row["start"]),
                format_time(row["end"]),
            )
        except Exception as e:
            print(f"An error occurred when processing {video_id} {row['wav_id']}: {e}")
            # 输出异常堆栈信息
            traceback.print_exc()
            continue  # 捕获异常后继续迭代


def seg_batch(meta_csv, id_to_name_fn, raw_dir, output_dir, num_processes):
    df_meta = pd.read_csv(meta_csv, dtype=str)
    df_grouped = df_meta.groupby("video_id")
    df_grouped_list = [(video_id, group_data) for video_id, group_data in df_grouped]
    df_grouped_list_sorted = sorted(df_grouped_list, key=lambda x: len(x[1]))

    id_to_name = map_id_to_name(id_to_name_fn)

    if num_processes is None:
        num_processes = int(0.7 * multiprocessing.cpu_count())
    chunks = [
        df_grouped_list_sorted[i: i + num_processes]
        for i in range(0, len(df_grouped_list_sorted), num_processes)
    ]
    pool = multiprocessing.Pool(processes=num_processes)
    for chunk in chunks:
        for video_id, group_data in chunk:
            pool.apply_async(
                partial(seg_one_play, id_to_name, raw_dir, output_dir),
                args=(
                    video_id,
                    group_data,
                ),
            )
    pool.close()
    pool.join()


def main():
    id_to_name_fn = "id_to_video.json"
    meta_csv = "test_meta.csv"  # "KunquDB.csv"
    raw_dir = "raw/Kunopera/Video"
    output_dir = "data/seg_videos"
    os.makedirs(output_dir, exist_ok=True)
    num_processes = None

    startTime = time.time()
    seg_batch(meta_csv, id_to_name_fn, raw_dir, output_dir, num_processes)
    print(
        "============Segementation completed! \nTook "
        + str(time.time() - startTime)
        + "s.============"
    )


if __name__ == "__main__":
    main()
