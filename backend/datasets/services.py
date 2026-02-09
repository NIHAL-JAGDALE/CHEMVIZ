"""
Service layer for CSV parsing, summary generation, and PDF report creation.
"""
import io
import pandas as pd
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt


class CSVValidationError(Exception):
    """Custom exception for CSV validation errors."""
    pass


def parse_csv(file) -> pd.DataFrame:
    """
    Parse and validate a CSV file. Accepts any valid CSV file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        pandas DataFrame with parsed data
        
    Raises:
        CSVValidationError: If validation fails
    """
    try:
        # Try reading with different encodings
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
        df = None
        last_error = None
        
        for encoding in encodings_to_try:
            try:
                file.seek(0)  # Reset file pointer for each attempt
                df = pd.read_csv(file, encoding=encoding, on_bad_lines='warn')
                break  # Successfully read the file
            except UnicodeDecodeError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue
        
        if df is None:
            raise CSVValidationError(f"Could not read CSV file with any supported encoding. Last error: {str(last_error)}")
        
        # Check for empty file
        if df.empty:
            raise CSVValidationError("CSV file is empty")
        
        # Check for at least one column
        if len(df.columns) == 0:
            raise CSVValidationError("CSV file has no columns")
        
        # Clean column names - strip whitespace
        df.columns = df.columns.str.strip()
        
        # Auto-detect and convert numeric columns
        for col in df.columns:
            # Try to convert to numeric if the column appears numeric
            if df[col].dtype == 'object':
                try:
                    # First try to clean the data - remove commas from numbers
                    cleaned = df[col].astype(str).str.replace(',', '', regex=False)
                    numeric_col = pd.to_numeric(cleaned, errors='coerce')
                    # Only convert if at least 50% of values are numeric
                    if numeric_col.notna().sum() / len(df) >= 0.5:
                        df[col] = numeric_col
                except Exception:
                    pass
        
        return df
        
    except pd.errors.EmptyDataError:
        raise CSVValidationError("CSV file is empty or malformed")
    except pd.errors.ParserError as e:
        raise CSVValidationError(f"CSV parsing error: {str(e)}")
    except CSVValidationError:
        raise  # Re-raise our own errors
    except Exception as e:
        raise CSVValidationError(f"Error processing CSV file: {str(e)}")


def get_numeric_columns(df: pd.DataFrame) -> list:
    """
    Get list of numeric columns from a DataFrame.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        List of numeric column names
    """
    return df.select_dtypes(include=['number']).columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> list:
    """
    Get list of categorical columns from a DataFrame.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        List of categorical column names
    """
    return df.select_dtypes(include=['object', 'category']).columns.tolist()


def generate_summary(df: pd.DataFrame) -> dict:
    """
    Generate summary statistics from a DataFrame.
    Dynamically detects numeric and categorical columns.
    
    Args:
        df: pandas DataFrame with data
        
    Returns:
        Dictionary containing summary statistics
    """
    # Total count
    total_count = len(df)
    
    # Get numeric columns dynamically
    numeric_columns = get_numeric_columns(df)
    
    # Calculate averages for all numeric columns
    averages = {}
    for col in numeric_columns:
        avg = df[col].mean()
        averages[col.lower().replace(' ', '_')] = round(avg, 2) if pd.notna(avg) else 0
    
    # Get categorical columns dynamically
    categorical_columns = get_categorical_columns(df)
    
    # Type distribution - use the first categorical column or first column as default
    type_distribution = {}
    distribution_column = None
    
    if categorical_columns:
        distribution_column = categorical_columns[0]
    elif len(df.columns) > 0:
        # Use first column if no categorical columns found
        distribution_column = df.columns[0]
    
    if distribution_column:
        type_counts = df[distribution_column].value_counts().head(10).to_dict()
        type_distribution = {str(k): int(v) for k, v in type_counts.items()}
    
    # Column names
    column_names = df.columns.tolist()
    
    return {
        'total_count': total_count,
        'averages': averages,
        'type_distribution': type_distribution,
        'column_names': column_names,
        'numeric_columns': numeric_columns,
        'categorical_columns': categorical_columns,
        'distribution_column': distribution_column,
    }


def enforce_history_limit(user, max_datasets=None):
    """
    Ensure user has at most max_datasets stored. Delete oldest if exceeded.
    
    Args:
        user: User object
        max_datasets: Maximum number of datasets (defaults to settings value)
    """
    from .models import Dataset
    
    if max_datasets is None:
        max_datasets = getattr(settings, 'MAX_DATASETS_PER_USER', 5)
    
    user_datasets = Dataset.objects.filter(user=user).order_by('-uploaded_at')
    
    if user_datasets.count() > max_datasets:
        # Get datasets to delete (oldest ones beyond the limit)
        datasets_to_delete = user_datasets[max_datasets:]
        for dataset in datasets_to_delete:
            # Delete the file from storage
            if dataset.file:
                dataset.file.delete(save=False)
            dataset.delete()


