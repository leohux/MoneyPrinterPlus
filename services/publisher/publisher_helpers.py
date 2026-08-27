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

import sys
import time

import pyperclip
import streamlit as st
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from tools.file_utils import read_file_start_with_secondline, read_head


def open_new_tab(driver, url):
    driver.switch_to.new_window("tab")
    driver.get(url)
    time.sleep(3)


def get_publish_meta(platform):
    use_common = st.session_state.get("video_publish_use_common_config")
    if use_common:
        prefix = st.session_state.get("video_publish_title_prefix") or ""
        tags = st.session_state.get("video_publish_tags") or ""
    else:
        prefix = st.session_state.get(f"video_publish_{platform}_title_prefix") or ""
        tags = st.session_state.get(f"video_publish_{platform}_tags") or ""
    return (prefix or "").strip(), (tags or "").strip()


def build_title_and_caption(platform, text_file, title_limit=None):
    prefix, tags = get_publish_meta(platform)
    head = (read_head(text_file) or "").strip()
    body = (read_file_start_with_secondline(text_file) or "").strip()
    title = (prefix + head).strip() or head
    if title_limit and len(title) > title_limit:
        title = (head or title)[:title_limit]
    tag_list = tags.split() if tags else []
    hashtags = " ".join(t if t.startswith("#") else f"#{t.lstrip('#')}" for t in tag_list)
    caption = "\n\n".join(part for part in [title, body, hashtags] if part)
    return title, body, hashtags, caption


def find_first(driver, xpaths, timeout=15):
    last_err = None
    per_try = max(2, int(timeout / max(len(xpaths), 1)))
    for xp in xpaths:
        try:
            return WebDriverWait(driver, per_try).until(
                EC.presence_of_element_located((By.XPATH, xp))
            )
        except Exception as e:
            last_err = e
    raise last_err or TimeoutException(f"none of selectors matched: {xpaths}")


def click_first(driver, xpaths, timeout=8):
    el = find_first(driver, xpaths, timeout)
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    except Exception:
        pass
    try:
        el.click()
    except Exception:
        driver.execute_script("arguments[0].click();", el)
    return el


def try_click_texts(driver, texts, timeout=5):
    xpaths = []
    for t in texts:
        xpaths.extend(
            [
                f'//button[contains(normalize-space(.), "{t}")]',
                f'//*[@role="button" and contains(normalize-space(.), "{t}")]',
                f'//div[@role="button" and contains(normalize-space(.), "{t}")]',
                f'//span[contains(normalize-space(.), "{t}")]/ancestor::button[1]',
                f'//span[contains(normalize-space(.), "{t}")]/ancestor::*[@role="button"][1]',
            ]
        )
    try:
        click_first(driver, xpaths, timeout)
        return True
    except Exception:
        return False


def upload_via_file_input(driver, video_file, timeout=30):
    wait = WebDriverWait(driver, timeout)
    inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//input[@type="file"]')))
    file_input = None
    for inp in inputs:
        accept = (inp.get_attribute("accept") or "").lower()
        if (not accept) or ("video" in accept) or ("mp4" in accept) or ("*" in accept):
            file_input = inp
            break
    if file_input is None:
        file_input = inputs[0]
    driver.execute_script(
        "arguments[0].style.display='block'; arguments[0].style.opacity=1;"
        "arguments[0].style.visibility='visible'; arguments[0].removeAttribute('hidden');"
        "arguments[0].removeAttribute('disabled');",
        file_input,
    )
    file_input.send_keys(video_file)
    print("uploaded file:", video_file)
    time.sleep(8)


def paste_into(driver, element, text):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    element.click()
    time.sleep(0.4)
    cmd = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
    try:
        element.send_keys(Keys.CONTROL if sys.platform != "darwin" else Keys.COMMAND, "a")
        element.send_keys(Keys.DELETE)
    except Exception:
        pass
    pyperclip.copy(text)
    webdriver.ActionChains(driver).key_down(cmd).send_keys("v").key_up(cmd).perform()
    time.sleep(1)


def maybe_publish(driver, extra_xpaths=None):
    if not st.session_state.get("video_publish_auto_publish"):
        print("auto publish disabled, skip click")
        return False
    extra_xpaths = extra_xpaths or []
    if extra_xpaths:
        try:
            click_first(driver, extra_xpaths, 10)
            print("clicked platform publish button")
            return True
        except Exception:
            pass
    if try_click_texts(
        driver,
        ["Post", "Publish", "Share", "发布", "發佈", "分享", "立即发布", "Post now", "Share now"],
        timeout=8,
    ):
        print("clicked publish by text")
        return True
    print("publish button not found")
    return False
