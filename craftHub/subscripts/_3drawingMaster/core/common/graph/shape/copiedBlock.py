##########################################################################################################
#   Description: 复制块类
#                将当前文件或外部DXF文件中的某个块复制为一个新的块
#                注意该复制可能不完全，至少目前发现无法复制表格类以及部分复杂block
#                注意增强属性是块参照的属性，而不是块的属性，复制块定义无法复制块参照上的增强属性值
#
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from pathlib import Path
from typing import Optional

from ezdxf import recover
from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout

from craftHub.tool import GLog

from .usedBlock import NewBlock


class CopiedBlock(NewBlock):
    '''复制块类，只允许复制为新块'''

    def __init__(
            self,
            doc: Drawing,
            sourceBlockName: str,
            blockName: Optional[str] = None,
            sourceDocPath: Optional[Path] = None,
            includeNestedBlock: bool = True
    ) -> None:
        """复制源块为一个新的目标块

        :param doc: 当前文件
        :param sourceBlockName: 源块名称
        :param blockName: 目标块名称，设置为None表示自动命名
        :param sourceDocPath: 源模板文件路径，设置为None表示从当前文件复制块
        :param includeNestedBlock: 是否复制嵌套块
        """

        self.doc = doc
        self.sourceDocPath = sourceDocPath
        self.sourceBlockName = sourceBlockName
        self.includeNestedBlock = includeNestedBlock

        self.sourceDoc = self._loadSourceDoc()

        super().__init__(
            doc=doc,
            blockName=blockName
        )

        self.copyBlock(
            sourceBlockName=sourceBlockName,
            targetBlock=self.block,
            includeNestedBlock=includeNestedBlock
        )

    def _loadSourceDoc(self) -> Drawing:
        '''加载源文档'''

        if self.sourceDocPath is None:
            return self.doc

        try:
            sourceDoc, _ = recover.readfile(self.sourceDocPath)
            return sourceDoc

        except Exception as error:
            raise Exception(f"读取源模板文件失败: {str(error)}")

    def copyBlock(
            self,
            sourceBlockName: str,
            targetBlock: BlockLayout,
            includeNestedBlock: bool = True
    ) -> bool:
        """复制源块中的所有实体到目标块

        :param sourceBlockName: 源块名称
        :param targetBlock: 目标块
        :param includeNestedBlock: 是否复制嵌套块
        :return: 是否成功复制
        """

        if sourceBlockName not in self.sourceDoc.blocks:
            raise FileNotFoundError(f"源块不存在: '{sourceBlockName}'")

        sourceBlock = self.sourceDoc.blocks.get(sourceBlockName)

        if sourceBlock is None:
            raise ValueError(f"无法获取源块: '{sourceBlockName}'")

        try:
            successCount = 0

            for entity in sourceBlock:
                if self._copySingleEntity(
                        sourceEntity=entity,
                        targetBlock=targetBlock,
                        includeNestedBlock=includeNestedBlock
                ):
                    successCount += 1

            GLog.logInfo(
                f"'{sourceBlockName}' | 成功复制 {successCount}/{len(sourceBlock)} 个实体到新块 '{targetBlock.name}'"
            )

            self._copyBlockProperties(
                sourceBlock=sourceBlock,
                targetBlock=targetBlock
            )

            return successCount > 0

        except Exception as error:
            raise Exception(f"复制块实体失败: {str(error)}")

    def _copySingleEntity(
            self,
            sourceEntity,
            targetBlock: BlockLayout,
            includeNestedBlock: bool
    ) -> bool:
        '''复制单个实体'''

        try:
            entityType = sourceEntity.dxftype()

            if entityType == "INSERT":
                nestedBlockName = sourceEntity.dxf.name

                if includeNestedBlock:
                    self._copyNestedBlock(nestedBlockName)

            clonedEntity = sourceEntity.copy()
            targetBlock.add_entity(clonedEntity)

            return True

        except Exception as error:
            GLog.logInfo(f"复制实体失败: {str(error)}")
            return False

    def _copyNestedBlock(self, blockName: str) -> bool:
        '''复制嵌套块定义'''

        if blockName in self.doc.blocks:
            return True

        if blockName not in self.sourceDoc.blocks:
            GLog.logInfo(f"嵌套块不存在，跳过复制: '{blockName}'")
            return False

        sourceBlock = self.sourceDoc.blocks.get(blockName)

        if sourceBlock is None:
            GLog.logInfo(f"无法获取嵌套块，跳过复制: '{blockName}'")
            return False

        try:
            targetBlock = self.doc.blocks.new(
                name=blockName,
                base_point=sourceBlock.base_point
            )

            successCount = 0

            for entity in sourceBlock:
                if self._copySingleEntity(
                        sourceEntity=entity,
                        targetBlock=targetBlock,
                        includeNestedBlock=True
                ):
                    successCount += 1

            self._copyBlockProperties(
                sourceBlock=sourceBlock,
                targetBlock=targetBlock
            )

            GLog.logInfo(
                f"'{blockName}' | 成功复制嵌套块 {successCount}/{len(sourceBlock)} 个实体"
            )

            return True

        except Exception as error:
            GLog.logInfo(f"复制嵌套块失败: '{blockName}', {str(error)}")
            return False

    def _copyBlockProperties(self, sourceBlock: BlockLayout, targetBlock: BlockLayout) -> None:
        '''复制块的附加属性'''

        try:
            targetBlock.block.dxf.base_point = sourceBlock.base_point # type: ignore
        except Exception:
            pass

    def saveTargetDocument(self, filePath: Path) -> bool:
        '''保存目标文档'''

        try:
            self.doc.saveas(filePath)
            GLog.logInfo(f"成功保存到: {filePath}")
            return True

        except Exception as error:
            GLog.logInfo(f"保存文件失败: {str(error)}")
            return False