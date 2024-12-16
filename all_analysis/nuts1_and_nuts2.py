# all_analysis/nuts1_and_nuts2.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly
import numpy as np

class DataAnalyzer:
    def __init__(self):
        self.nuts1_df = None
        self.nuts2_df = None
        self.load_data()

    def load_data(self):
        """Load NUTS1 and NUTS2 data from Excel files"""
        try:
            self.nuts1_df = pd.read_excel('data/nuts_1_2023.xlsx')
            self.nuts2_df = pd.read_excel('data/nuts_2_2023.xlsx')
            self.clean_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def clean_data(self):
        """Clean the dataframes by removing ':' values and converting to numeric"""
        def clean_df(df):
            # Make a copy to avoid modifying the original
            cleaned = df.copy()
            
            # Replace ':' with NaN
            cleaned = cleaned.replace(':', np.nan)
            
            # Convert all columns except first (if it's region names) to numeric
            numeric_cols = cleaned.columns[1:] if isinstance(cleaned.columns[0], str) else cleaned.columns
            for col in numeric_cols:
                cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce')
            
            # Drop rows with all NaN values
            cleaned = cleaned.dropna(how='all')
            
            return cleaned

        self.nuts1_df = clean_df(self.nuts1_df)
        self.nuts2_df = clean_df(self.nuts2_df)

    def analyze_nuts1(self):
        """Analyze NUTS1 data"""
        # Calculate only valid numeric values
        numeric_cols = self.nuts1_df.select_dtypes(include=[np.number]).columns
        
        analysis = {
            'total_population': float(self.nuts1_df[numeric_cols].sum().sum()), 
            'average_monthly': float(self.nuts1_df[numeric_cols].mean().mean()),
            'max_month': float(self.nuts1_df[numeric_cols].max().max()),
            'min_month': float(self.nuts1_df[numeric_cols].min().min()),
            'regional_averages': self.nuts1_df[numeric_cols].mean().to_dict(),
            'monthly_totals': self.nuts1_df[numeric_cols].sum().to_dict()
        }
        return analysis

    def analyze_nuts2(self):
        """Analyze NUTS2 data"""
        numeric_cols = self.nuts2_df.select_dtypes(include=[np.number]).columns
        
        analysis = {
            'total_population': float(self.nuts2_df[numeric_cols].sum().sum()),
            'average_monthly': float(self.nuts2_df[numeric_cols].mean().mean()),
            'max_month': float(self.nuts2_df[numeric_cols].max().max()),
            'min_month': float(self.nuts2_df[numeric_cols].min().min()),
            'regional_averages': self.nuts2_df[numeric_cols].mean().to_dict(),
            'monthly_totals': self.nuts2_df[numeric_cols].sum().to_dict()
        }
        return analysis

    def create_monthly_trend_plot(self):
        """Create monthly trend visualization"""
        fig = go.Figure()
        
        # NUTS1 monthly trend
        nuts1_monthly = self.nuts1_df.select_dtypes(include=[np.number]).mean()
        fig.add_trace(go.Scatter(
            x=list(nuts1_monthly.index),
            y=nuts1_monthly.values,
            name='NUTS1',
            mode='lines+markers'
        ))
        
        # NUTS2 monthly trend
        nuts2_monthly = self.nuts2_df.select_dtypes(include=[np.number]).mean()
        fig.add_trace(go.Scatter(
            x=list(nuts2_monthly.index),
            y=nuts2_monthly.values,
            name='NUTS2',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title='Monthly Accommodation Trends',
            xaxis_title='Month',
            yaxis_title='Average Population',
            template='plotly_white',
            showlegend=True
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def create_regional_comparison_plot(self):
        """Create regional comparison visualization"""
        fig = go.Figure()
        
        # NUTS1 regional data
        nuts1_regional = self.nuts1_df.select_dtypes(include=[np.number]).sum()
        fig.add_trace(go.Bar(
            name='NUTS1',
            x=nuts1_regional.index,
            y=nuts1_regional.values
        ))
        
        # NUTS2 regional data
        nuts2_regional = self.nuts2_df.select_dtypes(include=[np.number]).sum()
        fig.add_trace(go.Bar(
            name='NUTS2',
            x=nuts2_regional.index,
            y=nuts2_regional.values
        ))
        
        fig.update_layout(
            title='Regional Comparison',
            xaxis_title='Region',
            yaxis_title='Total Population',
            barmode='group',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def get_full_analysis(self):
        """Get complete analysis including visualizations"""
        nuts1_analysis = self.analyze_nuts1()
        nuts2_analysis = self.analyze_nuts2()
        
        plot_data = {
            'monthly_trend': self.create_monthly_trend_plot(),
            'regional_comparison': self.create_regional_comparison_plot()
        }
        
        return nuts1_analysis, nuts2_analysis, plot_data