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

from config.config import instagram_site
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


def instagram_publisher(driver, video_file, text_file):
    print("instagram publisher start")
    open_new_tab(driver, instagram_site)
    time.sleep(3)

    try:
        click_first(
            driver,
            [
                '//svg[@aria-label="New post"]/ancestor::a[1]',
                '//svg[@aria-label="New post"]/ancestor::*[@role="link" or @role="button"][1]',
                '//svg[@aria-label="新帖子"]/ancestor::a[1]',
                '//svg[@aria-label="Create"]/ancestor::a[1]',
                '//span[normalize-space()="Create"]/ancestor::a[1]',
                '//span[normalize-space()="创建"]/ancestor::a[1]',
                '//a[contains(@href,"/create/")]',
            ],
            timeout=10,
        )
        time.sleep(2)
    except Exception as e:
        print("instagram create button skip:", e)

    upload_via_file_input(driver, video_file)
    time.sleep(6)

    try_click_texts(driver, ["OK", "好的", "继续以 Reel 发布", "Continue"], timeout=4)
    for _ in range(2):
        if not try_click_texts(driver, ["Next", "下一步"], timeout=6):
            break
        time.sleep(1.5)

    _, _, _, caption = build_title_and_caption("instagram", text_file, title_limit=150)
    try:
        editor = find_first(
            driver,
            [
                '//div[@aria-label="Write a caption..."]',
                '//div[contains(@aria-label,"Write a caption")]',
                '//div[contains(@aria-label,"说明")]',
                '//div[contains(@aria-label,"标语")]',
                '//div[contains(@aria-label,"caption")]',
                '//div[@contenteditable="true" and @role="textbox"]',
                '//div[@contenteditable="true"]',
            ],
            timeout=15,
        )
        paste_into(driver, editor, caption)
        time.sleep(1)
    except Exception as e:
        print("instagram caption skip:", e)

    maybe_publish(
        driver,
        [
            '//div[@role="button" and normalize-space()="Share"]',
            '//div[@role="button" and normalize-space()="分享"]',
            '//div[@role="button" and normalize-space()="Share to"]',
        ],
    )
    print("instagram publisher done")
