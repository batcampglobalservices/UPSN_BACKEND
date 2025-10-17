from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings
import os


def generate_result_pdf(result_summary):
    """
    Generate a PDF result sheet for a pupil
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    
    # Add school logo if exists
    try:
        from media_manager.models import SchoolLogo
        logo = SchoolLogo.objects.first()
        if logo and logo.logo:
            logo_path = os.path.join(settings.MEDIA_ROOT, str(logo.logo))
            if os.path.exists(logo_path):
                img = Image(logo_path, width=1*inch, height=1*inch)
                elements.append(img)
                elements.append(Spacer(1, 12))
    except:
        pass
    
    # School name and title
    elements.append(Paragraph("SCHOOL NAME", title_style))
    elements.append(Paragraph("PUPIL RESULT SHEET", heading_style))
    elements.append(Spacer(1, 12))
    
    # Pupil information
    pupil = result_summary.pupil
    try:
        pupil_class = pupil.pupil_profile.pupil_class.name
    except:
        pupil_class = "N/A"
    
    pupil_info = [
        ['Pupil Name:', pupil.full_name, 'Class:', pupil_class],
        ['Pupil ID:', pupil.username, 'Session:', result_summary.session.name],
        ['Term:', result_summary.get_term_display(), '', ''],
    ]
    
    pupil_table = Table(pupil_info, colWidths=[2*inch, 2.5*inch, 1.5*inch, 2*inch])
    pupil_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(pupil_table)
    elements.append(Spacer(1, 20))
    
    # Results table
    from .models import Result
    results = Result.objects.filter(
        pupil=pupil,
        session=result_summary.session,
        term=result_summary.term
    ).order_by('subject__name')
    
    # Table headers
    result_data = [
        ['S/N', 'Subject', 'Test (30)', 'Exam (70)', 'Total (100)', 'Grade', 'Remark']
    ]
    
    # Add results
    for idx, result in enumerate(results, 1):
        remark = 'Excellent' if result.grade == 'A' else \
                'Very Good' if result.grade == 'B' else \
                'Good' if result.grade == 'C' else \
                'Pass' if result.grade == 'D' else 'Fail'
        
        result_data.append([
            str(idx),
            result.subject.name,
            f"{result.test_score:.2f}",
            f"{result.exam_score:.2f}",
            f"{result.total:.2f}",
            result.grade,
            remark
        ])
    
    # Add summary row
    result_data.append(['', '', '', '', '', '', ''])
    result_data.append([
        '', 
        'TOTAL SUBJECTS:', 
        str(result_summary.total_subjects), 
        'AVERAGE:', 
        f"{result_summary.average_score:.2f}",
        'GRADE:',
        result_summary.overall_grade
    ])
    
    result_table = Table(result_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 1.2*inch])
    result_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A90E2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        
        # Data rows
        ('FONT', (0, 1), (-1, -3), 'Helvetica', 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -3), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -3), [colors.white, colors.HexColor('#F5F5F5')]),
        
        # Summary row
        ('FONT', (1, -1), (-1, -1), 'Helvetica-Bold', 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F4F8')),
        ('ALIGN', (1, -1), (-1, -1), 'LEFT'),
    ]))
    
    elements.append(result_table)
    elements.append(Spacer(1, 30))
    
    # Comments section
    if result_summary.teacher_comment:
        elements.append(Paragraph(f"<b>Class Teacher's Comment:</b> {result_summary.teacher_comment}", normal_style))
        elements.append(Spacer(1, 12))
    
    if result_summary.principal_comment:
        elements.append(Paragraph(f"<b>Principal's Comment:</b> {result_summary.principal_comment}", normal_style))
        elements.append(Spacer(1, 12))
    
    # Signature section
    elements.append(Spacer(1, 30))
    signature_data = [
        ['_____________________', '', '_____________________'],
        ["Class Teacher's Signature", '', "Principal's Signature"],
    ]
    
    signature_table = Table(signature_data, colWidths=[2.5*inch, 2*inch, 2.5*inch])
    signature_table.setStyle(TableStyle([
        ('FONT', (0, 1), (-1, 1), 'Helvetica-Bold', 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(signature_table)
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
