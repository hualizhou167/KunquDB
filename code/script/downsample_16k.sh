#!/bin/bash
###
 # @Author: hualizhou167 zhouHLzhou@163.com
 # @Date: 2024-01-20 11:10:46
 # @LastEditors: hualizhou167 zhouHLzhou@163.com
 # @LastEditTime: 2024-03-27 18:31:41
 # @FilePath: /kunopera-ASV/release/script/down_sample_16k.sh
 # @Description: 
 # 
 # Copyright (c) 2024 by Huali Zhou, All Rights Reserved.
### 

# 输入目录
export input_dir="data/seg_wavs_spleeter"

# 输出目录
export output_dir="data/wavs_16k_ffmpeg"

# 设置目标采样率和通道数
export target_sample_rate=16000
export target_channels=1

# 指定并行任务数
num_parallel_jobs=64


# 处理函数，使用 FFmpeg 进行重采样
downsample_16k() {
  input_file="$1"
  output_file="$2"
  mkdir -p "$(dirname "$output_file")"
  # 使用 FFmpeg 进行重采样，并将输出重定向到文件
  ffmpeg -i "$input_file" -ar $target_sample_rate -ac $target_channels -y -loglevel 1 "$output_file" > downsample_16k.log 2>&1
  # 检查命令是否成功执行
  if [ $? -ne 0 ]; then
    echo "FFmpeg command failed. Check downsample_16k.log for details."
  fi
}


export -f downsample_16k

# 获取所有匹配的文件列表
files=()
while IFS= read -r -d $'\0'; do
  files+=("$REPLY")
done < <(find "$input_dir" -name "*.wav" -type f -print0)
echo "Number of files: ${#files[@]}"


# 使用 xargs 执行 Ffmpeg 命令并进行重采样
printf "%s\0" "${files[@]}" | xargs -0 -n 1 -P "$num_parallel_jobs" -I {} \
  bash -c 'input_file="$0"; output_file="${input_file/$input_dir/$output_dir}"; downsample_16k "$input_file" "$output_file"' {}


echo "Downsampling complete."
