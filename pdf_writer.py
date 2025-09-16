from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch
import re

def write_summary_pdf(summary_markdown: str, output_path: str):
	doc = SimpleDocTemplate(output_path, pagesize=LETTER,
							leftMargin=0.75*inch, rightMargin=0.75*inch,
							topMargin=0.75*inch, bottomMargin=0.75*inch)

	styles = getSampleStyleSheet()
	heading = ParagraphStyle(name="HeadingLarge",
							 parent=styles["Heading2"],
							 fontSize=20,
							 leading=24,
							 spaceAfter=12)
	bullet = ParagraphStyle(name="BulletText",
							 parent=styles["BodyText"],
							 fontSize=11,
							 leading=14)

	story = []

	sections = re.split(r"^###\s+", summary_markdown, flags=re.MULTILINE)
	for block in sections:
		block = block.strip()
		if not block:
			continue
		lines = block.splitlines()
		title = lines[0].strip()
		items = []
		for line in lines[1:]:
			if re.match(r"^[-*]\s+", line):
				items.append(re.sub(r"^[-*]\s+", "", line).strip())
			elif line.strip():
				if items:
					items[-1] += " " + line.strip()

		story.append(Paragraph(title, heading))
		if items:
			lf = ListFlowable([ListItem(Paragraph(it, bullet)) for it in items],
							  bulletType='bullet', start='-')
			story.append(lf)
		story.append(Spacer(1, 0.25*inch))

	doc.build(story)


