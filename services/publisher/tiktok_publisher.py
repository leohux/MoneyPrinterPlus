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

from config.config import tiktok_site
from services.publisher.publisher_helpers import (
    build_title_and_caption,
    find_first,
    maybe_publish,
    open_new_tab,
    paste_into,
    upload_via_file_input,
)


def tiktok_publisher(driver, video_file, text_file):
    print("tiktok publisher start")
    open_new_tab(driver, tiktok_site)
    upload_via_file_input(driver, video_file)
    time.sleep(6)

    _, _, _, caption = build_title_and_caption("tiktok", text_file, title_limit=150)
    editor = find_first(
        driver,
        [
            '//div[@data-e2e="caption_container"]//div[@contenteditable="true"]',
            '//div[contains(@class,"DraftEditor-root")]//div[@contenteditable="true"]',
            '//div[@contenteditable="true" and @role="textbox"]',
            '//div[@contenteditable="true"]',
        ],
        timeout=50,
    )
    paste_into(driver, editor, caption)
    time.sleep(2)

    maybe_publish(
        driver,
        [
            '//button[@data-e2e="post_video_button"]',
            '//button[contains(@class,"btn-post")]',
            '//div[contains(@class,"btn-post")]',
            '//button[normalize-space()="Post"]',
            '//button[normalize-space()="发布"]',
        ],
    )
    print("tiktok publisher done")
