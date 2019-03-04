Welcome!

gen_memo.py 为执行脚本
sample_route_data.py 生成测试数据（路线素材列表）
script_conf.yaml 脚本配置文件
materials 包含各种素材文件

执行python gen_memo.py，会生成一个ffmpeg filter_complex graph配置文件，
命名格式：filter_complex.[uid].[路线id].[时间戳]

python调用系统ffmpeg命令的方式生成视频，
视频命名格式：mymemo_[用户名]_[路线名]_[时间戳].mp4