#!/usr/bin/env python3
"""
Export APIs for Quotations
XLSX and PDF export functionality
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Dict, Any
import tempfile
from datetime import datetime
import xlsxwriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

from ..database.enhanced_models import EnhancedDatabaseManager, QuotationManager, QuotationItemManager
from ..api.auth import get_current_user

# Create router for export endpoints
router = APIRouter(prefix="/contractors", tags=["export"])

@router.get(
    "/quotations/{quotation_id}/export/xlsx",
    response_class=FileResponse,
    summary="📊 Export Quotation to XLSX",
    description="Export a quotation with all its items to an Excel file for download"
)
async def export_quotation_xlsx(
    quotation_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Export quotation to XLSX format"""
    try:
        # Initialize database managers
        db_manager = EnhancedDatabaseManager()
        quotation_manager = QuotationManager(db_manager)
        item_manager = QuotationItemManager(db_manager)
        
        # Get quotation details
        quotation = quotation_manager.get_quotation(quotation_id)
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        # Check if user owns the quotation or if they're an admin
        if quotation.get('user_id') != current_user['id'] and current_user.get('role') != 'admin':
            raise HTTPException(
                status_code=403, 
                detail="You can only export your own quotations unless you're an admin"
            )
        
        # Get quotation items
        items = item_manager.get_items_by_quotation(quotation_id)
        
        # Create temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quotation_{quotation_id}_{timestamp}.xlsx"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        
        # Create workbook and worksheet
        workbook = xlsxwriter.Workbook(temp_file.name)
        worksheet = workbook.add_worksheet('Quotation Details')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#D9E2F3',
            'border': 1
        })
        
        data_format = workbook.add_format({
            'border': 1,
            'align': 'left'
        })
        
        currency_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'border': 1,
            'align': 'right'
        })
        
        # Write quotation header
        worksheet.merge_range('A1:F1', f'QUOTATION #{quotation_id}', header_format)
        worksheet.merge_range('A2:F2', f'Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', data_format)
        
        # Write quotation details
        row = 4
        worksheet.write(row, 0, 'Quotation Name:', title_format)
        worksheet.write(row, 1, quotation.get('quotation_name', 'N/A'), data_format)
        row += 1
        
        worksheet.write(row, 0, 'Client Name:', title_format)
        worksheet.write(row, 1, quotation.get('client_name', 'N/A'), data_format)
        row += 1
        
        worksheet.write(row, 0, 'Status:', title_format)
        worksheet.write(row, 1, quotation.get('status', 'N/A'), data_format)
        row += 1
        
        worksheet.write(row, 0, 'Created Date:', title_format)
        worksheet.write(row, 1, quotation.get('created_at', 'N/A'), data_format)
        row += 1
        
        worksheet.write(row, 0, 'Total Cost:', title_format)
        worksheet.write(row, 1, quotation.get('total_cost', 0), currency_format)
        row += 2
        
        # Write items header
        worksheet.write(row, 0, 'ITEM DETAILS', header_format)
        worksheet.merge_range(f'A{row+1}:F{row+1}', '', data_format)
        row += 2
        
        # Write items table headers
        headers = ['Item Name', 'SKU/ID', 'Unit', 'Unit of Measure', 'Cost', 'Quantity', 'Total Cost']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, title_format)
        row += 1
        
        # Write items data
        for item in items:
            worksheet.write(row, 0, item.get('item_name', ''), data_format)
            worksheet.write(row, 1, item.get('sku', 'N/A'), data_format)
            worksheet.write(row, 2, item.get('unit', ''), data_format)
            worksheet.write(row, 3, item.get('unit_of_measure', ''), data_format)
            worksheet.write(row, 4, item.get('cost', 0), currency_format)
            worksheet.write(row, 5, item.get('quantity', 0), data_format)
            worksheet.write(row, 6, item.get('total_cost', 0), currency_format)
            row += 1
        
        # Write total summary
        row += 1
        worksheet.write(row, 5, 'TOTAL:', title_format)
        worksheet.write(row, 6, quotation.get('total_cost', 0), currency_format)
        
        # Set column widths
        worksheet.set_column('A:A', 25)  # Item Name
        worksheet.set_column('B:B', 15)  # SKU/ID
        worksheet.set_column('C:C', 15)  # Unit
        worksheet.set_column('D:D', 20)  # Unit of Measure
        worksheet.set_column('E:E', 12)  # Cost
        worksheet.set_column('F:F', 12)  # Quantity
        worksheet.set_column('G:G', 15)  # Total Cost
        
        workbook.close()
        
        # Return file for download
        return FileResponse(
            path=temp_file.name,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/quotations/{quotation_id}/export/pdf",
    response_class=FileResponse,
    summary="📄 Export Quotation to PDF",
    description="Export a quotation with all its items to a PDF file for download"
)
async def export_quotation_pdf(
    quotation_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Export quotation to PDF format"""
    try:
        # Initialize database managers
        db_manager = EnhancedDatabaseManager()
        quotation_manager = QuotationManager(db_manager)
        item_manager = QuotationItemManager(db_manager)
        
        # Get quotation details
        quotation = quotation_manager.get_quotation(quotation_id)
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        # Check if user owns the quotation or if they're an admin
        if quotation.get('user_id') != current_user['id'] and current_user.get('role') != 'admin':
            raise HTTPException(
                status_code=403, 
                detail="You can only export your own quotations unless you're an admin"
            )
        
        # Get quotation items
        items = item_manager.get_items_by_quotation(quotation_id)
        
        # Create temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quotation_{quotation_id}_{timestamp}.pdf"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
        # Create PDF document
        doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        normal_style = styles['Normal']
        
        # Add title
        story.append(Paragraph(f"QUOTATION #{quotation_id}", title_style))
        story.append(Spacer(1, 20))
        
        # Add generation date
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Add quotation details
        story.append(Paragraph("Quotation Details", heading_style))
        
        details_data = [
            ['Quotation Name:', quotation.get('quotation_name', 'N/A')],
            ['Client Name:', quotation.get('client_name', 'N/A')],
            ['Status:', quotation.get('status', 'N/A')],
            ['Created Date:', quotation.get('created_at', 'N/A')],
            ['Total Cost:', f"${quotation.get('total_cost', 0):,.2f}"]
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 20))
        
        # Add items section
        story.append(Paragraph("Item Details", heading_style))
        
        # Prepare items data
        items_data = [['Item Name', 'SKU/ID', 'Unit', 'Cost', 'Quantity', 'Total Cost']]
        
        for item in items:
            items_data.append([
                item.get('item_name', ''),
                item.get('sku', 'N/A'),
                item.get('unit', ''),
                f"${item.get('cost', 0):,.2f}",
                str(item.get('quantity', 0)),
                f"${item.get('total_cost', 0):,.2f}"
            ])
        
        # Add total row
        items_data.append(['', '', '', '', 'TOTAL:', f"${quotation.get('total_cost', 0):,.2f}"])
        
        items_table = Table(items_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(items_table)
        
        # Build PDF
        doc.build(story)
        
        # Return file for download
        return FileResponse(
            path=temp_file.name,
            filename=filename,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/contractors/{user_id}/quotations/export/xlsx",
    response_class=FileResponse,
    summary="📊 Export All Contractor Quotations to XLSX",
    description="Export all quotations for a specific contractor with all items to an Excel file"
)
async def export_contractor_quotations_xlsx(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Export all contractor quotations to XLSX format"""
    try:
        # Initialize database managers
        db_manager = EnhancedDatabaseManager()
        quotation_manager = QuotationManager(db_manager)
        item_manager = QuotationItemManager(db_manager)
        
        # Check if user is accessing their own data or if they're an admin
        if user_id != current_user['id'] and current_user.get('role') != 'admin':
            raise HTTPException(
                status_code=403, 
                detail="You can only export your own quotations unless you're an admin"
            )
        
        # Get all quotations for the contractor
        quotations = quotation_manager.get_quotations_by_user(user_id)
        if not quotations:
            raise HTTPException(status_code=404, detail="No quotations found for this contractor")
        
        # Create temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contractor_{user_id}_quotations_{timestamp}.xlsx"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        
        # Create workbook and worksheet
        workbook = xlsxwriter.Workbook(temp_file.name)
        worksheet = workbook.add_worksheet('All Quotations')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        quotation_header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#70AD47',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#D9E2F3',
            'border': 1
        })
        
        data_format = workbook.add_format({
            'border': 1,
            'align': 'left'
        })
        
        currency_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'border': 1,
            'align': 'right'
        })
        
        # Write main header
        worksheet.merge_range('A1:H1', f'ALL QUOTATIONS - CONTRACTOR ID: {user_id}', header_format)
        worksheet.merge_range('A2:H2', f'Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', data_format)
        worksheet.merge_range('A3:H3', f'Total Quotations: {len(quotations)}', data_format)
        
        current_row = 5
        
        # Process each quotation
        for quotation in quotations:
            quotation_id = quotation.get('id')
            
            # Write quotation header
            worksheet.merge_range(f'A{current_row}:H{current_row}', f'QUOTATION #{quotation_id}', quotation_header_format)
            current_row += 1
            
            # Write quotation details
            worksheet.write(current_row, 0, 'Quotation Name:', title_format)
            worksheet.write(current_row, 1, quotation.get('quotation_name', 'N/A'), data_format)
            worksheet.write(current_row, 2, 'Client Name:', title_format)
            worksheet.write(current_row, 3, quotation.get('client_name', 'N/A'), data_format)
            current_row += 1
            
            worksheet.write(current_row, 0, 'Status:', title_format)
            worksheet.write(current_row, 1, quotation.get('status', 'N/A'), data_format)
            worksheet.write(current_row, 2, 'Created Date:', title_format)
            worksheet.write(current_row, 3, quotation.get('created_at', 'N/A'), data_format)
            current_row += 1
            
            worksheet.write(current_row, 0, 'Total Cost:', title_format)
            worksheet.write(current_row, 1, quotation.get('total_cost', 0), currency_format)
            current_row += 2
            
            # Get items for this quotation
            items = item_manager.get_items_by_quotation(quotation_id)
            
            if items:
                # Write items table headers
                headers = ['Item Name', 'SKU/ID', 'Unit', 'Unit of Measure', 'Cost', 'Quantity', 'Total Cost']
                for col, header in enumerate(headers):
                    worksheet.write(current_row, col, header, title_format)
                current_row += 1
                
                # Write items data
                for item in items:
                    worksheet.write(current_row, 0, item.get('item_name', ''), data_format)
                    worksheet.write(current_row, 1, item.get('sku', 'N/A'), data_format)
                    worksheet.write(current_row, 2, item.get('unit', ''), data_format)
                    worksheet.write(current_row, 3, item.get('unit_of_measure', ''), data_format)
                    worksheet.write(current_row, 4, item.get('cost', 0), currency_format)
                    worksheet.write(current_row, 5, item.get('quantity', 0), data_format)
                    worksheet.write(current_row, 6, item.get('total_cost', 0), currency_format)
                    current_row += 1
                
                # Write quotation total
                worksheet.write(current_row, 5, 'QUOTATION TOTAL:', title_format)
                worksheet.write(current_row, 6, quotation.get('total_cost', 0), currency_format)
                current_row += 2
            else:
                worksheet.write(current_row, 0, 'No items found for this quotation', data_format)
                current_row += 2
        
        # Set column widths
        worksheet.set_column('A:A', 25)  # Item Name
        worksheet.set_column('B:B', 15)  # SKU/ID
        worksheet.set_column('C:C', 15)  # Unit
        worksheet.set_column('D:D', 20)  # Unit of Measure
        worksheet.set_column('E:E', 12)  # Cost
        worksheet.set_column('F:F', 12)  # Quantity
        worksheet.set_column('G:G', 15)  # Total Cost
        worksheet.set_column('H:H', 5)   # Extra space
        
        workbook.close()
        
        # Return file for download
        return FileResponse(
            path=temp_file.name,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/contractors/{user_id}/quotations/export/pdf",
    response_class=FileResponse,
    summary="📄 Export All Contractor Quotations to PDF",
    description="Export all quotations for a specific contractor with all items to a PDF file"
)
async def export_contractor_quotations_pdf(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Export all contractor quotations to PDF format"""
    try:
        # Initialize database managers
        db_manager = EnhancedDatabaseManager()
        quotation_manager = QuotationManager(db_manager)
        item_manager = QuotationItemManager(db_manager)
        
        # Check if user is accessing their own data or if they're an admin
        if user_id != current_user['id'] and current_user.get('role') != 'admin':
            raise HTTPException(
                status_code=403, 
                detail="You can only export your own quotations unless you're an admin"
            )
        
        # Get all quotations for the contractor
        quotations = quotation_manager.get_quotations_by_user(user_id)
        if not quotations:
            raise HTTPException(status_code=404, detail="No quotations found for this contractor")
        
        # Create temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contractor_{user_id}_quotations_{timestamp}.pdf"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
        # Create PDF document
        doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        main_title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        quotation_title_style = ParagraphStyle(
            'QuotationTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkgreen
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        normal_style = styles['Normal']
        
        # Add main title
        story.append(Paragraph(f"ALL QUOTATIONS - CONTRACTOR ID: {user_id}", main_title_style))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
        story.append(Paragraph(f"Total Quotations: {len(quotations)}", normal_style))
        story.append(Spacer(1, 30))
        
        # Process each quotation
        for i, quotation in enumerate(quotations):
            quotation_id = quotation.get('id')
            
            # Add quotation title
            story.append(Paragraph(f"QUOTATION #{quotation_id}", quotation_title_style))
            
            # Add quotation details
            story.append(Paragraph("Quotation Details", heading_style))
            
            details_data = [
                ['Quotation Name:', quotation.get('quotation_name', 'N/A')],
                ['Client Name:', quotation.get('client_name', 'N/A')],
                ['Status:', quotation.get('status', 'N/A')],
                ['Created Date:', quotation.get('created_at', 'N/A')],
                ['Total Cost:', f"${quotation.get('total_cost', 0):,.2f}"]
            ]
            
            details_table = Table(details_data, colWidths=[2*inch, 3*inch])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(details_table)
            story.append(Spacer(1, 15))
            
            # Get items for this quotation
            items = item_manager.get_items_by_quotation(quotation_id)
            
            if items:
                # Add items section
                story.append(Paragraph("Item Details", heading_style))
                
                # Prepare items data
                items_data = [['Item Name', 'SKU/ID', 'Unit', 'Cost', 'Quantity', 'Total Cost']]
                
                for item in items:
                    items_data.append([
                        item.get('item_name', ''),
                        item.get('sku', 'N/A'),
                        item.get('unit', ''),
                        f"${item.get('cost', 0):,.2f}",
                        str(item.get('quantity', 0)),
                        f"${item.get('total_cost', 0):,.2f}"
                    ])
                
                # Add total row
                items_data.append(['', '', '', '', 'TOTAL:', f"${quotation.get('total_cost', 0):,.2f}"])
                
                items_table = Table(items_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 1.2*inch])
                items_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(items_table)
            else:
                story.append(Paragraph("No items found for this quotation", normal_style))
            
            # Add spacing between quotations (except for the last one)
            if i < len(quotations) - 1:
                story.append(Spacer(1, 30))
        
        # Build PDF
        doc.build(story)
        
        # Return file for download
        return FileResponse(
            path=temp_file.name,
            filename=filename,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
