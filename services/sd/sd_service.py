#  Copyright © [2024] 程序那些事
#
#  All rights reserved. This software and associated documentation files (the "Software") are provided for personal and educational use only. Commercial use of the Software is strictly prohibited unless explicit permission is obtained from the author.
#
#  Permission is hereby granted to any person to use, copy, and modify the Software for non-commercial purposes, provided that the following conditions are met:
#
#  1. The original copyright notice and this permission notice must be included in all copies or substantial portions of the Software.
#  2. Modifications, if any, must retain the original copyright information and must not imply that the modified version is an official version of the Software.
#  3. Any distribution of the Software or its modifications must retain the original copyright notice and include this permission notice.
#
#  For commercial use, including but not limited to selling, distributing, or using the Software as part of any commercial product or service, you must obtain explicit authorization from the author.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Author: 程序那些事
#  email: flydean@163.com
#  Website: [www.flydean.com](http://www.flydean.com)
#  GitHub: [https://github.com/ddean2009/MoneyPrinterPlus](https://github.com/ddean2009/MoneyPrinterPlus)
#
#  All rights reserved.
#
#

import os

import streamlit as st

from config.config import my_config
from services.llm.llm_provider import get_llm_provider
from services.sd import webuiapi
from tools.file_utils import split_text
from tools.utils import must_have_value, random_with_system_time

text_min_length = 10
DEFAULT_NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, deformed, bad anatomy, watermark, text, logo"
)

# work 目录：保存 SD 生成的图片
script_dir = os.path.dirname(os.path.abspath(__file__))
work_output_dir = os.path.abspath(os.path.join(script_dir, "../../work"))


class SDService:
    def __init__(self):
        self.base_url = my_config['resource'].get('stableDiffusion', {}).get("server_address", "")
        must_have_value(self.base_url, "请设置Stable diffusion的地址")
        self.base_url = self._normalize_base_url(self.base_url)
        self.user_name = my_config['resource'].get('stableDiffusion', {}).get("user_name", "")
        self.password = my_config['resource'].get('stableDiffusion', {}).get("password", "")
        if self.user_name is not None and self.password is not None and self.user_name != "" and self.password != "":
            self.api = webuiapi.WebUIApi(baseurl=self.base_url, username=self.user_name, password=self.password)
        else:
            self.api = webuiapi.WebUIApi(baseurl=self.base_url)

    @staticmethod
    def _normalize_base_url(url: str) -> str:
        """允许填写 http://127.0.0.1:7860，自动补全 /sdapi/v1。"""
        url = (url or "").strip().rstrip("/")
        if url and not url.endswith("/sdapi/v1"):
            url = url + "/sdapi/v1"
        return url

    def sd_get_video_list(self, video_content):
        """
        按文案分段 → LLM 转 SD prompt → 生图并落盘。
        返回: (image_path_list, text_segment_list)
        """
        os.makedirs(work_output_dir, exist_ok=True)

        text_list = split_text(video_content, text_min_length)
        if not text_list:
            text_list = [video_content.strip()] if video_content and video_content.strip() else []
        if not text_list:
            st.toast("视频文案为空，无法生图", icon="⚠️")
            st.stop()

        neg_prompt = st.session_state.get("sd_negative_prompt") or DEFAULT_NEGATIVE_PROMPT
        width = max(64, int(st.session_state.get("sd_width") or 720) // 8 * 8)
        height = max(64, int(st.session_state.get("sd_height") or 1280) // 8 * 8)
        sampler_name = st.session_state.get("sd_sample") or None
        if sampler_name and str(sampler_name).startswith("("):
            sampler_name = None
        steps = int(st.session_state.get("sd_step") or 20)
        scheduler = st.session_state.get("sd_schedule") or None
        if scheduler and str(scheduler).startswith("("):
            scheduler = None
        cfg_scale = float(st.session_state.get("sd_cfg_scale") or 7.0)
        try:
            seed = int(st.session_state.get("sd_seed") or -1)
        except (TypeError, ValueError):
            seed = -1

        checkpoint = st.session_state.get("sd_checkpoint")
        if checkpoint and not str(checkpoint).startswith("("):
            print("set SD checkpoint:", checkpoint)
            self.set_checkpoint(checkpoint)

        llm_provider = my_config['llm']['provider']
        print("llm_provider:", llm_provider)
        llm_service = get_llm_provider(llm_provider)

        image_path_list = []
        for i, topic in enumerate(text_list):
            print(f"SD generate [{i + 1}/{len(text_list)}]: {topic[:40]}...")
            sd_prompt = llm_service.generate_content(topic, llm_service.sd_prompt_template)
            print("sd_prompt:", sd_prompt)

            kwargs = {
                "prompt": sd_prompt,
                "negative_prompt": neg_prompt,
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "seed": seed,
            }
            if sampler_name:
                kwargs["sampler_name"] = sampler_name
            if scheduler:
                kwargs["scheduler"] = scheduler

            try:
                webuiapi_result = self.api.txt2img(**kwargs)
            except Exception as e:
                print(f"SD txt2img error: {e}")
                st.toast(f"第 {i + 1} 段生图失败: {e}", icon="⚠️")
                st.stop()
            if not webuiapi_result.images:
                st.toast(f"第 {i + 1} 段生图失败，未返回图片", icon="⚠️")
                st.stop()

            image = webuiapi_result.images[0]
            image_path = os.path.join(work_output_dir, f"sd_{random_with_system_time()}_{i}.png")
            image.save(image_path)
            print("saved SD image:", image_path)
            image_path_list.append(image_path)

        return image_path_list, text_list

    def set_checkpoint(self, checkpoint_name):
        self.api.util_set_model(checkpoint_name)

    def get_checkpoints(self):
        try:
            checkpoints = self.api.util_get_model_names()
        except Exception as e:
            print(f"SD发生了一个错误: {e}")
            checkpoints = []
        return checkpoints

    def get_samples(self):
        try:
            samples = self.api.util_get_sampler_names()
        except Exception as e:
            print(f"SD发生了一个错误: {e}")
            samples = []

        return samples

    def get_schedulers(self):
        try:
            schedulers = self.api.util_get_scheduler_names()
        except Exception as e:
            print(f"SD发生了一个错误: {e}")
            schedulers = []
        return schedulers

    def text_2_img(self, prompt, negative_prompt, width, height, steps, sampler_name, scheduler, cfg_scale, seed):
        return self.api.txt2img(prompt=prompt, negative_prompt=negative_prompt,
                                width=width, height=height,
                                sampler_name=sampler_name,
                                scheduler=scheduler,
                                steps=steps, cfg_scale=cfg_scale, seed=seed)
