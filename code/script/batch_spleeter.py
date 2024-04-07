import concurrent.futures
import logging
import os
import subprocess
from datetime import datetime
import shutil
import glob
from tqdm import tqdm

# 设置日志配置，以写模式打开文件（如果存在，则截断文件）
timestamp = datetime.now().strftime("%y%m%d-%H%M")
logging.basicConfig(
    filename=f"spleeter_{timestamp}.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def spleeter_mini_batch(input_folder, output_folder, start_idx, end_idx):
    input_folder = os.path.abspath(input_folder)
    output_folder = os.path.abspath(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    wav_files = sorted([x for x in os.listdir(input_folder) if x.endswith(".wav")])[
        start_idx:end_idx
    ]

    logging.info(
        f"Processing [{start_idx}/{end_idx}], {len(wav_files)} wav files under {input_folder}"
    )
    # Construct the command to run Spleeter in Docker
    # "--user", f"{user_id}:{group_id}",
    docker_command = [
        "docker",
        "run",
        "--rm",  # 进程结束时自动rm容器
        # "--gpus",
        # "0,1,2,3,4,5,6",  # Adjust as needed
        "-v",
        f"{input_folder}:/input",
        "-v",
        f"{output_folder}:/output",
        "deezer/spleeter:3.8-5stems",
        "separate",
        "-d",
        "6400",
        "-p",
        "spleeter:5stems",
        "-o",
        "/output",
    ] + [f"/input/{wav}" for wav in wav_files]
    try:
        print(docker_command)
        with subprocess.Popen(
            docker_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ) as process:
            stdout, stderr = process.communicate()
            # 将子进程输出记录到日志中
            if stdout:
                logging.info("Spleeter Output:\n" + stdout)
            if stderr:
                logging.error("Spleeter Error:\n" + stderr)
    except Exception as e:
        # 捕获异常，并记录异常信息到日志
        logging.error(f"Error during processing: {str(e)}")


def spleeter_wavs_one_video(input_folder, output_folder, num_proc, batch_size=30):
    """
    num_proc: spleeter_mini_batch同时执行的最大进程数
    batch_size: 每次spleeter_mini_batch执行处理的最大文件数量
    """
    total_num = len(os.listdir(input_folder))
    # 准备每个小批次的参数集合
    args_list = [
        (input_folder, output_folder, start_idx, min(start_idx + batch_size, total_num))
        for start_idx in range(0, total_num, batch_size)
    ]

    # 使用 ProcessPoolExecutor 并行执行每个小批次

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_proc) as executor:
        # 使用 submit 提交任务
        futures = [executor.submit(spleeter_mini_batch, *args) for args in args_list]

        # 使用 wait 检查任务状态
        done, not_done = concurrent.futures.wait(futures)

        # 输出任务状态和异常信息
        for future in done:
            try:
                future.result()
            except Exception as e:
                logging.error(f"Task failed with exception: {e}")


def get_process_num(percentage=0.5):
    # 获取系统核心数
    num_cores = os.cpu_count()
    # 计算 num_proc
    num_proc = max(int(num_cores * percentage), 1)
    return num_proc


def organize_result_vocals(src_root, tgt_root):
    """need to customize glob.glob pattern string for all vocal files"""
    vocal_wavs = glob.glob(f"{src_root}/*/*/vocals.wav")
    print(len(vocal_wavs), vocal_wavs)
    for x in tqdm(vocal_wavs):
        wav_dir_path = "/".join(x.split("/")[:-2]).replace(src_root, tgt_root)
        wav_src_name = x.split("/")[-2]
        tgt_path = os.path.join(wav_dir_path, f"{wav_src_name}.wav")
        print(tgt_path)
        os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
        # 复制文件并重命名
        shutil.copy(x, tgt_path)


def stage_01():
    wav_root = "data/seg_wavs"
    prefix_ori, prefix_tgt = "seg_wavs", "seg_wavs_spleeter_ori"
    input_folders = sorted(glob.glob(f"{wav_root}/*"))
    num_proc = get_process_num()
    logging.info(f"Num process: {num_proc}")
    for input_folder in input_folders:
        logging.info(f"Start to run spleeter for: {input_folder}")
        output_folder = input_folder.replace(prefix_ori, prefix_tgt)
        spleeter_wavs_one_video(input_folder, output_folder, num_proc, batch_size=30)
        logging.info(f"Complete spleeter running for: {input_folder}")


def stage_02():
    src_root = "data/seg_wavs_spleeter_ori"
    tgt_root = "data/seg_wavs_spleeter"
    organize_result_vocals(src_root, tgt_root)


if __name__ == "__main__":
    stage_01()
    stage_02()
