import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .llm import LLM
from .prompts import STOCK_ANALYZER_PROMPT, PORTFOLIO_OPTIMIZER_PROMPT

class ReportGenerator:
  """
  Generates a multi-section PDF report with financial
  analysis, charts, and portfolio optimization details.
  """

  def __init__(self, report_name):

    self.llm = LLM()
    self.styles = None
    self.doc = None

    self.initialize_params(report_name)


  def build_final_report(self, metrics_df:pd.DataFrame, sector_list:list):
    """
    Build the final report on financial analysis of various sectors
    and details on portfolio optimization.

    Parameters
    ----------
    metrics_df : pd.DataFrame
        DataFrame containing sector metrics.
        
    sector_list : list of str
        List of sector names to include in the report.

    Returns
    -------
    None
    """

    report = []
    report = self.build_cover_page(report, "Report On Analysis of S&P 500 Stocks")

    # Iterate over each sector to build final report
    for sector_name in sector_list:
      report = self.build_section(sector_name, metrics_df[metrics_df.sector == sector_name], report)
      report.append(PageBreak())

    report = self.build_portfolio_section(report)

    self.doc.build(report)


  def build_section(self, sector_name:str, metrics_df:pd.DataFrame, report:list)->list:
    """
    Build a single section based on sector for the final report.

    Creates a title, introductory paragraph, chart image, and analysis text
    for a given sector, then appends them to the report content list.

    Parameters
    ----------
    sector_name : str
        Name of the sector being analyzed.

    metrics_df : pd.DataFrame
        DataFrame containing metrics for this sector.

    report : list
        Current list of report elements to which this section will be added.

    Returns
    -------
    list
        Updated report content list with the sector's section appended.
    """

    # Title
    report.append(Paragraph(f"Analysis of {sector_name} Sector", self.styles['TitleStyle']))

    # Header paragraph
    head_text =  f"Below is a financial analysis of the investment trends in the {sector_name} Sector"
    report.append(Paragraph(head_text, self.styles['BodyStyle']))

    # Chart Image
    img = Image(f'{sector_name}.png', width=7*inch, height=4.5*inch)
    img.hAlign = 'CENTER'
    report.append(img)

    # Analysis Text
    analysis_text = self.generate_analysis(metrics_df)
    report.append(Paragraph(analysis_text.strip(), self.styles['BodyStyle']))

    return report


  def generate_analysis(self, metrics_df:pd.DataFrame)->str:
    """
    Generate a text-based analysis for a given sector's metrics.

    Parameters
    ----------
    metrics_df : pd.DataFrame
      DataFrame containing sector metrics.

    Returns
    -------
    str
      Generated analysis text for the sector.
    """

    prompt = self.build_prompt(metrics_df)
    analysis = self.llm.get_response(prompt)

    return analysis


  def build_prompt(self, metrics_df:pd.DataFrame)->str:
    """
    Build an LLM prompt string from metrics data.

    Parameters
    ----------
    metrics_df : pd.DataFrame
        DataFrame containing metrics to be analyzed.

    Returns
    -------
    str
        Prompt string ready for the LLM.
    """

    prompt = str(metrics_df.to_xml()) + '\n\n' + STOCK_ANALYZER_PROMPT

    return prompt


  def build_cover_page(self, report:list, text:str)->list:
    """
    Build a cover page for the final report.

    Parameters
    ----------

    report : list
        Current list of report elements to which this section will be added.

    text : str
        Name for the cover page.

    Returns
    -------
    list
        Updated report content list with the cover page appended.
    """
    # --- Cover Page ---
    report.append(Spacer(1, A4[1] / 2.5))  # Push down to center-ish vertically
    report.append(Paragraph(text.strip(), self.styles["HeaderStyle"]))
    report.append(PageBreak())

    return report


  def build_portfolio_section(self, report:list) -> list:
    """
    Build a portfolio section for the final report.

    Describes portfolio optimization technique

    Parameters
    ----------

    report : list
        Current list of report elements to which this section will be added.

    Returns
    -------
    list
        Updated report content list with the portfolio section appended.
    """

    # --- Cover Page ---
    report =self.build_cover_page(report, "PORTFOLIO OPTIMIZATION")

    # Title paragraph
    report.append(Paragraph('TECHNIQUE', self.styles['TitleStyle']))

    text = self.llm.get_response(PORTFOLIO_OPTIMIZER_PROMPT)

    report.append(Paragraph(text.strip(), self.styles['BodyStyle']))


  def initialize_params(self, report_name:str):
    """
    Initialize report document template and custom paragraph styles.

    Parameters
    ----------
    report_name : str
        The filename for the generated report (e.g., 'report.pdf').

    Returns
    -------
    None
    """

    self.doc = SimpleDocTemplate(report_name, pagesize=A4,
                                    rightMargin=40, leftMargin=40,
                                    topMargin=40, bottomMargin=40)
    
    self.styles = getSampleStyleSheet()

    # Custom styles
    self.styles.add(ParagraphStyle(name="HeaderStyle",
                              parent=self.styles['Title'],
                              fontName='Helvetica-Bold',
                              fontSize=28,
                              alignment=TA_CENTER,
                              spaceAfter=20))

    self.styles.add(ParagraphStyle(name="TitleStyle",
                              parent=self.styles['Title'],
                              fontName='Helvetica-Bold',
                              fontSize=20,
                              alignment=TA_CENTER,
                              spaceAfter=20))

    self.styles.add(ParagraphStyle(name="BodyStyle",
                              parent=self.styles['Normal'],
                              fontName='Helvetica',
                              fontSize=12,
                              leading=16,
                              spaceBefore=12,
                              spaceAfter=12))

  