##########################################################################################################
#   Description: 纵向加密连接图数据读取器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import re
from dataclasses import dataclass
from typing import List, Optional, Literal

from ....reader import DataUnitDDN
from ..cryptoCommonDev import (
    CommonCryptoDev,
    CryptoDeviceType,
    CryptoDevPair,
    CryptoExistedEdgedIDF,
    CryptoNewEdgedIDF,
    CryptoNormalIDF,
    CryptoAccessSwitch,
    CryptoRoomConnectedIDF
)

from ..cryptoCommonDev import CryptoDeviceType


@dataclass
class CryptoParseUnit:
    '''纵向加密设备解析单元'''

    value: str
    tag: Optional[str] = None

    TAG_PATTERN = re.compile(r"^(?P<value>.*?)(?:<(?P<tag>.*?)>)?$")

    @classmethod
    def fromRaw(cls, rawValue: str):
        '''从原始字符串解析设备值与TAG'''

        if rawValue is None:
            raise ValueError("纵向加密设备配置为空，无法解析")

        rawValue = str(rawValue).strip()
        matched = cls.TAG_PATTERN.match(rawValue)

        if matched is None:
            raise ValueError(f"纵向加密设备配置解析失败: {rawValue}")

        value = matched.group("value").strip()
        tag = matched.group("tag")

        if tag is not None:
            tag = tag.strip().lower()

        if not value:
            raise ValueError(f"纵向加密设备配置缺少设备值: {rawValue}")

        return cls(value=value, tag=tag)

    def isRoom2(self) -> bool:
        '''是否位于第二机房'''

        return self.tag == CryptoLinkReader.TAG_ROOM2

    def isJump(self) -> bool:
        '''是否跳过绘制'''

        return self.tag == CryptoLinkReader.TAG_JUMP

    def isExistedEdgedIDF(self) -> bool:
        '''是否为利旧现有成端IDF'''

        return self.tag == CryptoLinkReader.TAG_EXISTED_EDGED_IDF

    def isNoPhoto(self) -> bool:
        '''是否未拍照'''

        return self.tag == CryptoLinkReader.TAG_NO_PHOTO


