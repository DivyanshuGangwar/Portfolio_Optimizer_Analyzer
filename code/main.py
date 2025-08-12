import utils_pkg
import pandas as pd


class MainTool:

  def __init__(self):

    self.stock_obj = utils_pkg.StockAnalyzer()
    self.report_obj = utils_pkg.ReportGenerator("final_report.pdf")

  def main(
    self, 
    stock_data_df:pd.DataFrame, 
    portfolio_amount:int, 
    portfolio_sector_size:int =10
  ):
    """
    Executes the end-to-end stock analysis and portfolio optimization workflow
    with report genration.

    Parameters
    ----------
    stock_data_df : pd.DataFrame
      DataFrame containing stock-level financial data for multiple sectors.

    portfolio_amount : int
      Total capital to allocate across the portfolio.

    portfolio_sector_size : int, default=10
      Maximum number of stocks to select from each sector.

    Returns
    -------
    pd.DataFrame
        Optimized portfolio with recommended number of shares per stock.
    """

    stock_data_df = self.stock_obj.get_sp_500_info()

    print('extracting global metrics at sector level')
    sectors_list = stock_data_df.sector.unique()
    metrics_df_global = self.stock_obj.extract_metrics(stock_data_df, None, 'sector')

    print('extracting sector level metrics at industry level')
    total_sector_metrics =[]

    for sector in sectors_list:

      print(f'extracting sector level metrics for {sector} sector')
      sector_metrics = self.stock_obj.extract_metrics(stock_data_df, sector, 'industry')
      total_sector_metrics.append(sector_metrics)
    
    self.test = total_sector_metrics = pd.concat(total_sector_metrics)
    
    print('generating optimized portfolio')
    portfolio =self.stock_obj.portfolio_optimization(metrics_df_global, stock_data_df, \
                                            portfolio_amount, portfolio_sector_size)

    print('generating final report')
    self.report_obj.build_final_report(total_sector_metrics, sectors_list)

    return portfolio

