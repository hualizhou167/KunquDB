###
 # @Author: hualizhou167 zhouHLzhou@163.com
 # @Date: 2024-03-27 17:38:34
 # @LastEditors: hualizhou167 zhouHLzhou@163.com
 # @LastEditTime: 2024-03-27 18:18:55
 # @FilePath: /kunopera-ASV/release/script/extract_audio_from_video.sh
 # @Description: 
 # 
 # Copyright (c) 2024 by Huali Zhou, All Rights Reserved.
### 

# 输入目录
export input_dir="data/seg_videos"

# 输出目录
export output_dir="data/seg_wavs"

# 指定并行任务数
num_parallel_jobs=32

# 处理函数，使用 FFmpeg
extract_audio() {
  input_file="$1"
  output_file="$2"
  mkdir -p "$(dirname "$output_file")"

  ffmpeg -i "$input_file" -vn -acodec pcm_s16le -ar 48000 -ac 2 -y -loglevel 1 "$output_file" > extract_audio.log 2>&1
  # 检查命令是否成功执行
  if [ $? -ne 0 ]; then
    echo "FFmpeg command failed. Check extract_audio.log for details."
  fi
}

export -f extract_audio


# 获取所有匹配的文件列表
files=()
while IFS= read -r -d $'\0'; do
  files+=("$REPLY")
done < <(find "$input_dir" -name "*.mp4" -type f -print0)
echo "Number of files: ${#files[@]}"

# 使用 xargs 执行 Ffmpeg 命令并进行重采样
printf "%s\0" "${files[@]}" | xargs -0 -n 1 -P "$num_parallel_jobs" -I {} \
  bash -c 'input_file="$0"; output_file="${input_file/$input_dir/$output_dir}"; output_file="${output_file//.mp4/.wav}"; extract_audio "$input_file" "$output_file"' {}


echo "Extracting audio finished."

