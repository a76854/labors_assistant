from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from langchain_core.tools import tool

from agent.state import LawsuitElementsSchema


@tool(args_schema=LawsuitElementsSchema)
def generate_legal_doc_tool(
  plaintiff: str,
  defendant: str,
  claim: str,
  amount: str,
  cause_of_action: str,
  facts_and_reasons: str,
  court_name: str,
) -> str:
  """
  法律文书生成工具：生成符合中国法院常用格式的《民事起诉状》。

  '【终极动作】当且仅当：1.已集齐四个案件要素；2.已调用检索工具查阅了法律；3.已向用户输出了案情分析评估后。你必须作为最后一步调用此工具，为用户生成标准的法律文书。'

  参数:
    plaintiff: 原告信息。
    defendant: 被告信息。
    claim: 诉讼请求。
    amount: 涉案金额。
    cause_of_action: 案由。
    facts_and_reasons: 事实与理由。
    court_name: 管辖法院名称。

  返回:
    生成结果说明与模拟下载链接。
  """
  try:
    output_dir = Path("./generated_docs")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"legal_doc_{timestamp}.docx"
    file_path = output_dir / filename

    doc = Document()

    # 统一正文样式，便于法院窗口打印审阅。
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "宋体"
    normal_style.font.size = Pt(12)

    title = doc.add_paragraph("民事起诉状")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.name = "宋体"
    title.runs[0].font.size = Pt(18)
    title.runs[0].bold = True

    doc.add_paragraph(f"案由：{cause_of_action}")
    doc.add_paragraph(f"受诉法院：{court_name}")
    doc.add_paragraph("")

    doc.add_paragraph(f"原告：{plaintiff}")
    doc.add_paragraph(f"被告：{defendant}")
    doc.add_paragraph("")

    doc.add_paragraph("诉讼请求：")
    claims = [line.strip() for line in claim.replace("；", "\n").split("\n") if line.strip()]
    if claims:
      for idx, claim_item in enumerate(claims, start=1):
        doc.add_paragraph(f"{idx}. {claim_item}")
    else:
      doc.add_paragraph(f"1. {claim}")
    doc.add_paragraph(f"诉讼标的金额：{amount}")
    doc.add_paragraph("")

    doc.add_paragraph("事实与理由：")
    facts_lines = [line.strip() for line in facts_and_reasons.split("\n") if line.strip()]
    if facts_lines:
      for line in facts_lines:
        doc.add_paragraph(f"{line}")
    else:
      doc.add_paragraph(facts_and_reasons)
    doc.add_paragraph("")

    doc.add_paragraph("证据和证据来源，证人姓名和住所：")
    doc.add_paragraph("1. 借条/合同等书证；")
    doc.add_paragraph("2. 银行转账记录、支付凭证；")
    doc.add_paragraph("3. 聊天记录、催告记录等电子数据；")
    doc.add_paragraph("4. 其他与案件事实相关的证据材料。")
    doc.add_paragraph("")

    doc.add_paragraph("此致")
    doc.add_paragraph(court_name)
    doc.add_paragraph("")
    doc.add_paragraph("具状人（原告）：________________")
    doc.add_paragraph(f"日期：{datetime.now().strftime('%Y年%m月%d日')}")
    doc.add_paragraph("")
    doc.add_paragraph("附：本起诉状副本及相关证据材料清单。")

    doc.save(str(file_path))

    download_link = f"http://127.0.0.1:8000/download/{filename}"
    return (
      "文书已生成成功。\n"
      f"文件名：{filename}\n"
      f"本地路径：{file_path.as_posix()}\n"
      f"下载链接：{download_link}"
    )
  except Exception as exc:
    return f"文书生成失败：{exc}"
