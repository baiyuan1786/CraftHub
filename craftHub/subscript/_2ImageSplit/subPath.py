##########################################################################################################
#   Description: 子脚本路径管理
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from path import PATH_SUBSCRIPT

PATH_SUB_ROOT = PATH_SUBSCRIPT / "_2ImageSplit" # 子脚本根路径

PATH_DOC = PATH_SUB_ROOT / "doc"
PATH_DATA = PATH_SUB_ROOT / "doc" / "info" / "data.yaml"                # data路径
PATH_SET = PATH_SUB_ROOT / "doc" / "info" / "set.yaml"                  # set路径
PATH_INFO = PATH_SUB_ROOT / "doc" / "info" / "info.yaml"                # info路径
PATH_DESC = PATH_SUB_ROOT / "doc" / "info" / "description.txt"          # 描述路径
PATH_SETTING_CONFIG = PATH_SUB_ROOT / "doc" / "info" / "setting.yaml"   # 设置路径
PATH_PATTERN = PATH_SUB_ROOT / "doc" / "info" / "pattern.txt"           # pattern路径
