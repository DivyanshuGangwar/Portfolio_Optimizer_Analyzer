import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns

class StockAnalyzer:
  """
  Provides tools for analyzing stock market data, computing sector metrics,
  and optimizing portfolio allocations with visual insights.
  """

  def __init__(self):
    pass


  def portfolio_optimization(
    self,
    metrics_df_global: pd.DataFrame, 
    stock_port_df: pd.DataFrame,
    total_amount: float,
    limit: int
  ) -> pd.DataFrame:
    """
    Optimize portfolio allocation based on sector betas and stock rankings.

    Parameters
    ----------
    metrics_df_global : pd.DataFrame
        DataFrame containing sector-level performance metrics.
        
    stock_port_df : pd.DataFrame
        DataFrame containing stock-level data.
        
    total_amount : float
        The total amount of capital to be allocated across the portfolio.

    limit : int
        The maximum number of stocks to select per sector.

    Returns
    -------
    pd.DataFrame
        Portfolio allocation DataFrame conatining number of shares to purchase per
        stock
    """

    # Calculate sector weight based on beta for each sector (lower beta → higher weight)
    inverse_beta = 1/metrics_df_global['avg_beta']
    metrics_df_global['sector_wieghts'] = inverse_beta/inverse_beta.sum()

    # For each sector, select top <limit> stocks based on profit margin
    stock_port_df = stock_port_df.groupby('sector', group_keys=False) \
                    .apply(lambda group: self.extract_stock_wieght(group, limit))

    # Recommend shares to buy per stock based on portfolio optimization criteria
    merged_df = stock_port_df.join(metrics_df_global[['sector','sector_wieghts']] \
                .set_index('sector'), on='sector', how='inner') 
    merged_df['final_wieght'] = merged_df['stock_wieght']*merged_df['sector_wieghts']
    portfolio_df = self.allocate_funds(merged_df, total_amount)

    return portfolio_df.sort_values('shares', ascending = False)


  def allocate_funds(
    self,
    df_orig:pd.DataFrame, 
    total_amount:float, 
    price_col:str='regularMarketPrice', 
    weight_col:str='final_wieght'
  ) -> pd.DataFrame:
    """
    Allocate portfolio funds into discrete shares of stocks based on 
    stock importance weights.

    Parameters
    ----------
    df_orig : pd.DataFrame
        DataFrame containing stock information and calculated weights.

    total_amount : float
        Total capital to be allocated across all stocks.

    price_col : str
        Column name for stock share price.

    weight_col : str
        Column name for final stock importance weights.

    Returns
    -------
    pd.DataFrame
        DataFrame containing final recommendation for fund allocation 
        accross portfolio.
    """
    # Sort by weight (highest first) for allocation priority and get cummulative price
    df = df_orig.sort_values('final_wieght', ascending = False).copy()
    df['cumulative_price'] = df['regularMarketPrice'].cumsum()

    # Initial share allocation based on proportional weights
    # Floor division ensures whole shares only
    df_orig['shares'] = df['shares'] = np.floor((total_amount * df[weight_col]) / df[price_col])

    # "residue is the unspent cash remaining after rounding share purchases down to        
    #  whole numbers.
    residue = total_amount - (df['shares'] * df[price_col]).sum()

    # logic to use residue amount to buy additional shares
    # residue amount is distributed as much as possible accross higher priority
    # shares as much as possible in each pass.
    while True:

      print(f'residue is {residue}')
      
      df_res = df[df[price_col] < residue].copy()
      if df_res.empty:
        break
      df_res['c_price'] = df_res[price_col].cumsum()
      df_res = df_res[df_res['c_price'] < residue]
      df_res['shares'] +=1
      df_orig.loc[df_orig.index.isin(df_res.index), 'shares'] +=1
      residue -= df_res[price_col].sum()

    return df_orig[['industry','sector','website', 'shares', price_col]].reset_index(names='ticker_symbol')


  def extract_stock_wieght(
    self, 
    sector_group:pd.DataFrame, 
    limit:int
  )->pd.DataFrame:
    """
    Select top <limit> stocks in a sector based on profit margins
    and derive normalised stock weights from those margins

    Parameters
    ----------
    sector_group : pd.DataFrame
        DataFrame containing stock data for a single sector.
    limit : int
        Maximum number of top stocks to select based on profit margins.

    Returns
    -------
    pd.DataFrame
        DataFrame containing only the top `limit` profitable stocks in the sector,
        with a new column 'stock_weight' representing each stock's proportion
        of total profit margins within the sector.
    """

    sector_group = sector_group .nlargest(limit, 'profitMargins')
    sector_group = sector_group[sector_group['profitMargins']>0]
    sector_group['stock_wieght'] = sector_group['profitMargins']/sector_group['profitMargins'].sum()
    return sector_group 


  def plot_thematic_sector_metrics(
    self,
    summary_df:pd.DataFrame,
    sector_name:str,
    sector_col:str='thematicSector',
    limit:int = 10,
    ascending:bool = False
  ):
    """
    Plots key metrics (Market Cap, P/E, Dividend Yield, 1-Year Return) by <sector_col>.

    Parameters
    ----------
    summary_df : pd.DataFrame
      DataFrame with aggregated metrics by <sector_col> for sector <sector_name>.

    sector_name : str
      Name of sector for which the visualisation needs to be done.

    sector_col: str
      column by which sub-grouping within the sector gets done.

    limit : int
      Maximum number of <sector_col> values to display.

    ascending : bool
      sort display by magnitude of metric

    """
    
    market_cap_col='total_market_cap'
    pe_col='avg_pe'
    dividend_yield_col='avg_dividend_yield'
    return_col='avg_1y_return'
    figsize=(14, 10)

    if summary_df.shape[0] < limit:
        limit = summary_df.shape[0]

    sns.set(style="whitegrid")

    palettes = {
        'market_cap': "viridis",
        'pe': "magma",
        'dividend': "coolwarm",
        'return': "crest"
    }

    fig, axs = plt.subplots(2, 2, figsize=figsize)

    # Market Cap (log scale)
    sns.barplot(
        x=market_cap_col, y=sector_col,
        data=summary_df.sort_values(market_cap_col, ascending=ascending)[0:limit],
        ax=axs[0, 0], palette=palettes['market_cap']
    )
    axs[0, 0].set_title('Total Market Capitalization by Thematic Sector')
    axs[0, 0].set_xscale('log')
    axs[0, 0].set_xlabel('Total Market Cap (log scale)')
    axs[0, 0].set_ylabel(sector_col)

    # Average P/E Ratio
    sns.barplot(
        x=pe_col, y=sector_col,
        data=summary_df.sort_values(pe_col, ascending=ascending)[0:limit],
        ax=axs[0, 1], palette=palettes['pe']
    )
    axs[0, 1].set_title('Average P/E Ratio by Thematic Sector')
    axs[0, 1].set_xlabel('Average P/E Ratio')
    axs[0, 1].set_ylabel(sector_col)

    # Average Dividend Yield
    sns.barplot(
        x=dividend_yield_col, y=sector_col,
        data=summary_df.sort_values(dividend_yield_col, ascending=ascending)[0:limit],
        ax=axs[1, 0], palette=palettes['dividend']
    )
    axs[1, 0].set_title('Average Dividend Yield by Thematic Sector')
    axs[1, 0].set_xlabel('Average Dividend Yield')
    axs[1, 0].set_ylabel(sector_col)

    # Average 1-Year Price Return
    sns.barplot(
        x=return_col, y=sector_col,
        data=summary_df.sort_values(return_col, ascending=ascending)[0:limit],
        ax=axs[1, 1], palette=palettes['return']
    )
    axs[1, 1].set_title('Average 1-Year Price Return by Thematic Sector')
    axs[1, 1].set_xlabel('Average 1-Year Price Return')
    axs[1, 1].set_ylabel(sector_col)

    plt.tight_layout()
    save_path = f'{sector_name}.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved")
    plt.close()


  def extract_metrics(
    self, 
    data_df:pd.DataFrame,
    sector_name:str,
    group_col:str) -> pd.DataFrame:
    """
    Compute aggregated financial metrics for a given sector or across sectors.

    Parameters
    ----------
    data_df : pd.DataFrame
      DataFrame containing stock-level financial data.
        
    sector_name : str or None
        If provided, metrics will be calculated only for this sector.
        If None, metrics are calculated for all sectors/groups.

    group_col : str
        Column name to group by (e.g., 'sector', 'industry').

    Returns
    -------
    pd.DataFrame
        Aggregated metrics by `group_col`, including:
    """

    if sector_name is not None:
      data_df = data_df[data_df.sector == sector_name] 

    summary_df = data_df.groupby(group_col).agg(
              total_market_cap=('marketCap', 'sum'),
              avg_pe=('trailingPE', 'mean'),
              avg_dividend_yield=('dividendYield', 'mean'),
              avg_1y_return=('52WeekChange', 'mean'),
              avg_beta = ('beta', 'mean')
          ).reset_index()

    if sector_name is not None:
      summary_df['sector'] = sector_name
      self.plot_thematic_sector_metrics(summary_df, sector_name, group_col)

    return summary_df


  def get_sp_500_info(self) -> pd.DataFrame:
    """
    Retrieve detailed stock information for all S&P 500 companies.

    Returns
    -------
    pd.DataFrame
        DataFrame containing stock information for all S&P 500 companies,
        with one row per ticker and columns for each available info field.
        Rows with missing sector information are excluded.
    """

    tickers = self.get_sp_500_tickers()

    tickers_obj = yf.Tickers(" ".join(tickers))

    info_dict = {
        sym: tickers_obj.tickers[sym].info
        for sym in tickers
    }

    # Convert to DataFrame: rows = tickers, columns = info keys
    stock_info_df = pd.DataFrame.from_dict(info_dict, orient="index")
    stock_info_df = stock_info_df[pd.notna(stock_info_df.sector)]

    return stock_info_df


  def get_sp_500_tickers(self) -> list:
    """
    Retrieve the list of S&P 500 ticker symbols from Wikipedia.

    Scrapes the 'List of S&P 500 companies' Wikipedia page and
    extracts the symbols from the constituents table.

    Returns
    -------
    list of str
        A list of S&P 500 ticker symbols.
    """

    df = pd.read_html(
      "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
      attrs={'id': 'constituents'}
    )[0]
    tickers = df["Symbol"].tolist()

    return tickers