class CryptoLinkReader:
    '''纵向加密连接图数据读取器'''

    TAG_ROOM2 = "r2"
    TAG_JUMP = "j"
    TAG_EXISTED_EDGED_IDF = "e"
    TAG_NO_PHOTO = "np"

    VALID_TAG_SET = {
        None,
        TAG_ROOM2,
        TAG_JUMP,
        TAG_EXISTED_EDGED_IDF,
        TAG_NO_PHOTO
    }

    DATA_KEY_DDN_INSTALL_PNUM = "DDNInstallPnum"
    DATA_KEY_EDGED_IDF_ALTITUDE_U = "edgedIDFaltitudeU"

    DATA_KEY_RTCD_PNAME = "rtcdPname"
    DATA_KEY_RTCD_DEV_NUM_LIST = "rtcdDevNumList"
    DATA_KEY_RTCD_DEV_PORT_LIST = "rtcdDevPortList"

    DATA_KEY_NRTCD_PNAME = "nrtcdPname"
    DATA_KEY_NRTCD_DEV_NUM_LIST = "nrtcdDevNumList"
    DATA_KEY_NRTCD_DEV_PORT_LIST = "nrtcdDevPortList"

    EXISTED_EDGED_IDF_ERROR_TEXT = "已标记使用现有IDF设备，不能新增成端IDF"

    def __init__(self, data: DataUnitDDN) -> None:
        """初始化纵向加密连接图数据读取器

        :param data: ddn单站数据
        """

        self.data = data
        self.deviceList: List[CommonCryptoDev] = []

        self.rtDevUnitList: List[CryptoParseUnit] = []
        self.nrtDevUnitList: List[CryptoParseUnit] = []
        self.rtPortList: List[str] = []
        self.nrtPortList: List[str] = []

        self._initRawData()
        self._initDeviceList()
        
        
        
        self._checkDeviceList()

    def _initRawData(self):
        '''初始化原始解析数据'''

        self.rtDevUnitList = [
            CryptoParseUnit.fromRaw(rawValue)
            for rawValue in self.data.get(self.DATA_KEY_RTCD_DEV_NUM_LIST)
        ]

        self.nrtDevUnitList = [
            CryptoParseUnit.fromRaw(rawValue)
            for rawValue in self.data.get(self.DATA_KEY_NRTCD_DEV_NUM_LIST)
        ]

        self.rtPortList = self.data.get(self.DATA_KEY_RTCD_DEV_PORT_LIST)
        self.nrtPortList = self.data.get(self.DATA_KEY_NRTCD_DEV_PORT_LIST)

        self._checkRawData()

    def _checkRawData(self):
        '''检查原始数据合法性'''

        if len(self.rtDevUnitList) == 0:
            raise ValueError("实时纵向加密设备列表为空")

        if len(self.nrtDevUnitList) == 0:
            raise ValueError("非实时纵向加密设备列表为空")

        if len(self.rtDevUnitList) != len(self.nrtDevUnitList):
            raise ValueError(
                "纵向加密实时和非实时设备数量不一致，"
                f"实时={len(self.rtDevUnitList)}，非实时={len(self.nrtDevUnitList)}"
            )

        if len(self.rtDevUnitList) != len(self.rtPortList):
            raise ValueError(
                "实时纵向加密设备数量和端口数量不一致，"
                f"设备={len(self.rtDevUnitList)}，端口={len(self.rtPortList)}"
            )

        if len(self.nrtDevUnitList) != len(self.nrtPortList):
            raise ValueError(
                "非实时纵向加密设备数量和端口数量不一致，"
                f"设备={len(self.nrtDevUnitList)}，端口={len(self.nrtPortList)}"
            )

        for unit in self.rtDevUnitList + self.nrtDevUnitList:
            if unit.tag not in self.VALID_TAG_SET:
                raise ValueError(f"纵向加密设备TAG非法: {unit.value}<{unit.tag}>")

    def _initDeviceList(self):
        '''初始化设备列表'''

        self.deviceList = []

        self._appendNewEdgedIDF()
        self._appendIDFList()
        self._appendCryptoDevPair()

    def _appendNewEdgedIDF(self):
        '''追加本期新增成端IDF'''

        if self.data.get(self.DATA_KEY_EDGED_IDF_ALTITUDE_U) is None:
            return

        self.deviceList.append(
            CryptoNewEdgedIDF(
                deviceNum=self.data.get(self.DATA_KEY_DDN_INSTALL_PNUM)
            )
        )

    def _appendIDFList(self):
        '''追加IDF设备列表'''

        # 最后一项是纵向加密设备本体，不作为IDF处理
        rtIDFUnitList = self.rtDevUnitList[:-1]
        nrtIDFUnitList = self.nrtDevUnitList[:-1]

        rtIDFPortList = self.rtPortList[:-1]
        nrtIDFPortList = self.nrtPortList[:-1]

        for index, (rtUnit, nrtUnit) in enumerate(zip(rtIDFUnitList, nrtIDFUnitList)):
            if rtUnit.isJump() and nrtUnit.isJump():
                continue

            self._checkIDFPair(
                index=index,
                rtUnit=rtUnit,
                nrtUnit=nrtUnit
            )

            if rtUnit.isExistedEdgedIDF():
                self.deviceList.append(
                    CryptoExistedEdgedIDF(
                        deviceNum=rtUnit.value,
                        portR=rtIDFPortList[index],
                        portNR=nrtIDFPortList[index],
                        isRoom2=rtUnit.isRoom2() or nrtUnit.isRoom2(),
                        isJump=rtUnit.isJump() and nrtUnit.isJump(),
                        isNoPhoto=rtUnit.isNoPhoto() or nrtUnit.isNoPhoto(),
                        isCutBusiness=True
                    )
                )
                continue

            self.deviceList.append(
                CryptoNormalIDF(
                    deviceNum=rtUnit.value,
                    portR=rtIDFPortList[index],
                    portNR=nrtIDFPortList[index],
                    isRoom2=rtUnit.isRoom2() or nrtUnit.isRoom2(),
                    isJump=rtUnit.isJump() and nrtUnit.isJump(),
                    isNoPhoto=rtUnit.isNoPhoto() or nrtUnit.isNoPhoto(),
                    isCutBusiness=self._shouldCutBusiness()
                )
            )

    def _appendCryptoDevPair(self):
        '''添加纵向加密设备对'''

        rtCDUnit = self.rtDevUnitList[-1]
        nrtCDUnit = self.nrtDevUnitList[-1]

        rtPort = self.rtPortList[-1]
        nrtPort = self.nrtPortList[-1]

        self.deviceList.append(
            CryptoDevPair(
                rtPnum=rtCDUnit.value,
                rtPname=self.data.get(self.DATA_KEY_RTCD_PNAME),
                nrtPnum=nrtCDUnit.value,
                nrtPname=self.data.get(self.DATA_KEY_NRTCD_PNAME),
                rtPort=rtPort,
                nrtPort=nrtPort,
                rtIsRoom2=rtCDUnit.isRoom2(),
                nrtIsRoom2=nrtCDUnit.isRoom2(),
                rtIsJump=rtCDUnit.isJump(),
                nrtIsJump=nrtCDUnit.isJump(),
                rtIsNoPhoto=rtCDUnit.isNoPhoto(),
                nrtIsNoPhoto=nrtCDUnit.isNoPhoto()
            )
        )

    def _checkIDFPair(
            self,
            index: int,
            rtUnit: CryptoParseUnit,
            nrtUnit: CryptoParseUnit
    ):
        '''检查实时/非实时IDF配置是否匹配'''

        if rtUnit.value != nrtUnit.value:
            raise ValueError(
                "纵向加密实时/非实时IDF设备号不一致，"
                f"第{index + 1}个IDF，实时={rtUnit.value}，非实时={nrtUnit.value}"
            )

        if rtUnit.isExistedEdgedIDF() != nrtUnit.isExistedEdgedIDF():
            raise ValueError(
                "纵向加密实时/非实时现有成端IDF标记不一致，"
                f"第{index + 1}个IDF，实时TAG={rtUnit.tag}，非实时TAG={nrtUnit.tag}"
            )

    def _shouldCutBusiness(self) -> bool:
        '''是否绘制断开业务标记'''

        for device in self.deviceList:
            if device.deviceType == CryptoDeviceType.NORMAL_IDF:
                return False

        return True

    def _parseRoomConnectedIDF(
            self,
            deviceList: List[CommonCryptoDev]
    ) -> List[CommonCryptoDev]:
        '''解析机房互联IDF'''

        resultDeviceList = list(deviceList)

        room2BoundaryRightIndex = self._getRoom2BoundaryRightIndex(resultDeviceList)

        if room2BoundaryRightIndex is None:
            return resultDeviceList

        if room2BoundaryRightIndex == 0:
            return resultDeviceList

        room2BoundaryLeftIndex = room2BoundaryRightIndex - 1

        leftDevice = resultDeviceList[room2BoundaryLeftIndex]
        rightDevice = resultDeviceList[room2BoundaryRightIndex]

        if not self._isNormalOldIDF(leftDevice):
            return resultDeviceList

        if not self._isNormalOldIDF(rightDevice):
            return resultDeviceList

        resultDeviceList[room2BoundaryLeftIndex] = self._toRoomConnectedIDF(
            device=leftDevice,
            direction=CryptoRoomConnectedIDF.DIRECTION_LEFT
        )

        resultDeviceList[room2BoundaryRightIndex] = self._toRoomConnectedIDF(
            device=rightDevice,
            direction=CryptoRoomConnectedIDF.DIRECTION_RIGHT
        )

        return resultDeviceList

    def _getRoom2BoundaryRightIndex(
            self,
            deviceList: List[CommonCryptoDev]
    ) -> Optional[int]:
        '''获取第二机房边界右侧设备索引'''

        for index, device in enumerate(deviceList):
            if device.isRoom2:
                return index

        return None
    
    def _isNormalOldIDF(
            self,
            device: CommonCryptoDev
    ) -> bool:
        '''判断设备是否为普通旧IDF'''

        if device.deviceType != CryptoDeviceType.NORMAL_IDF:
            return False

        if device.isNew:
            return False

        return True

    def _toRoomConnectedIDF(
            self,
            device: CommonCryptoDev,
            direction: Literal["left", "right"]
    ) -> CryptoRoomConnectedIDF:
        '''将普通IDF转换为机房互联IDF'''

        if device.deviceNum is None:
            raise ValueError("机房互联IDF设备号不能为空")

        return CryptoRoomConnectedIDF(
            deviceNum=device.deviceNum,
            portR=getattr(device, "portR"),
            portNR=getattr(device, "portNR"),
            direction=direction,
            isRoom2=device.isRoom2,
            isJump=device.isJump,
            isNoPhoto=device.isNoPhoto,
            isCutBusiness=getattr(device, "isCutBusiness", False)
        )

    def _checkDeviceList(self):
        '''校验设备列表合法性'''

        self._checkEdgedIDF()
        self._checkCryptoDevPair()

    def _checkEdgedIDF(self):
        '''检查成端IDF合法性'''

        edgedIDFIndexList: List[int] = [
            index
            for index, device in enumerate(self.deviceList)
            if device.deviceType in (
                "newEdgedIDF",
                "existedEdgedIDF"
            )
        ]

        if len(edgedIDFIndexList) == 0:
            return

        if len(edgedIDFIndexList) > 1:
            if self._hasNewEdgedIDF() and self._hasExistedEdgedIDF():
                raise ValueError(self.EXISTED_EDGED_IDF_ERROR_TEXT)

            raise ValueError("成端IDF设备最多只能配置一个")

        if edgedIDFIndexList[0] != 0:
            raise ValueError("成端IDF设备必须是第一个设备")

    def _checkCryptoDevPair(self):
        '''检查纵向加密设备对合法性'''

        if len(self.deviceList) == 0:
            raise ValueError("纵向加密设备列表为空")

        if not isinstance(self.deviceList[-1], CryptoDevPair):
            raise ValueError("纵向加密设备列表最后一个设备必须是加密设备对")

    def _hasNewEdgedIDF(self) -> bool:
        '''是否存在本期新增成端IDF'''

        return any(
            isinstance(device, CryptoNewEdgedIDF)
            for device in self.deviceList
        )

    def _hasExistedEdgedIDF(self) -> bool:
        '''是否存在利旧现有成端IDF'''

        return any(
            isinstance(device, CryptoExistedEdgedIDF)
            for device in self.deviceList
        )

    def _assertCanMergeAccessSwitch(
            self,
            currentDevice: CommonCryptoDev,
            nextDevice: CommonCryptoDev
    ):
        '''断言两个设备可以合并为接入交换机'''

        if currentDevice.deviceType != CryptoDeviceType.NORMAL_IDF:
            raise ValueError(
                "连续两个设备号相同，但第一个设备不是旧普通IDF，"
                f"设备号={currentDevice.deviceNum}，设备类型={currentDevice.deviceType}"
            )

        if nextDevice.deviceType != CryptoDeviceType.NORMAL_IDF:
            raise ValueError(
                "连续两个设备号相同，但第二个设备不是旧普通IDF，"
                f"设备号={nextDevice.deviceNum}，设备类型={nextDevice.deviceType}"
            )

        if currentDevice.isNew:
            raise ValueError(
                "连续两个设备号相同，但第一个设备不是旧设备，"
                f"设备号={currentDevice.deviceNum}"
            )

        if nextDevice.isNew:
            raise ValueError(
                "连续两个设备号相同，但第二个设备不是旧设备，"
                f"设备号={nextDevice.deviceNum}"
            )

        for attrName in ["portR", "portNR"]:
            if not hasattr(currentDevice, attrName):
                raise ValueError(
                    f"连续两个设备号相同，但第一个设备缺少{attrName}属性，"
                    f"无法合并为接入交换机"
                )

            if not hasattr(nextDevice, attrName):
                raise ValueError(
                    f"连续两个设备号相同，但第二个设备缺少{attrName}属性，"
                    f"无法合并为接入交换机"
                )

    def _isSameDeviceNum(
            self,
            currentDevice: CommonCryptoDev,
            nextDevice: CommonCryptoDev
    ) -> bool:
        '''判断两个连续设备是否设备号相同'''

        if currentDevice.deviceNum is None:
            return False

        if nextDevice.deviceNum is None:
            return False

        return currentDevice.deviceNum == nextDevice.deviceNum

    def _mergeAccessSwitch(
            self,
            deviceList: List[CommonCryptoDev]
    ) -> List[CommonCryptoDev]:
        '''合并接入交换机'''

        resultDeviceList: List[CommonCryptoDev] = []
        index = 0

        while index < len(deviceList):
            currentDevice = deviceList[index]

            if index + 1 >= len(deviceList):
                resultDeviceList.append(currentDevice)
                break

            nextDevice = deviceList[index + 1]

            if self._isSameDeviceNum(currentDevice, nextDevice):
                self._assertCanMergeAccessSwitch(
                    currentDevice=currentDevice,
                    nextDevice=nextDevice
                )

                assert isinstance(currentDevice, CryptoNormalIDF)
                assert isinstance(nextDevice, CryptoNormalIDF)

                resultDeviceList.append(
                    CryptoAccessSwitch(
                        deviceNum=currentDevice.deviceNum, # type: ignore
                        frontPort1=currentDevice.portR,
                        frontPort2=currentDevice.portNR,
                        afterPort1=nextDevice.portR,
                        afterPort2=nextDevice.portNR,
                        isRoom2=currentDevice.isRoom2 or nextDevice.isRoom2,
                        isNoPhoto=currentDevice.isNoPhoto or nextDevice.isNoPhoto
                    )
                )

                index += 2
                continue

            resultDeviceList.append(currentDevice)
            index += 1

        return resultDeviceList

    def toDeviceList(self) -> List[CommonCryptoDev]:
        '''输出设备列表'''

        deviceList = [
            device
            for device in self.deviceList
            if not device.isJump
        ]

        deviceList = self._mergeAccessSwitch(deviceList)
        deviceList = self._parseRoomConnectedIDF(deviceList)

        return deviceList