def generate_chart_image(type_distribution: dict) -> bytes:
    """
    Generate a bar chart image for type distribution.
    
    Args:
        type_distribution: Dictionary of equipment type counts
        
    Returns:
        PNG image bytes
    """
    # Handle empty or invalid data
    if not type_distribution or len(type_distribution) == 0:
        # Return a placeholder chart
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, 'No distribution data available', ha='center', va='center', fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        plt.close(fig)
        return buffer.getvalue()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Truncate long labels and sanitize
    types = []
    for t in type_distribution.keys():
        label = str(t)[:20] + '...' if len(str(t)) > 20 else str(t)
        types.append(label)
    counts = list(type_distribution.values())
    
    # Limit to top 10 for readability
    if len(types) > 10:
        sorted_items = sorted(zip(types, counts), key=lambda x: x[1], reverse=True)[:10]
        types, counts = zip(*sorted_items)
        types, counts = list(types), list(counts)
    
    colors_list = ['#667eea', '#764ba2', '#11998e', '#38ef7d', '#f5576c', '#f093fb', '#e67e22', '#1abc9c', '#3498db', '#9b59b6']
    bar_colors = [colors_list[i % len(colors_list)] for i in range(len(types))]
    
    bars = ax.bar(types, counts, color=bar_colors, edgecolor='white', linewidth=1.5)
    
    ax.set_xlabel('Category', fontsize=11, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Count', fontsize=11, fontweight='bold', color='#2c3e50')
    ax.set_title('Distribution by Category', fontsize=14, fontweight='bold', pad=15, color='#2c3e50')
    
    # Add value labels on bars
    max_count = max(counts) if counts else 1
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_count * 0.02,
                str(count), ha='center', va='bottom', fontsize=9, fontweight='bold', color='#34495e')
    
    ax.set_ylim(0, max_count * 1.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    
    # Save to bytes
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    plt.close(fig)
    
    return buffer.getvalue()


def generate_averages_chart(averages: dict) -> bytes:
    """
    Generate a bar chart for average values.
    
    Args:
        averages: Dictionary of average values per numeric column
        
    Returns:
        PNG image bytes
    """
    # Handle empty or invalid data
    if not averages or len(averages) == 0:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, 'No numeric data available', ha='center', va='center', fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        plt.close(fig)
        return buffer.getvalue()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Truncate long labels and limit to top 10
    params = []
    for k in averages.keys():
        label = k.replace('_', ' ').title()
        label = label[:18] + '...' if len(label) > 18 else label
        params.append(label)
    values = list(averages.values())
    
    # Limit to top 10 for readability
    if len(params) > 10:
        sorted_items = sorted(zip(params, values), key=lambda x: abs(x[1]), reverse=True)[:10]
        params, values = zip(*sorted_items)
        params, values = list(params), list(values)
    
    # Color gradient from blue to green
    colors_list = ['#667eea', '#764ba2', '#11998e', '#38ef7d', '#f5576c', '#f093fb', '#e67e22', '#1abc9c', '#3498db', '#9b59b6']
    bar_colors = [colors_list[i % len(colors_list)] for i in range(len(params))]
    
    bars = ax.bar(params, values, color=bar_colors, edgecolor='white', linewidth=1.5)
    
    ax.set_xlabel('Parameter', fontsize=11, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Average Value', fontsize=11, fontweight='bold', color='#2c3e50')
    ax.set_title('Average Parameter Values', fontsize=14, fontweight='bold', pad=15, color='#2c3e50')
    
    # Add value labels on bars
    max_val = max(abs(v) for v in values) if values else 1
    for bar, val in zip(bars, values):
        offset = max_val * 0.02 if val >= 0 else -max_val * 0.08
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + offset,
                f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#34495e')
    
    ax.set_ylim(0, max_val * 1.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    
    # Save to bytes
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    plt.close(fig)
    
    return buffer.getvalue()


def generate_pdf_report(dataset) -> bytes:
    """
    Generate a visually appealing PDF report for a dataset.
    
    Args:
        dataset: Dataset model instance
        
    Returns:
        PDF file bytes
    """
    from reportlab.platypus import PageBreak, HRFlowable
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT
    from datetime import datetime
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        alignment=TA_CENTER,
        spaceAfter=8,
        textColor=colors.HexColor('#667eea'),
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=30,
        textColor=colors.HexColor('#7f8c8d')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=20,
        spaceAfter=15,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#34495e'),
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        textColor=colors.HexColor('#2c3e50')
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=TA_CENTER
    )
    
    story = []
    
    # ===== HEADER SECTION =====
    # Add a decorative line
    story.append(HRFlowable(width="100%", thickness=3, color=colors.HexColor('#667eea'), spaceAfter=20))
    
    # Title
    story.append(Paragraph("📊 Data Analysis Report", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    
    # File Information Box
    file_info_data = [
        ['Dataset Information', ''],
        ['📁 Filename:', dataset.filename],
        ['📅 Uploaded:', dataset.uploaded_at.strftime('%B %d, %Y at %I:%M %p')],
        ['📋 Total Records:', f"{dataset.summary.total_count:,}"],
    ]
    
    file_info_table = Table(file_info_data, colWidths=[2*inch, 4*inch])
    file_info_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('TOPPADDING', (0, 0), (-1, 0), 15),
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        # Rounded border effect
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#e0e0e0')),
    ]))
    story.append(file_info_table)
    story.append(Spacer(1, 25))
    
    summary = dataset.summary
    
    # ===== NUMERIC STATISTICS SECTION =====
    if summary.averages and len(summary.averages) > 0:
        story.append(Paragraph("📈 Numeric Statistics", heading_style))
        story.append(Paragraph("Average values for numeric columns in your dataset:", normal_style))
        
        # Create averages table with alternating rows
        avg_data = [['Parameter', 'Average Value']]
        for idx, (param, value) in enumerate(list(summary.averages.items())[:15]):  # Limit to 15 rows
            formatted_param = param.replace('_', ' ').title()
            if len(formatted_param) > 30:
                formatted_param = formatted_param[:27] + '...'
            avg_data.append([formatted_param, f"{value:,.2f}"])
        
        avg_table = Table(avg_data, colWidths=[3*inch, 2.5*inch])
        
        # Dynamic row styling with alternating colors
        table_style = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            # Data cells
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#ddd')),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#eee')),
        ]
        
        # Add alternating row colors
        for i in range(1, len(avg_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa')))
            else:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        
        avg_table.setStyle(TableStyle(table_style))
        story.append(avg_table)
        story.append(Spacer(1, 25))
    
    # ===== CATEGORY DISTRIBUTION SECTION =====
    if summary.type_distribution and len(summary.type_distribution) > 0:
        story.append(Paragraph("📊 Category Distribution", heading_style))
        story.append(Paragraph("Top categories by frequency:", normal_style))
        
        # Sort by count and limit
        sorted_dist = sorted(summary.type_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
        
        type_data = [['Category', 'Count', 'Percentage']]
        total = sum(v for _, v in sorted_dist)
        for eq_type, count in sorted_dist:
            formatted_type = str(eq_type)[:25] + '...' if len(str(eq_type)) > 25 else str(eq_type)
            percentage = (count / total * 100) if total > 0 else 0
            type_data.append([formatted_type, f"{count:,}", f"{percentage:.1f}%"])
        
        type_table = Table(type_data, colWidths=[3*inch, 1.25*inch, 1.25*inch])
        
        type_style = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            # Data
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#ddd')),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#eee')),
        ]
        
        for i in range(1, len(type_data)):
            if i % 2 == 0:
                type_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa')))
            else:
                type_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        
        type_table.setStyle(TableStyle(type_style))
        story.append(type_table)
        story.append(Spacer(1, 30))
    
    # ===== VISUALIZATIONS SECTION =====
    story.append(PageBreak())
    story.append(Paragraph("📉 Data Visualizations", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0'), spaceAfter=20))
    
    # Category Distribution Chart
    if summary.type_distribution and len(summary.type_distribution) > 0:
        story.append(Paragraph("Category Distribution Chart", subheading_style))
        try:
            chart_bytes = generate_chart_image(summary.type_distribution)
            chart_img = Image(io.BytesIO(chart_bytes), width=6*inch, height=4*inch)
            story.append(chart_img)
        except Exception as e:
            story.append(Paragraph(f"<i>Chart could not be generated: {str(e)}</i>", info_style))
        story.append(Spacer(1, 30))
    
    # Averages Chart
    if summary.averages and len(summary.averages) > 0:
        story.append(Paragraph("Numeric Averages Chart", subheading_style))
        try:
            avg_chart_bytes = generate_averages_chart(summary.averages)
            avg_chart_img = Image(io.BytesIO(avg_chart_bytes), width=6*inch, height=4*inch)
            story.append(avg_chart_img)
        except Exception as e:
            story.append(Paragraph(f"<i>Chart could not be generated: {str(e)}</i>", info_style))
    
    # ===== FOOTER =====
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0'), spaceBefore=20))
    story.append(Paragraph("Generated by Data Visualizer • All data is confidential", info_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
