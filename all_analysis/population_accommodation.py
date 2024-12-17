# all_analysis/population_accommodation.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly
import numpy as np

class PopulationAccommodationAnalyzer:
    def __init__(self):
        self.nuts1_pop = None
        self.nuts2_pop = None
        self.nuts1_acc = None
        self.nuts2_acc = None
        self.load_data()

    def load_data(self):
        """Load population and accommodation data"""
        try:
            # Load population data
            self.nuts1_pop = pd.read_excel('data/nuts_1_population.xlsx')
            self.nuts2_pop = pd.read_excel('data/nuts_2_population.xlsx')
            
            # Load accommodation data
            self.nuts1_acc = pd.read_excel('data/nuts_1_2023.xlsx')
            self.nuts2_acc = pd.read_excel('data/nuts_2_2023.xlsx')
            
            self.clean_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def clean_data(self):
        """Clean and prepare the data"""
        def clean_accommodation_df(df):
            cleaned = df.copy()
            # Replace ':' with NaN
            cleaned = cleaned.replace(':', np.nan)
            
            # Convert numeric columns
            numeric_cols = cleaned.columns[1:] if isinstance(cleaned.columns[0], str) else cleaned.columns
            for col in numeric_cols:
                cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce')
            
            return cleaned.dropna(how='all')

        def clean_population_df(df):
            cleaned = df.copy()
            # Assuming the last column is the population data
            pop_col = cleaned.columns[-1]
            cleaned[pop_col] = pd.to_numeric(cleaned[pop_col], errors='coerce')
            return cleaned

        self.nuts1_acc = clean_accommodation_df(self.nuts1_acc)
        self.nuts2_acc = clean_accommodation_df(self.nuts2_acc)
        self.nuts1_pop = clean_population_df(self.nuts1_pop)
        self.nuts2_pop = clean_population_df(self.nuts2_pop)

    def calculate_intensity_metrics(self):
        """Calculate accommodation intensity metrics"""
        # Get population column names
        nuts1_pop_col = self.nuts1_pop.columns[-1]
        nuts2_pop_col = self.nuts2_pop.columns[-1]

        # NUTS1 calculations
        nuts1_acc_total = self.nuts1_acc.iloc[:, 1:].sum(axis=1)
        nuts1_intensity = (nuts1_acc_total / self.nuts1_pop[nuts1_pop_col]).fillna(0)
        
        # NUTS2 calculations
        nuts2_acc_total = self.nuts2_acc.iloc[:, 1:].sum(axis=1)
        nuts2_intensity = (nuts2_acc_total / self.nuts2_pop[nuts2_pop_col]).fillna(0)
        
        return {
            'nuts1': {
                'intensity': nuts1_intensity.to_dict(),
                'total_accommodation': nuts1_acc_total.to_dict(),
                'population': self.nuts1_pop[nuts1_pop_col].to_dict()
            },
            'nuts2': {
                'intensity': nuts2_intensity.to_dict(),
                'total_accommodation': nuts2_acc_total.to_dict(),
                'population': self.nuts2_pop[nuts2_pop_col].to_dict()
            }
        }

    def analyze_seasonal_patterns(self):
        """Analyze seasonal patterns in accommodation"""
        def get_seasonal_stats(df):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            monthly_totals = df[numeric_cols].sum()
            peak_month = monthly_totals.idxmax()
            low_month = monthly_totals.idxmin()
            seasonality_index = monthly_totals.std() / monthly_totals.mean()
            return {
                'monthly_totals': monthly_totals.to_dict(),
                'peak_month': peak_month,
                'low_month': low_month,
                'seasonality_index': float(seasonality_index)
            }
        
        return {
            'nuts1': get_seasonal_stats(self.nuts1_acc),
            'nuts2': get_seasonal_stats(self.nuts2_acc)
        }

    def create_intensity_map(self):
        """Create visualization for accommodation intensity"""
        metrics = self.calculate_intensity_metrics()
        
        # Create DataFrame for plotting
        intensity_data = pd.DataFrame({
            'Region': list(metrics['nuts1']['intensity'].keys()),
            'Intensity': list(metrics['nuts1']['intensity'].values())
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=intensity_data['Region'],
            y=intensity_data['Intensity'],
            name='NUTS1 Regions',
            marker_color='#1f77b4'
        ))
        
        fig.update_layout(
            title='Accommodation Intensity by Region (Guests per Capita)',
            xaxis_title='Region',
            yaxis_title='Guests per Capita',
            template='plotly_white',
            height=500,
            xaxis={'tickangle': 45}
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def create_seasonal_pattern_plot(self):
        """Create visualization for seasonal patterns"""
        fig = go.Figure()
        
        # NUTS1 seasonal pattern
        nuts1_monthly = self.nuts1_acc.select_dtypes(include=[np.number]).sum()
        fig.add_trace(go.Scatter(
            x=list(nuts1_monthly.index),
            y=nuts1_monthly.values,
            name='NUTS1',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title='Seasonal Pattern of Accommodation Usage',
            xaxis_title='Month',
            yaxis_title='Total Guests',
            template='plotly_white',
            height=500
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def create_population_vs_accommodation_plot(self):
        """Create scatter plot of population vs accommodation"""
        metrics = self.calculate_intensity_metrics()
        
        # Get population column names
        nuts1_pop_col = self.nuts1_pop.columns[-1]
        
        fig = go.Figure()
        
        # NUTS1 scatter plot
        fig.add_trace(go.Scatter(
            x=list(metrics['nuts1']['population'].values()),
            y=list(metrics['nuts1']['total_accommodation'].values()),
            mode='markers+text',
            name='NUTS1 Regions',
            text=list(metrics['nuts1']['population'].keys()),
            textposition="top center",
            marker=dict(size=12)
        ))
        
        fig.update_layout(
            title='Population vs Total Accommodation by Region',
            xaxis_title='Population',
            yaxis_title='Total Accommodation',
            template='plotly_white',
            height=600,
            showlegend=True
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def get_full_analysis(self):
        """Get complete analysis including visualizations"""
        metrics = self.calculate_intensity_metrics()
        seasonal = self.analyze_seasonal_patterns()
        
        # Combine analyses
        analysis = {
            'metrics': metrics,
            'seasonal': seasonal,
            'insights': {
                'nuts1_highest_intensity': max(metrics['nuts1']['intensity'].items(), key=lambda x: x[1]),
                'nuts1_lowest_intensity': min(metrics['nuts1']['intensity'].items(), key=lambda x: x[1]),
                'seasonality_index_nuts1': seasonal['nuts1']['seasonality_index'],
                'peak_month_nuts1': seasonal['nuts1']['peak_month'],
                'low_month_nuts1': seasonal['nuts1']['low_month']
            }
        }
        
        plot_data = {
            'intensity_map': self.create_intensity_map(),
            'seasonal_pattern': self.create_seasonal_pattern_plot(),
            'population_accommodation': self.create_population_vs_accommodation_plot()
        }
        
        return analysis, plot_data