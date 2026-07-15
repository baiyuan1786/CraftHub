##########################################################################################################
#   Description: CAD块参照打印LSP构建器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from pathlib import Path
from typing import Optional


class CadBlockPrinterLspBuilder:
    '''CAD块参照打印LSP构建器'''

    DEFAULT_BLOCK_PREFIX = "GEDI_TQ"
    DEFAULT_ATTR_NAME = ""
    DEFAULT_PDF_DEVICE = "DWG To PDF.pc3"
    DEFAULT_PDF_MEDIA_NAME = "ISO_full_bleed_A3_(420.00_x_297.00_MM)"
    DEFAULT_FRAME_MARGIN = 5.0
    DEFAULT_PLOT_ROTATION = 0

    DONE_FLAG_FILE_NAME = "_cadBlockPrinter_done.flag"
    LSP_COMMAND_NAME = "BatchPlotGEDIFromPython"

    def __init__(
            self,
            blockPrefix: str = DEFAULT_BLOCK_PREFIX,
            pdfDevice: str = DEFAULT_PDF_DEVICE,
            pdfMediaName: str = DEFAULT_PDF_MEDIA_NAME,
            frameMargin: float = DEFAULT_FRAME_MARGIN,
            plotRotation: int = DEFAULT_PLOT_ROTATION,
    ):
        '''初始化CAD块参照打印LSP构建器'''

        self.blockPrefix = blockPrefix
        self.pdfDevice = pdfDevice
        self.pdfMediaName = pdfMediaName
        self.frameMargin = frameMargin
        self.plotRotation = plotRotation

    def buildLspText(
            self,
            outputDir: Path,
            fileStem: str,
            attrName: Optional[str] = None,
    ) -> str:
        '''构建AutoLISP脚本文本'''

        outputDirText = self._toLspPath(outputDir)
        doneFlagPathText = self._toLspPath(outputDir / self.DONE_FLAG_FILE_NAME)

        blockPrefixText = self._escapeLspString(self.blockPrefix)
        attrNameText = self._escapeLspString(attrName or self.DEFAULT_ATTR_NAME)
        pdfDeviceText = self._escapeLspString(self.pdfDevice)
        pdfMediaNameText = self._escapeLspString(self.pdfMediaName)
        fileStemText = self._escapeLspString(fileStem)

        return f'''
(vl-load-com)

(setq *FrameBlockPrefix* "{blockPrefixText}")
(setq *SortAttrName* "{attrNameText}")

(setq *PDFDevice* "{pdfDeviceText}")
(setq *PDFMediaName* "{pdfMediaNameText}")
(setq *FrameMargin* {self.frameMargin})
(setq *PlotRotation* {self.plotRotation})

(setq *OutputDir* "{outputDirText}")
(setq *DoneFlagPath* "{doneFlagPathText}")
(setq *FileStem* "{fileStemText}")

(defun _AttrEnabled ()
  (and *SortAttrName* (> (strlen *SortAttrName*) 0))
)

(defun _StartsWith (s prefix /)
  (and s prefix
       (>= (strlen s) (strlen prefix))
       (= (strcase (substr s 1 (strlen prefix)))
          (strcase prefix)))
)

(defun _SafeFileName (s / bad ch)
  (if (not s)
    (setq s "")
  )

  (setq bad '("\\\\" "/" ":" "*" "?" "\\\"" "<" ">" "|"))

  (foreach ch bad
    (while (vl-string-search ch s)
      (setq s (vl-string-subst "_" ch s))
    )
  )

  s
)

(defun _PadNumber (n / s)
  (setq s (itoa n))

  (cond
    ((< n 10) (strcat "00" s))
    ((< n 100) (strcat "0" s))
    (T s)
  )
)

(defun _MakePointVariant (pt / arr)
  (setq arr (vlax-make-safearray vlax-vbDouble '(0 . 1)))
  (vlax-safearray-fill arr (list (car pt) (cadr pt)))
  (vlax-make-variant arr)
)

(defun _GetBlockAttr (blk attrName / obj attrs i att val)
  (setq obj (vlax-ename->vla-object blk))

  (if (and obj (= (vla-get-HasAttributes obj) :vlax-true))
    (progn
      (setq attrs (vlax-invoke obj 'GetAttributes))
      (setq i 0)
      (setq val nil)

      (while (and (< i (length attrs)) (not val))
        (setq att (nth i attrs))

        (if (= (strcase (vla-get-TagString att))
               (strcase attrName))
          (setq val (vla-get-TextString att))
        )

        (setq i (1+ i))
      )

      val
    )
  )
)

(defun _GetBBox (ename / obj minpt maxpt)
  (setq obj (vlax-ename->vla-object ename))
  (vla-getBoundingBox obj 'minpt 'maxpt)

  (list
    (vlax-safearray->list minpt)
    (vlax-safearray->list maxpt)
  )
)

(defun _ExpandBBox (bbox margin / p1 p2)
  (setq p1 (car bbox))
  (setq p2 (cadr bbox))

  (list
    (list (- (car p1) margin) (- (cadr p1) margin))
    (list (+ (car p2) margin) (+ (cadr p2) margin))
  )
)

(defun _BBoxCenter (bbox / p1 p2)
  (setq p1 (car bbox))
  (setq p2 (cadr bbox))

  (list
    (/ (+ (car p1) (car p2)) 2.0)
    (/ (+ (cadr p1) (cadr p2)) 2.0)
  )
)

(defun _CollectFrames (/ ss i ename obj name attrVal frames bbox center)
  (setq frames '())
  (setq ss (ssget "X" '((0 . "INSERT") (410 . "Model"))))

  (if ss
    (progn
      (setq i 0)

      (while (< i (sslength ss))
        (setq ename (ssname ss i))
        (setq obj (vlax-ename->vla-object ename))

        (setq name
          (if (vlax-property-available-p obj 'EffectiveName)
            (vla-get-EffectiveName obj)
            (vla-get-Name obj)
          )
        )

        (if (_StartsWith name *FrameBlockPrefix*)
          (progn
            (setq attrVal "")

            (if (_AttrEnabled)
              (setq attrVal (_GetBlockAttr ename *SortAttrName*))
            )

            (if (or (not (_AttrEnabled)) attrVal)
              (progn
                (setq bbox (_GetBBox ename))
                (setq center (_BBoxCenter bbox))

                (setq frames
                  (cons
                    (list ename attrVal bbox center i)
                    frames
                  )
                )
              )
            )
          )
        )

        (setq i (1+ i))
      )
    )
  )

  (reverse frames)
)

(defun _SortFrames (frames)
  (if (_AttrEnabled)
    (vl-sort frames
      '(lambda (a b)
         (< (strcase (nth 1 a))
            (strcase (nth 1 b)))
       )
    )
    frames
  )
)

(defun _GetPdfBaseName (item idx / attrVal)
  (setq attrVal (nth 1 item))

  (if (and (_AttrEnabled) attrVal (> (strlen attrVal) 0))
    (_SafeFileName attrVal)
    (_SafeFileName (strcat *FileStem* "_" (_PadNumber idx)))
  )
)

(defun _PlotToPDF (path p1 p2 / acad doc layout plot)
  (setq acad (vlax-get-acad-object))
  (setq doc (vla-get-ActiveDocument acad))
  (setq layout (vla-Item (vla-get-Layouts doc) "Model"))
  (setq plot (vla-get-Plot doc))

  (setvar "BACKGROUNDPLOT" 0)
  (setvar "FILEDIA" 0)
  (setvar "CMDDIA" 0)

  (vla-put-ConfigName layout *PDFDevice*)
  (vla-RefreshPlotDeviceInfo layout)

  (vla-put-CanonicalMediaName layout *PDFMediaName*)
  (vla-put-PaperUnits layout 1)

  (vla-put-PlotRotation layout *PlotRotation*)

  (vla-SetWindowToPlot layout
    (_MakePointVariant p1)
    (_MakePointVariant p2)
  )

  (vla-put-PlotType layout 4)
  (vla-put-CenterPlot layout :vlax-true)
  (vla-put-UseStandardScale layout :vlax-true)
  (vla-put-StandardScale layout 0)

  (vla-PlotToFile plot path *PDFDevice*)
)

(defun _WriteDoneFlag (/ file)
  (setq file (open *DoneFlagPath* "w"))
  (write-line "done" file)
  (close file)
)

(defun c:BatchPlotGEDIFromPython (/ frames idx item bbox win p1 p2 pdfBaseName pdfPath)
  (setq frames (_CollectFrames))
  (setq frames (_SortFrames frames))

  (if (not frames)
    (progn
      (princ "\\n未找到可打印的图框。")
    )
    (progn
      (princ (strcat "\\n找到 " (itoa (length frames)) " 个图框。"))

      (setq idx 1)

      (foreach item frames
        (setq bbox (nth 2 item))
        (setq win (_ExpandBBox bbox *FrameMargin*))
        (setq p1 (car win))
        (setq p2 (cadr win))

        (setq pdfBaseName (_GetPdfBaseName item idx))
        (setq pdfPath (strcat *OutputDir* "/" pdfBaseName ".pdf"))

        (princ (strcat "\\n导出: " pdfPath))

        (_PlotToPDF pdfPath p1 p2)

        (setq idx (1+ idx))
      )

      (princ "\\n全部PDF导出完成。")
    )
  )

  (_WriteDoneFlag)

  (princ)
)
'''

    def writeLspFile(
            self,
            lspPath: Path,
            outputDir: Path,
            fileStem: str,
            attrName: Optional[str] = None,
    ):
        '''写入AutoLISP脚本文件'''

        lspText = self.buildLspText(
            outputDir=outputDir,
            fileStem=fileStem,
            attrName=attrName,
        )

        lspPath.write_text(lspText, encoding="utf-8")

    def toLspPath(self, path: Path) -> str:
        '''转换为AutoLISP可读取路径'''

        return self._toLspPath(path)

    def _toLspPath(self, path: Path) -> str:
        '''转换为AutoLISP可读取路径'''

        return self._escapeLspString(str(path).replace("\\", "/"))

    def _escapeLspString(self, text: str) -> str:
        '''转义AutoLISP字符串'''

        return text.replace("\\", "\\\\").replace('"', '\\"')