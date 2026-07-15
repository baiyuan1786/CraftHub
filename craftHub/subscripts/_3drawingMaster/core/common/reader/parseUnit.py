##########################################################################################################
#   Description: 表格字符串解析单元
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Optional


class ParseUnit:
    '''表格字符串解析单元'''

    TAG_START = "<"
    TAG_END = ">"

    def __init__(self, rawStr: str) -> None:
        """初始化表格字符串解析单元

        :param rawStr: 原始字符串，例如 34P02<r2>
        """

        if not isinstance(rawStr, str):
            raise TypeError(f"rawStr必须是str类型，当前类型为{type(rawStr)}")

        self.rawStr = rawStr.strip()
        self.value: str
        self.tag: Optional[str]

        self.value, self.tag = self._parseRawStr(self.rawStr)

    def _parseRawStr(self, rawStr: str) -> tuple[str, Optional[str]]:
        '''解析原始字符串'''

        if not rawStr.endswith(self.TAG_END):
            return rawStr, None

        tagStartIndex = rawStr.rfind(self.TAG_START)

        if tagStartIndex < 0:
            raise ValueError(f"解析失败，存在结束符但没有开始符: {rawStr}")

        value = rawStr[:tagStartIndex].strip()
        tag = rawStr[tagStartIndex + 1:-1].strip()

        if tag == "":
            raise ValueError(f"解析失败，tag不能为空: {rawStr}")

        return value, tag.lower()

    def isMatched(self, other: "ParseUnit | Optional[str]") -> bool:
        '''判断tag是否匹配'''

        if isinstance(other, ParseUnit):
            return self.tag == other.tag

        if other is None:
            return self.tag is None

        if not isinstance(other, str):
            raise TypeError(f"other必须是ParseUnit、str或None，当前类型为{type(other)}")

        other = other.strip()

        if other == "":
            return self.tag is None

        if other.endswith(self.TAG_END) and self.TAG_START in other:
            return self.tag == ParseUnit(other).tag

        return self.tag == other.lower()

    def __repr__(self) -> str:
        '''调试字符串'''

        return f"ParseUnit(value={self.value!r}, tag={self.tag!r})"
    
    def __eq__(self, other: object) -> bool:
        '''判断与另一个相同类一致'''
        if not isinstance(other, ParseUnit):
            return NotImplemented
        
        return self.tag == other.tag and self.value == other.value
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)