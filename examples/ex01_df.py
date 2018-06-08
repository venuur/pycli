from pycli import run_application, add_cli

import pandas as pd

@add_cli(output='plot')
def plot_columns(
        #df:pd.DataFrame,
        index_col:str, value_col:str) -> type(None):
    '''Plots a value column vs. and index column for a given data frame.

    Args:
        df (pd.DataFrame): Data frame to use as source for plot.
        index_col (str): Name of column to use as index.
        value_col (str): Name of column to use for values.

    Returns:
        None: Nothing
    '''

    # TODO: Until I add a load dataframe feature to add_cli.
    df = pd.DataFrame({index_col: [1, 4, 9], value_col: [6, 2, 10]})
    df.set_index(index_col)[value_col].plot()


if __name__ == '__main__':
    run_application()
