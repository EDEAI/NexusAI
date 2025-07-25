from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File
import logging
from dify_plugin.config.logger_format import plugin_logger_handler

import asyncio
import websocket
import ssl as pyssl
import json
import os
import time
import io
import wave

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)

class FunasrConnecterTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        host = tool_parameters.get("host", "127.0.0.1")
        port = tool_parameters.get("port", 10095)
        audio_in = tool_parameters.get("audio_in", None)
        mode = tool_parameters.get("mode", "offline")
        chunk_size = tool_parameters.get("chunk_size", "5,10,5")
        use_itn = tool_parameters.get("use_itn", True)
        ssl_enable = tool_parameters.get("ssl", False)
        hotword = tool_parameters.get("hotword", "")
        output_dir = tool_parameters.get("output_dir", None)

        if isinstance(chunk_size, str):
            chunk_size = [int(x) for x in chunk_size.split(",")]


        result = self.record_from_scp(host, port, audio_in, mode, chunk_size, use_itn, ssl_enable, hotword)
        yield self.create_json_message({
            "result": result
        })
        yield self.create_text_message(
            result.get("text", "")
        )

    def record_from_scp(self,host, port, audio_in, mode, chunk_size, use_itn, ssl_enable, hotword):
        global voices
        uri = f"{'wss' if ssl_enable else 'ws'}://{host}:{port}"
        is_finished = False
        chunk_interval = 10

        if isinstance(audio_in, list):
            for audio_file in audio_in:
                sample_rate = 16000
                wav_format = "pcm"

                if audio_file and isinstance(audio_file, File):
                    try:
                        if audio_file.extension == ".pcm":
                            audio_bytes = io.BytesIO(audio_file.blob).read()
                        elif audio_file.extension == ".wav":
                            wav_file = wave.Wave_read(io.BytesIO(audio_file.blob))
                            sample_rate = wav_file.getframerate()
                            frames = wav_file.readframes(wav_file.getnframes())
                            audio_bytes = bytes(frames)
                        else:
                            audio_bytes = io.BytesIO(audio_file.blob).read()
                            wav_format = "others"
                    except Exception as e:
                        logger.error(f"Warning: Could not process audio_in audio: {e}. Proceeding without audio_in.")
                        return(f"Warning: Could not process audio_in audio: {e}. Proceeding without audio_in.")
                    
                wav_name = audio_file.filename

                hotword_msg = ""
                if hotword.strip():
                    try:
                        hotwords = {line.split()[0]: int(line.split()[1]) for line in hotword.strip().splitlines() if len(line.split()) == 2}
                        hotword_msg = json.dumps(hotwords)
                    except Exception as e:
                        logger.error("Invalid hotword format:", e)

                stride = int(60 * chunk_size[1] / chunk_interval / 1000 * sample_rate * 2)
                chunk_num = (len(audio_bytes) - 1) // stride + 1
                # print(stride)

                sslopt = {"cert_reqs": pyssl.CERT_NONE} if ssl_enable else {}
                ws = websocket.create_connection(uri, sslopt=sslopt)

                # send first time
                message = json.dumps({"mode": mode, "chunk_size": chunk_size, "chunk_interval": chunk_interval, "audio_fs":sample_rate,
                            "wav_name": wav_name, "wav_format": wav_format, "is_speaking": True, "hotwords":hotword_msg, "itn": use_itn},ensure_ascii=False).encode('utf-8')
                #voices.put(message)

                logger.info(f"ws send first msg:{message}")
                ws.send(message)
                is_speaking = True
                for i in range(chunk_num):

                    beg = i * stride
                    data = audio_bytes[beg:beg + stride]
                    #voices.put(message)
                    ws.send_binary(data)
                    if i == chunk_num - 1:
                        is_speaking = False
                        message = json.dumps({"is_speaking": is_speaking})
                        #voices.put(message)
                        logger.info(f"ws send msg:{message}")
                        ws.send(message)

                    sleep_duration = 0.001 if mode == "offline" else 60 * chunk_size[1] / chunk_interval / 1000
                
                    time.sleep(sleep_duration)
        
                if not mode=="offline":
                    time.sleep(2)
                # offline model need to wait for message recved
        
                if mode=="offline":
                        time.sleep(1)
                result_received = False
                while not result_received:
                    try:
                        response = ws.recv()
                        result = json.loads(response)
                        logger.info(f"funasr result:{result}")
                        ws.close()
                        return result
                    except Exception as e:
                        print("Error receiving result:", e)
                        return "Error occurred during recognition."
