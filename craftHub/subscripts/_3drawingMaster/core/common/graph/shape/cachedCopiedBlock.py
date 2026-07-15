##########################################################################################################
#   Description: 缓存复制块类
#                如果目标块已经存在，则直接使用已有块
#                如果目标块不存在，则从源文件复制源块到当前文件中
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from pathlib import Path
from typing import Optional

from ezdxf import recover
from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout

from craftHub.tool import GLog

from .block import CustomBlock


class CachedCopiedBlock(CustomBlock):
    '''缓存复制块类，已有则复用，不存在则复制创建'''

    def __init__(
            self,
            doc: Drawing,
            blockName: str,
            sourceDocPath: Path,
            sourceBlockName: Optional[str] = None,
            includeNestedBlock: bool = True
    ) -> None:
        """初始化缓存复制块

        :param doc: 当前文档
        :param blockName: 当前文档中的目标块名, 如果本文档已有该块则停止复制
        :param sourceDocPath: 源模板文件路径
        :param sourceBlockName: 源块名称，设置为None表示与目标块名相同
        :param includeNestedBlock: 是否复制嵌套块
        """

        if sourceBlockName is None:
            sourceBlockName = blockName

        self.sourceDocPath = sourceDocPath
        self.sourceBlockName = sourceBlockName
        self.includeNestedBlock = includeNestedBlock
        self.sourceDoc: Optional[Drawing] = None

        # 这里允许调用已有块。
        # 如果 blockName 已存在，父类会直接获取已有块。
        # 如果 blockName 不存在，父类会创建新块。
        super().__init__(
            doc=doc,
            blockName=blockName,
            allowExisted=True
        )

        # 如果不是新块，说明已经成功复用了已有块，不需要再复制
        if not self.isNewBlock:
            GLog.logInfo(f"'{blockName}' | 已存在，跳过模板复制")
            return

        # 如果是新块，则从模板文件复制源块实体
        self.sourceDoc = self._loadSourceDoc(sourceDocPath)

        self.copyBlock(
            sourceBlockName=sourceBlockName,
            targetBlock=self.block,
            includeNestedBlock=includeNestedBlock
        )

    def _loadSourceDoc(self, sourceDocPath: Path) -> Drawing:
        '''加载源文档'''

        try:
            sourceDoc, _ = recover.readfile(sourceDocPath)
            return sourceDoc

        except Exception as error:
            raise Exception(f"读取源模板文件失败: {str(error)}")

    def copyBlock(
            self,
            sourceBlockName: str,
            targetBlock: BlockLayout,
            includeNestedBlock: bool = True
    ) -> bool:
        '''复制源块中的所有实体到目标块'''

        if self.sourceDoc is None:
            raise ValueError("源文档尚未加载，无法复制块")

        if sourceBlockName not in self.sourceDoc.blocks:
            raise FileNotFoundError(f"源块不存在: '{sourceBlockName}'")

        sourceBlock = self.sourceDoc.blocks.get(sourceBlockName)

        if sourceBlock is None:
            raise ValueError(f"无法获取源块: '{sourceBlockName}'")

        successCount = 0

        for entity in sourceBlock:
            if self._copySingleEntity(
                    sourceEntity=entity,
                    targetBlock=targetBlock,
                    includeNestedBlock=includeNestedBlock
            ):
                successCount += 1

        self._copyBlockProperties(
            sourceBlock=sourceBlock,
            targetBlock=targetBlock
        )

        GLog.logInfo(
            f"'{sourceBlockName}' | 成功复制 {successCount}/{len(sourceBlock)} 个实体到新块 '{targetBlock.name}'"
        )

        return successCount > 0

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

        if self.sourceDoc is None:
            return False

        if blockName in self.doc.blocks:
            return True

        if blockName not in self.sourceDoc.blocks:
            GLog.logInfo(f"嵌套块不存在，跳过复制: '{blockName}'")
            return False

        sourceBlock = self.sourceDoc.blocks.get(blockName)

        if sourceBlock is None:
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

    def _copyBlockProperties(
            self,
            sourceBlock: BlockLayout,
            targetBlock: BlockLayout
    ) -> None:
        '''复制块属性'''

        try:
            targetBlock.block.dxf.base_point = sourceBlock.base_point # type: ignore
        except Exception:
            pass