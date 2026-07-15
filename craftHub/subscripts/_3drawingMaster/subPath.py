##########################################################################################################
#   Description: 绘图大师子脚本路径管理
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from path import PATH_SUBSCRIPT

PATH_SUB_ROOT = PATH_SUBSCRIPT / "_3drawingMaster" # 子脚本根路径

PATH_DOC = PATH_SUB_ROOT / "doc"
PATH_DATA = PATH_DOC / "info" / "data.yaml"                # data路径
PATH_INFO = PATH_DOC / "info" / "info.yaml"                # info路径
PATH_DESC = PATH_DOC / "info" / "description.txt"          # 描述路径
PATH_SET = PATH_DOC / "info" / "data.yaml"                 # 就使用data路径
PATH_TEMPLATE_DIR = PATH_DOC / "template"                  # 模板路径