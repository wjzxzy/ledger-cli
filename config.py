"""
config.py —— 全局配置
============================================
所有"写死在代码里的常量"都集中到这里，其他文件从这里 import。
想改路径、想加类别，只动这一个文件。

原来这两行在 main.py 顶部，现在搬到这里：
    DATA_FILE = "data.json"
    CATEGORIES = ["餐饮", "交通", "购物", "娱乐", "其他"]
"""

from pathlib import Path

# 本文件所在目录 = 项目根目录
# __file__ 是当前文件的路径，.parent 取它所在的文件夹
BASE_DIR = Path(__file__).resolve().parent

# 数据文件用「绝对路径」，这样不管你在哪个目录下运行 python main.py，
# 找到的都是同一个 data.json（原版用相对路径，换个目录运行就读不到旧数据了）
DATA_FILE = BASE_DIR / "data.json"

# 固定类别。想加类别只改这一处
CATEGORIES = ["餐饮", "交通", "购物", "娱乐", "其他"]
