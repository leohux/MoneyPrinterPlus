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

import time

from config.config import youtube_site
from services.publisher.publisher_helpers import (
    build_title_and_caption,
    click_first,
    find_first,
    maybe_publish,
    open_new_tab,
    paste_into,
    try_click_texts,
    upload_via_file_input,
)


def youtube_publisher(driver, video_file, text_file):
    print("youtube publisher start")
    open_new_tab(driver, youtube_site)
    time.sleep(4)

    try_click_texts(driver, ["Create", "创建", "建立"], timeout=4)
    try_click_texts(driver, ["Upload videos", "Upload video", "上传视频", "上傳影片"], timeout=4)

    upload_via_file_input(driver, video_file)
    time.sleep(6)

    title, body, hashtags, _ = build_title_and_caption("youtube", text_file, title_limit=100)
    title_box = find_first(
        driver,
        [
            '//*[@id="title-textarea"]//div[@id="textbox"]',
            '//ytcp-social-suggestions-textbox[@id="title-textarea"]//div[@id="textbox"]',
            '//div[@id="textbox" and (@aria-label or @contenteditable="true")]',
        ],
        timeout=60,
    )
    paste_into(driver, title_box, title)

    try:
        desc_box = find_first(
            driver,
            [
                '//*[@id="description-textarea"]//div[@id="textbox"]',
                '//ytcp-social-suggestions-textbox[@id="description-textarea"]//div[@id="textbox"]',
            ],
            timeout=8,
        )
        paste_into(driver, desc_box, "\n".join(part for part in [body, hashtags] if part))
    except Exception as e:
        print("youtube description skip:", e)

    try:
        click_first(
            driver,
            [
                '//tp-yt-paper-radio-button[@name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]',
                '//*[@name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]',
            ],
            timeout=8,
        )
    except Exception:
        try_click_texts(
            driver,
            ["No, it's not made for kids", "No, this video is not made for kids", "否，内容不是面向儿童"],
            timeout=4,
        )

    for _ in range(3):
        try:
            click_first(driver, ['//*[@id="next-button"]', '//ytcp-button[@id="next-button"]'], timeout=6)
            time.sleep(1.2)
        except Exception:
            if not try_click_texts(driver, ["Next", "下一步"], timeout=3):
                break

    try:
        click_first(
            driver,
            ['//tp-yt-paper-radio-button[@name="PUBLIC"]', '//*[@name="PUBLIC"]'],
            timeout=5,
        )
    except Exception:
        try_click_texts(driver, ["Public", "公开", "公開"], timeout=3)

    maybe_publish(
        driver,
        [
            '//*[@id="done-button"]',
            '//ytcp-button[@id="done-button"]',
            '//ytcp-button[@id="publish-button"]',
        ],
    )
    print("youtube publisher done")
