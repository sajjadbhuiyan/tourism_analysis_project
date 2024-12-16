# all_analysis/nuts1_foreign_domestic.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly
import numpy as np

class ForeignDomesticAnalyzer:
    def __init__(self):
        self.domestic_df = None
        self.foreign_df = None
        self.load_data()

    def load_data(self):
        """Load domestic and foreign NUTS1 data"""
        try:
            self.domestic_df = pd.read_excel('data/nuts_1_2023_domestic.xlsx')
            self.foreign_df = pd.read_excel('data/nuts_1_2023_foreigner.xlsx')
            self.clean_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def clean_data(self):
        """Clean the dataframes by removing ':' values and converting to numeric"""
        def clean_df(df):
            cleaned = df.copy()
            cleaned = cleaned.replace(':', np.nan)
            
            numeric_cols = cleaned.columns[1:] if isinstance(cleaned.columns[0], str) else cleaned.columns
            for col in numeric_cols:
                cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce')
            
            cleaned = cleaned.dropna(how='all')
            return cleaned

        self.domestic_df = clean_df(self.domestic_df)
        self.foreign_df = clean_df(self.foreign_df)

    def analyze_data(self):
        """Analyze both domestic and foreign data"""
        def get_analysis(df, name):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            return {
                'total': float(df[numeric_cols].sum().sum()),
                'average_monthly': float(df[numeric_cols].mean().mean()),
                'max_month': float(df[numeric_cols].max().max()),
                'min_month': float(df[numeric_cols].min().min()),
                'regional_totals': df[numeric_cols].sum().to_dict(),
                'monthly_totals': df[numeric_cols].sum(axis=0).to_dict(),
                'name': name
            }

        domestic_analysis = get_analysis(self.domestic_df, 'Domestic')
        foreign_analysis = get_analysis(self.foreign_df, 'Foreign')

        # Calculate percentage comparisons
        total_visitors = domestic_analysis['total'] + foreign_analysis['total']
        analysis = {
            'domestic': domestic_analysis,
            'foreign': foreign_analysis,
            'comparisons': {
                'domestic_percentage': (domestic_analysis['total'] / total_visitors) * 100,
                'foreign_percentage': (foreign_analysis['total'] / total_visitors) * 100,
                'total_visitors': total_visitors
            }
        }
        return analysis

    def create_monthly_comparison_plot(self):
        """Create monthly comparison visualization"""
        fig = go.Figure()
        
        # Monthly trends for domestic
        domestic_monthly = self.domestic_df.select_dtypes(include=[np.number]).mean()
        fig.add_trace(go.Scatter(
            x=list(domestic_monthly.index),
            y=domestic_monthly.values,
            name='Domestic',
            mode='lines+markers'
        ))
        
        # Monthly trends for foreign
        foreign_monthly = self.foreign_df.select_dtypes(include=[np.number]).mean()
        fig.add_trace(go.Scatter(
            x=list(foreign_monthly.index),
            y=foreign_monthly.values,
            name='Foreign',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title='Monthly Domestic vs Foreign Visitors',
            xaxis_title='Month',
            yaxis_title='Average Visitors',
            template='plotly_white',
            showlegend=True
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def create_regional_distribution_plot(self):
        """Create regional distribution visualization"""
        fig = go.Figure()
        
        # Regional totals for domestic
        domestic_regional = self.domestic_df.select_dtypes(include=[np.number]).sum()
        fig.add_trace(go.Bar(
            name='Domestic',
            x=domestic_regional.index,
            y=domestic_regional.values
        ))
        
        # Regional totals for foreign
        foreign_regional = self.foreign_df.select_dtypes(include=[np.number]).sum()
        fig.add_trace(go.Bar(
            name='Foreign',
            x=foreign_regional.index,
            y=foreign_regional.values
        ))
        
        fig.update_layout(
            title='Regional Distribution of Domestic vs Foreign Visitors',
            xaxis_title='Region',
            yaxis_title='Total Visitors',
            barmode='group',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def create_pie_chart(self):
        """Create pie chart for domestic vs foreign distribution"""
        analysis = self.analyze_data()
        
        fig = go.Figure(data=[go.Pie(
            labels=['Domestic', 'Foreign'],
            values=[analysis['domestic']['total'], analysis['foreign']['total']],
            hole=.3
        )])
        
        fig.update_layout(
            title='Distribution of Domestic vs Foreign Visitors',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def get_full_analysis(self):
        """Get complete analysis including visualizations"""
        analysis = self.analyze_data()
        
        plot_data = {
            'monthly_comparison': self.create_monthly_comparison_plot(),
            'regional_distribution': self.create_regional_distribution_plot(),
            'visitor_distribution': self.create_pie_chart()
        }
        
        return analysis, plot_data