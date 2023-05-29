# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: songjixian
@file: clean_message.py
@time: 2023/5/25 下午4:16
@Description: 
"""
import json
import os.path
import pandas as pd
import numpy as np
from utils import parse_xml
import re


def get_uid_name(contact_file):
    df = pd.read_csv(contact_file)
    print("Total %d data" % len(df))
    print("\t".join(df.columns))
    # fill nan with special token in conRemark column
    df["conRemark"] = df["conRemark"].fillna("None")
    # filter conRemark
    filter_df = df[df["conRemark"] != "None"]
    return dict(zip(filter_df["username"], filter_df["conRemark"]))


def collect_his(uid, u_name, u_df):
    # sort by timeline
    u_df.sort_values(by="createTime", inplace=True, ascending=False)
    # filter emoji

    def filter_emoji(x):  # filter unknown emoji and emoji pictures
        return re.sub(r"^[\s\S]*:0:0:[\s\S]*::0\n", "你猜是什么表情包？\n", x.replace("??", ""))
    u_df["content"] = u_df["content"].apply(filter_emoji)
    # filter emoji picture
    message_history = []
    ref_dict = dict()
    voice_call_p = f"{uid}:\d+:\d+"
    emoji_p = "\[(.*?)\]"
    for index, item in u_df.iterrows():
        is_send = item["isSend"]
        content = item["content"]
        message_id = str(item["msgSvrId"])
        item_res = {
            "is_send": is_send,
            "message_id": message_id,
            "content": None,
            "reference": None
        }
        if re.match(voice_call_p, content) is not None:  # ignore voice calls
            continue
        if "xml" in content or "&lt;" in content or "<msg" in content:
            res = parse_xml(content, u_df)
            # ignore illegal xml
            if res is None or "撤回了一条消息" in res["content"]:  # ignore none or special words
                continue
            item_res["content"] = res["content"]
            item_res["reference"] = res['reference']
        else:
            if "撤回了一条消息" in content:  # ignore none or special words
                continue
            item_res["content"] = content
        ref_dict[message_id] = len(message_history)
        message_history.append(item_res)
    print("Total %d history for %s %s" % (len(message_history), uid, u_name))
    for mes in message_history:
        if mes["reference"] is not None:
            reference_id = mes["reference"]["reference_id"]
            if reference_id not in ref_dict:  # The reference is illegal or not exists
                mes["reference"] = None
                continue
            refer_index = ref_dict[reference_id]
            # the expression is different for emoji in ori content and refer content
            ori_item_content = re.sub(emoji_p, "", message_history[refer_index]["content"])
            refer_content = re.sub(emoji_p, "", mes["reference"]["reference_content"])
            if ori_item_content != refer_content:
                print("%s #### %s" % (message_history[refer_index]["content"], mes["reference"]["reference_content"]))
                print("%s #### %s" % (mes["message_id"], reference_id))
                raise ValueError("The reference contents are inconsistent")
            mes["reference"]["reference_index"] = ref_dict[reference_id]
    return message_history


def split_history_to_data(all_history, out_file, max_turns=5, max_length=256):
    samples = []
    for key in all_history:
        his_items = all_history[key]["history"]
        for h_id, message_item in enumerate(his_items):
            prompt = ""
            response = ""
            history = []
            # find the sentence sent by myself
            if message_item['is_send'] == 1:
                is_response = True
                context_index = h_id
                cur_turn = 0
                temp_response = ""
                temp_prompt = ""
                while context_index < len(his_items):
                    is_send = his_items[context_index]["is_send"]
                    reference = his_items[context_index]["reference"]
                    # sent by myself
                    if is_send == 1:
                        if not is_response:
                            is_response = True
                            # finish one turn dialogue, record it
                            if cur_turn == 0:  # take the first turn as prompt and response
                                prompt = temp_prompt
                                response = temp_response
                            else:  # append the data to history from the second turn
                                history.append((temp_prompt, temp_response))
                            cur_turn += 1
                            temp_prompt = ""
                            temp_response = ""
                            if cur_turn > max_turns:  # exit the loop when reaching the maximum number of turns
                                break
                        if len(temp_response) > 0:
                            temp_response = "{}\n{}".format(his_items[context_index]["content"], temp_response)
                        else:
                            temp_response = his_items[context_index]["content"]
                    elif is_send == 0:  # sent by others
                        if is_response:
                            is_response = False
                        if len(temp_prompt) > 0:
                            temp_prompt = "{}\n{}".format(his_items[context_index]["content"], temp_prompt)
                        else:
                            temp_prompt = his_items[context_index]["content"]
                    if reference is None:
                        # the default above is the next one
                        context_index += 1
                    else:
                        # got strict above from reference
                        context_index = reference["reference_index"]
                if context_index >= len(his_items) and len(temp_prompt) > 0 and len(temp_response) > 0:
                    if cur_turn == 0:
                        prompt = temp_prompt
                        response = temp_response
                    else:
                        history.append((temp_prompt, temp_response))
                if len(prompt) > 0 and len(response) > 0:
                    samples.append(
                        {
                            "prompt": prompt,
                            "response": response,
                            "history": history[::-1]
                        }
                    )

    print("Total %d samples" % len(samples))
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)


def clean_sensitive_info():
    pass


def clean_message(message_file, contact_dict):
    df = pd.read_csv(message_file)
    print("Total %d message " % len(df))
    print("\t".join(df.columns))
    # filter message not in contact_dict
    uid_set = contact_dict.keys()
    df = df[df["talker"].isin(uid_set)]
    print("After filtering only %d message remained" % len(df))
    all_history = {}
    for uid in contact_dict:
        u_df = df[df["talker"] == uid]
        if len(u_df) == 0:
            continue
        message_his = collect_his(uid, contact_dict[uid], u_df)
        all_history[uid] = {}
        all_history[uid]["history"] = message_his
        all_history[uid]["name"] = contact_dict[uid]
    out_file = os.path.join(os.path.dirname(message_file), "chat_data.json")
    split_history_to_data(all_history, out_file)


if __name__ == '__main__':
    contact_dict = get_uid_name("./message_data/friends.csv")
    clean_message("./message_data/message.csv", contact_dict)
