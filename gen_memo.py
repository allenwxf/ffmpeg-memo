#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
import random
import yaml
# from yaml.scanner import ScannerError
import sample_route_data


class Memo:
    scriptConf = {}
    staticPath = "materials/"
    logoPath = staticPath + "logo.png"
    OUTPUTRES = "hd720"
    CAPTIONTYPE = 1
    PICTYPE = 2
    VIDEOTYPE = 3
    PADSCALE = "6400x3600"

    ffmpegCmd = "ffmpeg -y "
    ffmpegVoutConf = "-c:v libx264 -pix_fmt yuv420p -r 25 -profile:v baseline -level 3"
    ffmpegAoutConf = "-c:a aac -qscale:a 1 -ac 2 -ar 48000 -ab 192k"
    ffmpegMetaConf = "-metadata title=\"我的旅游日记\" -metadata artist=\"我的名字\" -metadata album=\"路线名称\""

    def __init__(self, script_conf_path):
        try:
            f = open(script_conf_path)
            self.scriptConf = yaml.load(f)
        except FileNotFoundError:
            print("script conf file not found：" + str(FileNotFoundError))
            exit(0)

    def generate_memo(self):
        # 获取用户上传路线材料
        route_data = sample_route_data.gen_sample_route()

        # 随机获取背景音乐
        bgmusic = self.get_random_bgmusic()
        print(bgmusic)

        # 产生黑色背景
        self.get_blank_bg()

        # 输入素材列表、总时长、所有POI(CUT)格式化过的素材列表
        total_duration, total_materials, input_materials = self.materials_join_conf(route_data)

        # 得到POI遍历结果
        """
        eg.
        [{
            'vplist':[
                {'trans_out': 2,'subtitle_vfx': None,'duration': 5,'file': 'materials/sample/POI_2/WechatIMG33.jpeg','subtitle_x': 0,'subtitle_font_size': 12,'trans_in': 4,'subtitle_y': 0,'subtitle': '','subtitle_color': None}, 
                {'trans_out': 3, 'subtitle_vfx': None, 'duration': 3, 'file': 'materials/sample/POI_2/WechatIMG145.jpeg', 'subtitle_x': 0, 'subtitle_font_size': 12, 'trans_in': 1, 'subtitle_y': 0, 'subtitle': '', 'subtitle_color': None}
            ],
            'captions': {'content': '文字内容文字内容1','duration': 3,'subtitle_x': 0,'subtitle_vfx': None,'subtitle_font_size': 12,'subtitle_y': 0,'subtitle_color': None}
        }, {
            'vplist': [
                {'trans_out': 2,'subtitle_vfx': None,'duration': 5,'file': 'materials/sample/POI_2/WechatIMG132.jpeg','subtitle_x': 0,'subtitle_font_size': 12,'trans_in': 3,'subtitle_y': 0,'subtitle': '','subtitle_color ': None}
            ],
            'captions ': {}
        }]
        """

        for input_material in input_materials:
            self.ffmpegCmd += " -i {} ".format(input_material)
        print(self.ffmpegCmd)

        self.ffmpegCmd += "filter_complex \""










    def get_random_bgmusic(self):
        conf_bgmusic = self.scriptConf["memoflow"]["bgmusic"]
        bgmusic = random.choice(conf_bgmusic)
        self.ffmpegCmd += " -i {}musics/{} " . format(self.staticPath, bgmusic)
        return bgmusic

    def get_blank_bg(self):
        self.ffmpegCmd += " -f lavfi -i \"color=black:s={}\" ".format(self.OUTPUTRES)

    def materials_join_conf(self, route_data):
        # 输入素材列表
        input_materials = []

        # 总时长
        total_duration = 0
        # 所有POI(CUT)格式化过的素材列表
        total_materials = []

        # 遍历每个POI(CUT)
        for node in route_data["route"]:
            """
            eg. 
            {
                "node": "POI_2",
                "materials": [
                    [
                        {"ts": 1544858301, "type": 1, "content": "文字内容文字内容1"},
                        {"ts": 1544858302, "type": 2, "file": "WechatIMG33.jpeg"},
                        {"ts": 1544858303, "type": 3, "file": "2019-03-03-15.07.47.mp4"}
                    ],
                ]
            }
            """
            print("node name: {}".format(node["node"]))
            # 遍历每个material
            for m in node["materials"]:
                # 对于图片和视频，获取张数，以确定字幕时长
                cur_caption_duration = 0
                # 生成图片、视频特效配置
                cur_materials = {}
                cur_vplist = []
                cur_caption_conf = {}
                # 遍历一个组合内的素材（同一时间上传）
                for m_item in m:
                    type_conf = self.scriptConf["memoflow"][node["node"]]["type" + str(m_item["type"])]
                    if m_item["type"] in [self.PICTYPE, self.VIDEOTYPE]:
                        # print(self.scriptConf["memoflow"][node["node"]])

                        # 获取配置信息
                        cur_duration = random.choice(type_conf["duration"])
                        cur_vp_conf = {"file": m_item["file"],
                                       "duration": cur_duration,
                                       "trans_in": random.choice(type_conf["trans_in"]),
                                       "trans_out": random.choice(type_conf["trans_out"]),
                                       "subtitle": type_conf["subtitle"],
                                       "subtitle_font_size": type_conf["subtitle_font_size"],
                                       "subtitle_x": type_conf["subtitle_x"],
                                       "subtitle_y": type_conf["subtitle_y"],
                                       "subtitle_color": type_conf["subtitle_color"],
                                       "subtitle_vfx": type_conf["subtitle_vfx"]
                                       }

                        cur_caption_duration += cur_duration
                        cur_vplist.append(cur_vp_conf)

                        total_duration += cur_duration

                        input_materials.append(m_item["file"])
                    if m_item["type"] == self.CAPTIONTYPE:
                        if type_conf["strategy"] == "random":
                            cur_caption_conf = random.choice(type_conf["lists"])
                            cur_caption_conf["content"] = m_item["content"]
                cur_materials["captions"] = cur_caption_conf
                cur_materials["vplist"] = cur_vplist
                total_materials.append(cur_materials)

        return total_duration, total_materials, input_materials


class UsageError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error:
            raise UsageError(str(getopt.error))
        # more code, unchanged
    except UsageError:
        print(str(UsageError))
        print(sys.stderr, "for help use --help")
        return 2
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
    # process arguments
    # for arg in args:
        # process(arg)  # process() is defined elsewhere

    script_conf_path = r"script_conf.yaml"
    memo = Memo(script_conf_path)
    memo.generate_memo()


if __name__ == "__main__":
    sys.exit(main())


