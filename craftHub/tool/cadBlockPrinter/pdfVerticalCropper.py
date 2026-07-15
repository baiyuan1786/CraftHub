##########################################################################################################
#   Description: PDF上下空白裁剪器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from pathlib import Path
from typing import Optional, Tuple

import fitz
from ..common.log import GLog

class PdfVerticalCropper:
    '''PDF上下空白裁剪器'''

    DEFAULT_RENDER_DPI = 144
    DEFAULT_WHITE_THRESHOLD = 245
    DEFAULT_MIN_CONTENT_RATIO = 0.001
    DEFAULT_PADDING_PT = 4.0

    POINT_PER_INCH = 72.0
    RGB_CHANNEL_COUNT = 3

    MIN_CROP_HEIGHT_PT = 50.0

    @classmethod
    def cropPdf(
            cls,
            inputPdfPath: Path,
            outputPdfPath: Path,
            renderDpi: int = DEFAULT_RENDER_DPI,
            whiteThreshold: int = DEFAULT_WHITE_THRESHOLD,
            minContentRatio: float = DEFAULT_MIN_CONTENT_RATIO,
            paddingPt: float = DEFAULT_PADDING_PT,
    ):
        '''裁剪PDF每一页的上下空白区域'''

        inputPdfPath = Path(inputPdfPath)
        outputPdfPath = Path(outputPdfPath)

        if not inputPdfPath.exists():
            raise FileNotFoundError(f"PDF文件不存在: {inputPdfPath}")

        if inputPdfPath.resolve() == outputPdfPath.resolve():
            raise ValueError("输入PDF和输出PDF不能是同一个文件")

        outputPdfPath.parent.mkdir(parents=True, exist_ok=True)

        pdfDoc = fitz.open(str(inputPdfPath))

        try:
            pageCount = len(pdfDoc)

            for pageIndex, page in enumerate(pdfDoc, start=1): # type: ignore
                GLog.logInfo(f"正在处理第 {pageIndex} / {pageCount} 页")

                cropRect = cls._getVerticalCropRect(
                    page=page,
                    renderDpi=renderDpi,
                    whiteThreshold=whiteThreshold,
                    minContentRatio=minContentRatio,
                    paddingPt=paddingPt,
                )

                if cropRect is None:
                    GLog.logInfo(f"第 {pageIndex} 页未检测到有效裁剪区域，跳过")
                    continue

                page.set_cropbox(cropRect)
                GLog.logInfo(f"第 {pageIndex} 页裁剪完成")

            pdfDoc.save(
                str(outputPdfPath),
                garbage=4,
                deflate=True,
            )
        finally:
            pdfDoc.close()

    @classmethod
    def _getVerticalCropRect(
            cls,
            page: fitz.Page,
            renderDpi: int,
            whiteThreshold: int,
            minContentRatio: float,
            paddingPt: float,
    ) -> Optional[fitz.Rect]:
        '''获取页面上下裁剪区域'''

        pageRect = page.rect

        contentBounds = cls._detectVerticalContentBounds(
            page=page,
            renderDpi=renderDpi,
            whiteThreshold=whiteThreshold,
            minContentRatio=minContentRatio,
        )

        if contentBounds is None:
            return None

        contentTopPt, contentBottomPt = contentBounds

        cropTop = max(pageRect.y0, contentTopPt - paddingPt)
        cropBottom = min(pageRect.y1, contentBottomPt + paddingPt)

        if cropBottom - cropTop < cls.MIN_CROP_HEIGHT_PT:
            return None

        return fitz.Rect(
            pageRect.x0,
            cropTop,
            pageRect.x1,
            cropBottom,
        )

    @classmethod
    def _detectVerticalContentBounds(
            cls,
            page: fitz.Page,
            renderDpi: int,
            whiteThreshold: int,
            minContentRatio: float,
    ) -> Optional[Tuple[float, float]]:
        '''识别页面内容的上下边界'''

        scaleFactor = renderDpi / cls.POINT_PER_INCH
        matrix = fitz.Matrix(scaleFactor, scaleFactor)

        pixmap = page.get_pixmap(
            matrix=matrix,
            colorspace=fitz.csRGB,
            alpha=False,
        )

        width = pixmap.width
        height = pixmap.height
        samples = pixmap.samples

        minContentPixelCount = max(1, int(width * minContentRatio))

        topRow = cls._findTopContentRow(
            samples=samples,
            width=width,
            height=height,
            whiteThreshold=whiteThreshold,
            minContentPixelCount=minContentPixelCount,
        )

        if topRow is None:
            return None

        bottomRow = cls._findBottomContentRow(
            samples=samples,
            width=width,
            height=height,
            whiteThreshold=whiteThreshold,
            minContentPixelCount=minContentPixelCount,
        )

        if bottomRow is None:
            return None

        pageRect = page.rect

        contentTopPt = pageRect.y0 + topRow / scaleFactor
        contentBottomPt = pageRect.y0 + (bottomRow + 1) / scaleFactor

        return contentTopPt, contentBottomPt

    @classmethod
    def _findTopContentRow(
            cls,
            samples: bytes,
            width: int,
            height: int,
            whiteThreshold: int,
            minContentPixelCount: int,
    ) -> Optional[int]:
        '''查找顶部内容行'''

        for rowIndex in range(height):
            if cls._isContentRow(
                    samples=samples,
                    rowIndex=rowIndex,
                    width=width,
                    whiteThreshold=whiteThreshold,
                    minContentPixelCount=minContentPixelCount,
            ):
                return rowIndex

        return None

    @classmethod
    def _findBottomContentRow(
            cls,
            samples: bytes,
            width: int,
            height: int,
            whiteThreshold: int,
            minContentPixelCount: int,
    ) -> Optional[int]:
        '''查找底部内容行'''

        for rowIndex in range(height - 1, -1, -1):
            if cls._isContentRow(
                    samples=samples,
                    rowIndex=rowIndex,
                    width=width,
                    whiteThreshold=whiteThreshold,
                    minContentPixelCount=minContentPixelCount,
            ):
                return rowIndex

        return None

    @classmethod
    def _isContentRow(
            cls,
            samples: bytes,
            rowIndex: int,
            width: int,
            whiteThreshold: int,
            minContentPixelCount: int,
    ) -> bool:
        '''判断某一行是否存在有效内容'''

        rowStart = rowIndex * width * cls.RGB_CHANNEL_COUNT
        rowEnd = rowStart + width * cls.RGB_CHANNEL_COUNT
        contentPixelCount = 0

        for pixelIndex in range(rowStart, rowEnd, cls.RGB_CHANNEL_COUNT):
            red = samples[pixelIndex]
            green = samples[pixelIndex + 1]
            blue = samples[pixelIndex + 2]

            if red < whiteThreshold or green < whiteThreshold or blue < whiteThreshold:
                contentPixelCount += 1

                if contentPixelCount >= minContentPixelCount:
                    return True

        return False
    
if __name__ == "__main__":
    PdfVerticalCropper.cropPdf(inputPdfPath = Path(r"E:\gzq\两网工勘工程\Aidn绘图\PDF\4\U0301 设备安装施工图（地区网分册）-云浮供电局地区idn2026.06.26_2merged.pdf"),
                               outputPdfPath = Path(r"E:\gzq\两网工勘工程\Aidn绘图\PDF\4\cropped.pdf"))
