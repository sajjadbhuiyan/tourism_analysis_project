# app.py
from flask import Flask, render_template
from all_analysis.nuts1_and_nuts2 import DataAnalyzer
from all_analysis.nuts1_foreign_domestic import ForeignDomesticAnalyzer
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nuts1_and_nuts2')
def nuts_analysis():
    analyzer = DataAnalyzer()
    nuts1_analysis, nuts2_analysis, plot_data = analyzer.get_full_analysis()
    return render_template('nuts1_and_nuts2.html', 
                         nuts1=nuts1_analysis,
                         nuts2=nuts2_analysis,
                         plot_data=plot_data)

@app.route('/nuts1_foreign-domestic')
def foreign_domestic():
    analyzer = ForeignDomesticAnalyzer()
    analysis, plot_data = analyzer.get_full_analysis()
    return render_template('nuts1_foreign_domestic.html',
                         analysis=analysis,
                         plot_data=plot_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)