##########################################################################################################
#   Description: 装饰器
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from .log import gLog

import functools
from typing import Optional
from PyQt6.QtWidgets import QMessageBox

def tryDo(title: str, info: Optional[str] = None):
    """尝试执行
    此函数使用时可能会产生签名不匹配的问题，请检查信号与槽连接时，是否额外传递了参数

    :param title: 报错时的标题
    :param info:  成功执行时提示的信息
    """    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self):
            try:
                result = func(self)
            except TypeError as e:
                gLog.logInfo(f"Error: 函数签名不匹配, 可能是信号槽额外传递了参数, 请检查信号连接")
                raise e
            except Exception as e:
                gLog.logInfo(f"Error: {str(e)}")
                QMessageBox.critical(None,
                                    title,
                                    str(e))
                return None
            else:
                if info is not None:
                    QMessageBox.information(
                        None,
                        title,
                        info
                    )
                return result
        return wrapper
    return decorator

def askDo(title: str, prompt: str):
    """交互式询问执行

    :param title: 标题
    :param prompt: 引导词
    """    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self):
            reply = QMessageBox.question(
                    None,
                    title,
                    prompt,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                return func(self)
            
        return wrapper
    return decorator