# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: songjixian
@file: utils.py
@time: 2023/5/26 下午4:00
@Description: 
"""
import traceback
from xml.dom.minidom import parseString, parse
import html


def parse_xml(xml_str, u_df):
    """
    parse xml to find the message referenced by current message
    :param xml_str:
    :return: dict
    """
    xml_dom = parseString(xml_str)
    try:
        data = xml_dom.documentElement
        current_content = data.getElementsByTagName("title")[0].childNodes[0].nodeValue
        ref_data = data.getElementsByTagName("refermsg")[0]
        reference_content = ref_data.getElementsByTagName("content")[0].childNodes[0].nodeValue
        reference_id = int(ref_data.getElementsByTagName("svrid")[0].childNodes[0].nodeValue)
        is_send = u_df[u_df["msgSvrId"] == reference_id].iloc[0]["isSend"]
        # if reference is a reference
        r_reference = None
        if "xml" in reference_content or "<msg" in reference_content:
            restore_content = html.unescape(reference_content)
            r_reference = parse_r_reference(restore_content)
            if r_reference is None:
                return None
        res = {
            "content": current_content,
            "reference": {
                "reference_id": str(reference_id),
                "is_send": int(is_send),
                "reference_content": reference_content if r_reference is None else r_reference
            }
        }
        return res
    except Exception as e:
        print("Parsing xml error, just return None, {}".format(repr(e)))
        return None


def parse_r_reference(xml_str):
    """
        parse xml to find the message referenced by current message
        :param xml_str:
        :return: dict
        """
    xml_dom = parseString(xml_str)
    try:
        data = xml_dom.documentElement
        current_content = data.getElementsByTagName("title")[0].childNodes[0].nodeValue
        return current_content
    except Exception as e:
        traceback.print_exc()
        print("Parsing xml error, just return None, {}".format(repr(e)))
        return None


if __name__ == '__main__':
    with open("./message_data/test.xml", "r", encoding="utf-8") as f:
        xml_s = f.read()
    # xml_s = '<msg><appmsg appid=""  sdkver="0"><title>有一点用是有的电商平台会提高有直播间商家的曝光率</title><des></des><type>57</type><appattach><cdnthumbaeskey></cdnthumbaeskey><aeskey></aeskey></appattach></appmsg><fromusername>wxid_oi6im7dq11n522</fromusername><appinfo><version>1</version><appname></appname><isforceupdate>1</isforceupdate></appinfo></msg>'
    res = parse_xml(xml_s)
    print(res)
