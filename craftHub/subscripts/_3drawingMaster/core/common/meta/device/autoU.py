##########################################################################################################
#   Description: 自动U数计算器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from typing import List, Optional, Literal
from .base import Device
from .common import NewPDU, ExistedDevice, EdgedIDF
from .idn import IDN设备
from .ddn import DDN设备

class AutoUcalculator:
    '''自动U数计算器'''

    TOTAL_HEIGHT = 47
    MIN_BORDER_SPACE = 1
    MIN_BORDER_SPACE_REPLACE = 0 # 替换设备允许间隔

    IDN_HEIGHT = 4
    DDN_HEIGHT = 4
    PDU_HEIGHT = 3
    IDF_HEIGHT = 1

    def __init__(self,
                 existedDeviceList: List[ExistedDevice]) -> None:
        """U数计算器初始化

        :param existedDeviceList: 已经存在的设备列表
        """

        self.existedDeviceList = existedDeviceList

        self.deviceAltitudeUList = [
            device.altitudeU
            for device in existedDeviceList
        ]

        self.deviceHeightUList = [
            device.heightU
            for device in existedDeviceList
        ]

        self.idnPosition = None
        self.ddnPosition = None
        self.idfPosition = None
        self.pduPositionList = []

        self.deviceList: List[Device] = self._copyExistedDeviceList()  # type: ignore

        self._checkDevicePosition()

        self.occupiedPositions = self._createOccupiedPositionSet(
            self.deviceAltitudeUList,
            self.deviceHeightUList
        )

    def installPDU(self,
                   altitudeU: int | Literal["auto"] | None,
                   isNormal: bool = False) -> Optional[Device]:
        """安装PDU设备

        :param altitudeU: PDU设备海拔，支持None、auto、整数
        :param isNormal: 是否将新增设备设置为normal类型
        :return: 安装后的设备对象
        """

        if altitudeU is None:
            return None

        newDevice = NewPDU(
            name="新增PDU(前面安装)",
            altitudeU=0
        )

        replacedDevice = self._tryReplaceDevice(
            newDevice=newDevice,
            wishType="TP"
        )

        if replacedDevice is not None:
            self.pduPositionList.append(replacedDevice.altitudeU)
            self.deviceList.append(replacedDevice)
            return replacedDevice

        pduPosition = self._installDeviceToPosition(
            altitudeU=altitudeU,
            height=self.PDU_HEIGHT,
            deviceName="PDU",
            pdu=True
        )

        if pduPosition is None:
            return None

        pduDevice = NewPDU(
            name="新增PDU(前面安装)",
            altitudeU=pduPosition
        )

        if isNormal:
            pduDevice.setDevType("normal")

        self.pduPositionList.append(pduPosition)
        self.deviceList.append(pduDevice)

        return pduDevice

    def installIDN(self,
                   altitudeU: int | Literal["auto"] | None,
                   isNormal: bool = False) -> Optional[Device]:
        """安装IDN设备

        :param altitudeU: IDN设备海拔，支持None、auto、整数
        :param isNormal: 是否将新增设备设置为normal类型
        :return: 安装后的设备对象
        """

        if altitudeU is None:
            return None

        newDevice = IDN设备(
            altitudeU=0
        )

        replacedDevice = self._tryReplaceDevice(
            newDevice=newDevice,
            wishType="TR"
        )

        if replacedDevice is not None:
            self.idnPosition = replacedDevice.altitudeU
            self.deviceList.append(replacedDevice)
            return replacedDevice

        idnPosition = self._installDeviceToPosition(
            altitudeU=altitudeU,
            height=self.IDN_HEIGHT,
            deviceName="IDN",
            pdu=False
        )

        if idnPosition is None:
            return None

        idnDevice = IDN设备(
            altitudeU=idnPosition
        )

        if isNormal:
            idnDevice.setDevType("normal")

        self.idnPosition = idnPosition
        self.deviceList.append(idnDevice)

        return idnDevice

    def installDDN(self,
                   altitudeU: int | Literal["auto"] | None,
                   isNormal: bool = False) -> Optional[Device]:
        """安装DDN设备

        :param altitudeU: DDN设备海拔，支持None、auto、整数
        :param isNormal: 是否将新增设备设置为normal类型
        :return: 安装后的设备对象
        """

        if altitudeU is None:
            return None

        newDevice = DDN设备(
            altitudeU=0
        )

        replacedDevice = self._tryReplaceDevice(
            newDevice=newDevice,
            wishType="TR"
        )

        if replacedDevice is not None:
            self.ddnPosition = replacedDevice.altitudeU
            self.deviceList.append(replacedDevice)
            return replacedDevice

        ddnPosition = self._installDeviceToPosition(
            altitudeU=altitudeU,
            height=self.DDN_HEIGHT,
            deviceName="DDN",
            pdu=False
        )

        if ddnPosition is None:
            return None

        ddnDevice = DDN设备(
            altitudeU=ddnPosition
        )

        if isNormal:
            ddnDevice.setDevType("normal")

        self.ddnPosition = ddnPosition
        self.deviceList.append(ddnDevice)

        return ddnDevice

    def installIDF(self,
                   altitudeU: int | Literal["auto"] | None) -> Optional[Device]:
        """安装成端IDF设备

        :param altitudeU: IDF设备海拔，支持None、auto、整数
        :return: 安装后的设备对象
        :notice: 如果IDN已经安装，优先尝试紧贴IDN下方，其次紧贴IDN上方
        """

        if altitudeU is None:
            return None

        newDevice = EdgedIDF(
            altitudeU=0
        )

        replacedDevice = self._tryReplaceDevice(
            newDevice=newDevice,
            wishType="TR"
        )

        if replacedDevice is not None:
            self.idfPosition = replacedDevice.altitudeU
            self.deviceList.append(replacedDevice)
            return replacedDevice

        idfPosition = self._tryInstallIDFAroundMainDevice()

        if idfPosition is None:
            idfPosition = self._installDeviceToPosition(
                altitudeU=altitudeU,
                height=self.IDF_HEIGHT,
                deviceName="IDF",
                pdu=False
            )

        if idfPosition is None:
            return None

        idfDevice = EdgedIDF(
            altitudeU=idfPosition
        )

        self.idfPosition = idfPosition
        self.deviceList.append(idfDevice)

        return idfDevice

    def calculate(self) -> List[Device]:
        """执行U数计算，返回完整设备列表

        :return: 完整设备列表
        """

        return self._validDeviceList(self.deviceList)

    def _tryInstallIDFAroundMainDevice(self) -> Optional[int]:
        """尝试将IDF安装在IDN或DDN附近

        :return: IDF安装位置
        :notice: 优先尝试安装在IDN下方；如果IDN不存在，则尝试安装在DDN下方
        """

        referencePosition = self._getIDFReferencePosition()

        if referencePosition is None:
            return None

        # 优先安装在参考设备紧贴下方
        downPosition = referencePosition - self.IDF_HEIGHT - 1

        # 从参考设备下方开始，继续向下寻找可用位置
        for position in range(downPosition, 0, -1):
            if self._isPositionAvailable(
                startPos=position,
                height=self.IDF_HEIGHT,
                currentOccupied=self.occupiedPositions
            ):
                return self._installDeviceToPosition(
                    altitudeU=position,
                    height=self.IDF_HEIGHT,
                    deviceName="IDF",
                    pdu=False
                )

        return None


    def _getIDFReferencePosition(self) -> Optional[int]:
        """获取IDF参考安装设备位置

        :return: IDN位置或DDN位置
        """

        if self.idnPosition is not None:
            return self.idnPosition

        if self.ddnPosition is not None:
            return self.ddnPosition

        return None

    def _installDeviceToPosition(self,
                                 altitudeU: int | Literal["auto"] | None,
                                 height: int,
                                 deviceName: str,
                                 pdu: bool = False) -> Optional[int]:
        """安装一个设备并更新占用位置

        :param altitudeU: 设备海拔，支持None、auto、整数
        :param height: 设备高度
        :param deviceName: 设备名称
        :param pdu: 是否按照PDU策略寻找安装位置
        :return: 安装位置
        """

        if altitudeU is None or altitudeU is False:
            return None

        if altitudeU == "auto":
            position = self._findBestPosition(
                height=height,
                currentOccupied=self.occupiedPositions,
                pdu=pdu
            )

            if position is None:
                raise ValueError(f"无法为{deviceName}找到合适的安装位置")

        else:
            if not isinstance(altitudeU, int):
                raise ValueError(f"{deviceName}位置参数类型错误: {altitudeU}")

            # 指定位置安装可无视1U间隔
            if not self._isPositionAvailable(altitudeU, height, self.occupiedPositions, True):
                raise ValueError(f"{deviceName}指定位置{altitudeU}U不可用")

            position = altitudeU

        for i in range(height):
            self.occupiedPositions.add(position + i)

        self.deviceAltitudeUList.append(position)
        self.deviceHeightUList.append(height)

        return position

    def _checkDevicePosition(self):
        """检查已有设备位置是否合法"""

        for pos, height in zip(self.deviceAltitudeUList, self.deviceHeightUList):
            
            if pos < 0 or pos + height - 1 > self.TOTAL_HEIGHT - 1:
                raise ValueError(
                    f"设备位置无效: 位置{pos}, 高度{height} 超出屏柜范围"
                )

    @staticmethod
    def _createOccupiedPositionSet(positions: List[int], heights: List[int]) -> set:
        """创建已占用U位集合"""

        occupiedSet = set()

        for pos, height in zip(positions, heights):
            for i in range(height):
                occupiedSet.add(pos + i)

        return occupiedSet

    def _isPositionAvailable(self,
                            startPos: int,
                            height: int,
                            currentOccupied: set,
                            isReplace: bool = False) -> bool:
        """检查指定起始位置是否可安装指定高度的设备"""

        minPos = startPos
        maxPos = startPos + height - 1

        borderSpace = (
            self.MIN_BORDER_SPACE_REPLACE
            if isReplace
            else self.MIN_BORDER_SPACE
        )

        minAllowedPos = borderSpace
        maxAllowedPos = self.TOTAL_HEIGHT - borderSpace - 1

        if minPos < minAllowedPos:
            return False

        if maxPos > maxAllowedPos:
            return False

        for i in range(height):
            if (startPos + i) in currentOccupied:
                return False

        # 与已有设备至少间隔1U
        if (startPos - 1) in currentOccupied:
            return False

        if (startPos + height) in currentOccupied:
            return False

        return True

    def _findBestPosition(self,
                          height: int,
                          currentOccupied: set,
                          pdu: bool = False) -> Optional[int]:
        """查找最佳安装位置"""

        availablePositions = []

        minStart = self.MIN_BORDER_SPACE
        maxStart = self.TOTAL_HEIGHT - self.MIN_BORDER_SPACE - height

        if pdu:
            for startPos in range(maxStart, minStart - 1, -1):
                if self._isPositionAvailable(startPos, height, currentOccupied):
                    availablePositions.append(startPos)

            if availablePositions:
                return max(availablePositions)

            return None

        for startPos in range(minStart, maxStart + 1):
            if self._isPositionAvailable(startPos, height, currentOccupied):
                minDistanceToDevice = float("inf")

                for devicePos in self.deviceAltitudeUList:
                    targetCenter = startPos + (height - 1) / 2
                    deviceIndex = self.deviceAltitudeUList.index(devicePos)
                    deviceHeight = self.deviceHeightUList[deviceIndex]
                    deviceCenter = devicePos + (deviceHeight - 1) / 2

                    distance = abs(targetCenter - deviceCenter)
                    minDistanceToDevice = min(minDistanceToDevice, distance)

                if len(self.deviceAltitudeUList) == 0:
                    targetCenter = startPos + (height - 1) / 2
                    distanceToCenter = abs(targetCenter - (self.TOTAL_HEIGHT - 1) / 2)
                    minDistanceToDevice = -distanceToCenter

                availablePositions.append((startPos, minDistanceToDevice))

        if not availablePositions:
            return None

        availablePositions.sort(key=lambda x: -x[0])
        availablePositions.sort(key=lambda x: x[1])

        return availablePositions[0][0]

    def _copyExistedDeviceList(self) -> List[ExistedDevice]:
        """复制已有设备列表"""

        return self.existedDeviceList.copy()

    def _tryReplaceDevice(self,
                        newDevice: Device,
                        wishType="TP") -> Optional[Device]:
        """尝试使用新设备替换已有的可替换设备

        :param newDevice: 新设备
        :param wishType:  期望替换标记，例如TP、TR
        :return: 替换后的新设备
        """

        matchedExistedDeviceList: List[ExistedDevice] = [
            existedDevice
            for existedDevice in self.existedDeviceList
            if existedDevice.devType == "replace"
            and getattr(existedDevice, "signType", None) == wishType
        ]

        if not matchedExistedDeviceList:
            return None

        for existedDevice in matchedExistedDeviceList:
            currentOccupied = self._occupiedPositionsWithoutDevice(existedDevice)

            replacePosition = self._findReplacePositionAroundDevice(
                existedDevice=existedDevice,
                newDevice=newDevice,
                currentOccupied=currentOccupied
            )

            if replacePosition is None:
                continue

            try:
                newDevice.altitudeU = replacePosition
                replacedDevice = existedDevice.replacedWithNewDevice(newDevice, wishType)  # type: ignore
                replacedDevice.altitudeU = replacePosition

                self._applyReplaceDevicePosition(
                    existedDevice=existedDevice,
                    replacedDevice=replacedDevice
                )

                return replacedDevice

            except Exception:
                continue

        raise ValueError(
            f"{newDevice.name}无法替换已有设备，"
            f"虽然存在标记为<{wishType}>的可替换设备，"
            "但新设备高度不匹配，且整个屏柜中未找到可安装位置"
        )

    def _occupiedPositionsWithoutDevice(self, existedDevice: ExistedDevice) -> set:
        """获取移除指定旧设备后的占用U位集合"""

        currentOccupied = self.occupiedPositions.copy()

        for i in range(existedDevice.heightU):
            currentOccupied.discard(existedDevice.altitudeU + i)

        return currentOccupied

    def _findReplacePositionAroundDevice(self,
                                        existedDevice: ExistedDevice,
                                        newDevice: Device,
                                        currentOccupied: set) -> Optional[int]:
        """在被替换设备附近寻找新设备可安装位置"""

        for position in self._replaceCandidatePositionList(
                basePosition=existedDevice.altitudeU,
                height=newDevice.heightU,
                isReplace=True
        ):
            if self._isPositionAvailable(
                    startPos=position,
                    height=newDevice.heightU,
                    currentOccupied=currentOccupied,
                    isReplace=True
            ):
                return position

        return None

    def _replaceCandidatePositionList(self,
                                    basePosition: int,
                                    height: int,
                                    isReplace: bool = False) -> List[int]:
        """获取替换设备候选安装位置列表

        优先使用原位置；如果原位置不可用，再按照上下邻域逐步扩展搜索。
        """

        borderSpace = (
            self.MIN_BORDER_SPACE_REPLACE
            if isReplace
            else self.MIN_BORDER_SPACE
        )

        minStart = borderSpace
        maxStart = self.TOTAL_HEIGHT - borderSpace - height

        if maxStart < minStart:
            return []

        candidateList: List[int] = []
        usedPositionSet = set()

        def addCandidate(position: int):
            if position < minStart or position > maxStart:
                return

            if position in usedPositionSet:
                return

            candidateList.append(position)
            usedPositionSet.add(position)

        # 先尝试旧设备原位置
        addCandidate(basePosition)

        # 再向上下邻域扩展
        for offset in range(1, self.TOTAL_HEIGHT):
            addCandidate(basePosition + offset)
            addCandidate(basePosition - offset)

        return candidateList


    def _applyReplaceDevicePosition(self,
                                    existedDevice: ExistedDevice,
                                    replacedDevice: Device):
        """应用替换后的设备位置占用信息"""

        # 删除旧设备占用位
        for i in range(existedDevice.heightU):
            self.occupiedPositions.discard(existedDevice.altitudeU + i)

        # 添加新设备占用位
        for i in range(replacedDevice.heightU):
            self.occupiedPositions.add(replacedDevice.altitudeU + i)

        # 更新位置列表，避免后续自动安装时继续参考已被替换的旧设备高度
        for index, (altitudeU, heightU) in enumerate(
                zip(self.deviceAltitudeUList, self.deviceHeightUList)
        ):
            if (
                    altitudeU == existedDevice.altitudeU
                    and heightU == existedDevice.heightU
            ):
                self.deviceAltitudeUList.pop(index)
                self.deviceHeightUList.pop(index)
                break

        self.deviceAltitudeUList.append(replacedDevice.altitudeU)
        self.deviceHeightUList.append(replacedDevice.heightU)


    @staticmethod
    def _validDeviceList(deviceList: List[Device]) -> List[Device]:
        """过滤被丢弃的旧设备"""

        return [
            device for device in deviceList
            if not device.isDropped
        ]