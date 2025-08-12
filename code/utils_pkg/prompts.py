
STOCK_ANALYZER_PROMPT = """

I have an XML file with financial data for different industries including P/E ratio, dividend yield, 
market cap, and 1-year returns. Please create a consolidated financial analysis report that strictly 
focuses only on industries that represent either top investment opportunities or very poor investment 
prospects based on the provided metrics. 
Highlight important positive or negative trends for these selected industries only, explaining what these 
trends mean for their financial health and market performance. Do not include industries that fall into 
moderate or average performance categories. Do not add any additional commentary, explanations, or information 
beyond what is explicitly requested. Only provide the requested analysis.

Output should be in the below format. Try to be as concise as possible without loss of information.:

<b> Top Investment Opportunities: </b> <br/><br/>  

<b> { industry_name} </b>  : {industry analysis summary} <br/><br/> 

<b> Bad Investment Opportunities: <\b> <br/><br/> 

<b> { industry_name} </b> : {industry analysis summary} <br/><br/> 

"""

PORTFOLIO_OPTIMIZER_PROMPT = """

The original method is:

* First, group stocks into sectors.
* Assign each sector a weight that is inversely proportional to its volatility (sector beta).
* Within each sector, give each stock a weight proportional to its share of profit margin in that sector.
* Multiply the sector weight by the stock’s weight to get the final stock weight.
* Use these final weights for weighted fund allocation.

Rewrite my description of a portfolio optimization method into no more than 5 logical, easy-to-read, non-technical steps.
Do not provide any other output other than what is strictly asked.

Each step should follow this format:

{serial_number}. <b>{step header}</b><br/>
{1-2 line step description} <br/><br/>

"""