# all_analysis/nuts2_foreign_domestic.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly
import numpy as np

class NUTS2ForeignDomesticAnalyzer:
    def __init__(self):
        self.domestic_df = None
        self.foreign_df = None
        self.load_data()

    def load_data(self):
        """Load domestic and foreign NUTS2 data"""
        try:
            self.domestic_df = pd.read_excel('data/nuts_2_2023_domestic.xlsx')
            self.foreign_df = pd.read_excel('data/nuts_2_2023_foreigner.xlsx')
            self.clean_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def clean_data(self):
        """Clean the dataframes by removing ':' values and converting to numeric"""
        def clean_df(df):
            cleaned = df.copy()
            
            # Keep first column (Region) as is
            region_col = cleaned.iloc[:, 0]
            
            # Convert other columns to numeric
            numeric_data = cleaned.iloc[:, 1:].replace(':', np.nan)
            for col in numeric_data.columns:
                numeric_data[col] = pd.to_numeric(numeric_data[col], errors='coerce')
            
            # Combine back
            cleaned = pd.concat([region_col, numeric_data], axis=1)
            cleaned = cleaned.dropna(how='all', subset=cleaned.columns[1:])
            return cleaned

        self.domestic_df = clean_df(self.domestic_df)
        self.foreign_df = clean_df(self.foreign_df)

    def analyze_data(self):
        """Analyze both domestic and foreign data"""
        def get_analysis(df, name):
            # Get numeric columns (excluding Region column)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            # Calculate monthly averages
            monthly_data = df[numeric_cols].mean()
            peak_month = monthly_data.idxmax()
            low_month = monthly_data.idxmin()
            
            # Calculate regional totals
            regional_data = df.groupby(df.columns[0])[numeric_cols].sum()
            top_regions = regional_data.sum(axis=1).sort_values(ascending=False).head(5)
            
            return {
                'total': float(df[numeric_cols].sum().sum()),
                'average_monthly': float(monthly_data.mean()),
                'max_month': float(df[numeric_cols].max().max()),
                'min_month': float(df[numeric_cols].min().min()),
                'peak_month': peak_month,
                'low_month': low_month,
                'regional_totals': regional_data.sum(axis=1).to_dict(),
                'monthly_totals': monthly_data.to_dict(),
                'top_regions': top_regions.to_dict(),
                'name': name
            }

        domestic_analysis = get_analysis(self.domestic_df, 'Domestic')
        foreign_analysis = get_analysis(self.foreign_df, 'Foreign')

        total_visitors = domestic_analysis['total'] + foreign_analysis['total']
        analysis = {
            'domestic': domestic_analysis,
            'foreign': foreign_analysis,
            'comparisons': {
                'domestic_percentage': (domestic_analysis['total'] / total_visitors) * 100,
                'foreign_percentage': (foreign_analysis['total'] / total_visitors) * 100,
                'total_visitors': total_visitors,
                'ratio': foreign_analysis['total'] / domestic_analysis['total']
            }
        }
        return analysis

    def create_monthly_comparison_plot(self):
        """Create monthly comparison visualization"""
        fig = go.Figure()
        
        # Get numeric columns
        numeric_cols = self.domestic_df.select_dtypes(include=[np.number]).columns
        
        # Monthly trends for domestic
        domestic_monthly = self.domestic_df[numeric_cols].mean()
        fig.add_trace(go.Scatter(
            x=list(domestic_monthly.index),
            y=domestic_monthly.values,
            name='Domestic',
            mode='lines+markers',
            line=dict(color='#1f77b4')
        ))
        
        # Monthly trends for foreign
        foreign_monthly = self.foreign_df[numeric_cols].mean()
        fig.add_trace(go.Scatter(
            x=list(foreign_monthly.index),
            y=foreign_monthly.values,
            name='Foreign',
            mode='lines+markers',
            line=dict(color='#ff7f0e')
        ))
        
        fig.update_layout(
            title='Monthly NUTS2 Domestic vs Foreign Visitors',
            xaxis_title='Month',
            yaxis_title='Average Visitors',
            template='plotly_white',
            showlegend=True,
            height=500
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def create_regional_distribution_plot(self):
        """Create regional distribution visualization"""
        fig = go.Figure()
        
        # Get numeric columns
        numeric_cols = self.domestic_df.select_dtypes(include=[np.number]).columns
        region_col = self.domestic_df.columns[0]
        
        # Regional totals for domestic
        domestic_regional = self.domestic_df.groupby(region_col)[numeric_cols].sum().sum(axis=1)
        fig.add_trace(go.Bar(
            name='Domestic',
            x=domestic_regional.index,
            y=domestic_regional.values,
            marker_color='#1f77b4'
        ))
        
        # Regional totals for foreign
        foreign_regional = self.foreign_df.groupby(region_col)[numeric_cols].sum().sum(axis=1)
        fig.add_trace(go.Bar(
            name='Foreign',
            x=foreign_regional.index,
            y=foreign_regional.values,
            marker_color='#ff7f0e'
        ))
        
        fig.update_layout(
            title='Regional Distribution of NUTS2 Domestic vs Foreign Visitors',
            xaxis_title='Region',
            yaxis_title='Total Visitors',
            barmode='group',
            template='plotly_white',
            height=600,
            xaxis={'tickangle': 45}
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def create_pie_chart(self):
        """Create pie chart for domestic vs foreign distribution"""
        analysis = self.analyze_data()
        
        fig = go.Figure(data=[go.Pie(
            labels=['Domestic', 'Foreign'],
            values=[analysis['domestic']['total'], analysis['foreign']['total']],
            hole=.3,
            marker=dict(colors=['#1f77b4', '#ff7f0e'])
        )])
        
        fig.update_layout(
            title='Distribution of NUTS2 Domestic vs Foreign Visitors',
            template='plotly_white',
            height=400,
            annotations=[dict(text='Total', x=0.5, y=0.5, font_size=20, showarrow=False)]
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