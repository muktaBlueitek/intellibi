import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

const PDF_MARGIN_MM = 10

/**
 * Capture a DOM node as a multi-page A4 PDF (portrait).
 * Long dashboards are split across pages by offsetting the same image slice.
 */
export async function exportElementToPdf(
  element: HTMLElement,
  fileName: string
): Promise<void> {
  const canvas = await html2canvas(element, {
    scale: 2,
    useCORS: true,
    logging: false,
    backgroundColor: '#ffffff',
    scrollX: 0,
    scrollY: -window.scrollY,
  })

  const imgData = canvas.toDataURL('image/jpeg', 0.92)
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  })

  const pageWidth = pdf.internal.pageSize.getWidth()
  const pageHeight = pdf.internal.pageSize.getHeight()
  const contentWidth = pageWidth - 2 * PDF_MARGIN_MM
  const contentHeight = pageHeight - 2 * PDF_MARGIN_MM

  const imgWidth = contentWidth
  const imgHeight = (canvas.height * imgWidth) / canvas.width

  let heightLeft = imgHeight
  let position = PDF_MARGIN_MM

  pdf.addImage(imgData, 'JPEG', PDF_MARGIN_MM, position, imgWidth, imgHeight)
  heightLeft -= contentHeight

  while (heightLeft > 0.5) {
    position = heightLeft - imgHeight + PDF_MARGIN_MM
    pdf.addPage()
    pdf.addImage(imgData, 'JPEG', PDF_MARGIN_MM, position, imgWidth, imgHeight)
    heightLeft -= contentHeight
  }

  pdf.save(fileName)
}
