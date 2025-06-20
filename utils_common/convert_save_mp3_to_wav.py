import os
from datetime import datetime

from pydub import AudioSegment

from utils_common.normalized_path import get_full_file_normal_path


def convert_and_save_mp3_to_wav(
        mp3_full_path: str,
        wav_frame_rate: int = 16000,
        wav_channels: int = 1,
        temp_str: str = "temp"
) -> str | None:
    cur_dir_name = os.path.dirname(mp3_full_path)
    cur_mp3_name_with_ext = os.path.basename(mp3_full_path)
    cur_mp3_name_no_ext = os.path.splitext(cur_mp3_name_with_ext)[0]

    temp_id_str = datetime.now().strftime("%M%S%f")
    new_wav_name_no_ext = f"{cur_mp3_name_no_ext}_{temp_str}_{temp_id_str}"
    new_wav_name = f"{new_wav_name_no_ext}.wav"
    new_wav_full_path = get_full_file_normal_path(
        all_dir_str_parts=[cur_dir_name, ],
        file_name_with_ext=new_wav_name)

    try:
        mp3_audio = AudioSegment.from_mp3(mp3_full_path)
        mp3_frame_rate = mp3_audio.frame_rate
        mp3_channels = mp3_audio.channels
        mp3_sample_width = mp3_audio.sample_width
        mp3_bitrate = mp3_frame_rate * (mp3_sample_width * 8) * mp3_channels
        print(f"File MP3 parameters: \t"
              f"frame_rate: {mp3_frame_rate} \t"
              f"channels: {mp3_channels} \t"
              f"sample_width: {mp3_sample_width} \t"
              f"bitrate: {mp3_bitrate}")

        if mp3_frame_rate != wav_frame_rate:
            mp3_audio = mp3_audio.set_frame_rate(wav_frame_rate)

        if mp3_channels != wav_channels:
            mp3_audio = mp3_audio.set_channels(wav_channels)

        mp3_audio.export(new_wav_full_path, format="wav")

        wav_audio = AudioSegment.from_wav(new_wav_full_path)
        wav_frame_rate = wav_audio.frame_rate
        wav_channels = wav_audio.channels
        wav_sample_width = wav_audio.sample_width
        wav_bitrate = wav_frame_rate * (wav_sample_width * 8) * wav_channels
        print(f"File WAV parameters: \t"
              f"frame_rate: {wav_frame_rate} \t"
              f"channels: {wav_channels} \t"
              f"sample_width: {wav_sample_width} \t"
              f"bitrate: {wav_bitrate}")
        return new_wav_full_path
    except Exception as error:
        print(f"File mp3 not converted to wav [ERROR]: error: {error}")


async def async_convert_and_save_mp3_to_wav(
        mp3_full_path: str,
        wav_frame_rate: int = 16000,
        wav_channels: int = 1,
        temp_str: str = "temp"
) -> str | None:
    cur_dir_name = os.path.dirname(mp3_full_path)
    cur_mp3_name_with_ext = os.path.basename(mp3_full_path)
    cur_mp3_name_no_ext = os.path.splitext(cur_mp3_name_with_ext)[0]

    temp_id_str = datetime.now().strftime("%M%S%f")
    new_wav_name_no_ext = f"{cur_mp3_name_no_ext}_{temp_str}_{temp_id_str}"
    new_wav_name = f"{new_wav_name_no_ext}.wav"
    new_wav_full_path = get_full_file_normal_path(
        all_dir_str_parts=[cur_dir_name, ],
        file_name_with_ext=new_wav_name)

    try:
        mp3_audio = AudioSegment.from_mp3(mp3_full_path)
        mp3_frame_rate = mp3_audio.frame_rate
        mp3_channels = mp3_audio.channels
        mp3_sample_width = mp3_audio.sample_width
        mp3_bitrate = mp3_frame_rate * (mp3_sample_width * 8) * mp3_channels
        print(f"File MP3 parameters: \t"
              f"frame_rate: {mp3_frame_rate} \t"
              f"channels: {mp3_channels} \t"
              f"sample_width: {mp3_sample_width} \t"
              f"bitrate: {mp3_bitrate}")

        if mp3_frame_rate != wav_frame_rate:
            mp3_audio = mp3_audio.set_frame_rate(wav_frame_rate)

        if mp3_channels != wav_channels:
            mp3_audio = mp3_audio.set_channels(wav_channels)

        mp3_audio.export(new_wav_full_path, format="wav")

        wav_audio = AudioSegment.from_wav(new_wav_full_path)
        wav_frame_rate = wav_audio.frame_rate
        wav_channels = wav_audio.channels
        wav_sample_width = wav_audio.sample_width
        wav_bitrate = wav_frame_rate * (wav_sample_width * 8) * wav_channels
        print(f"File WAV parameters: \t"
              f"frame_rate: {wav_frame_rate} \t"
              f"channels: {wav_channels} \t"
              f"sample_width: {wav_sample_width} \t"
              f"bitrate: {wav_bitrate}")
        return new_wav_full_path
    except Exception as error:
        print(f"File mp3 not converted to wav [ERROR]: error: {error}")
