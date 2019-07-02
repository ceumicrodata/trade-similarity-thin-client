# coding=utf-8

import os
import dash_core_components as dcc
import dash_html_components as html
import json
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from dash import Dash
from flask import Flask

slopechart_dict = json.load(open('data/slopechart.json'))
heatmap_dict = json.load(open('data/heatmap.json'))
YEARS = json.load(open('data/years.json'))
PARTNERS = json.load(open('data/partners.json'))
NEW_MEMBER_STATES = json.load(open('data/new_member_states.json'))

def update_slopechart(_, selected):
    Declarants, Emphasized = NEW_MEMBER_STATES, []
    return {
        'data': [go.Scatter(**line) for line in slopechart_dict[selected]],
        'layout': go.Layout(
            xaxis={
                'title': "Year",
            },
            yaxis={
                'title': "Trade Similarity Index",
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }


fl_server = Flask('Trade Similarity Index')
app = Dash(name='Trade Similarity Index', server=fl_server)
app.server.secret_key = 'notterriblysecret'
server = app.server

mathjax = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'
app.scripts.append_script({ 'external_url' : mathjax })

layout = html.Div([
      html.Div([
        dcc.Markdown('''
          # Trade Similarity Index
          ***
          ## Motivation
          We use detailed product-level trade data to construct a Trade Similarity Index for each Member State. This involves measuring the external export and import structure towards third countries. The index captures the relevant economic structure of the Member States (for exports) and changes in applied external tariffs (for imports). A low value of the Trade Similarity Index for a Member State suggests that it has incentives to use national trade and investment promotion instruments to offset at least to some extent the effects of adopting the common commercial policy of the EU. The Trade Similarity Index provides valuable information on changes in trade structure over time and the incentives for national agencies to pursue idiosyncratic policies.

          The Trade Similarity Index takes values between 0 and 1. A higher value indicates that the trade patter on the Member State is *more similar* to the average of the European Union. A value of 0 means that there is no product overlap between the exports (or imports) of the Member State and the rest of the EU. A value of 1 means that the Member State exports (or imports) every product in the same proportion as the rest of the EU.

          ***
          ''', 
          className='container',
          style = {'maxWidth': '650px'}
        ),

        dcc.Dropdown(id="selected-year", options=[{"label": i, "value": i} for i in YEARS],
                   value='2017',
                   style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "60%"}),

        dcc.Graph(id="heatmap", style={"margin-right": "auto", "margin-left": "auto", "width": "60%"}, className='row'),

        dcc.Markdown('''
          ***
          ## Data and Methodology
          ### Data
          1. Data is downloaded from Eurostat Comext at [URL]
          2. We only keep trade flows in normal statistical regime (excluding, for example, processing trade)
          3. We aggregate all trade flows up to 6-digit Harmonized System products.
          4. There are cases when product codes are masked to protect confidentiality of individual sellers, affecting about 2--3 percent of trade value. Because these product codes are available at the Chapter (2-digit) level, we redistribute the total value of confidential trade across the reported, non-confidential product codes of the same Chapter.

          ### Computation
          $$ \\sum_\{p=1\}^P s_{ijp}\\ln(s_{ijp}/s_{jp}) $$
          This is the [Kullback-Leibler divergence](https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence) between the product shares (i,j) and the product shares (baseline,j).
          ''', 
          className='container',
          style = {'maxWidth': '650px'}
        ),

        html.P('$$ \\sum_\{p=1\}^P s_{ijp}\\ln(s_{ijp}/s_{jp}) $$'),

        dcc.Dropdown(id="selected-partner", options=[{"label": i, "value": i} for i in PARTNERS],
                   value='RU',
                   style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "60%"}),

        dcc.Graph(id="slopechart",
                figure = update_slopechart(None, 'RU'),
                style={"margin-right": "auto", "margin-left": "auto", "width": "60%"})],
                className="row"),

        dcc.Markdown('''
          ## State of the art

          All indexes of similarity start with a vector of trade shares si and sj and compute
          $$
          sum_p f(s_\{ip}, s_\{jp}),
          $$  
          for various functions $f$.

          The Krugman Specialization Index (Krugman, 1991) uses \\(f(x, y) = |x - y|\\). This index captures the absolute percentage deviation between trade shares.

          An alternative measure is the Finger-Kreining index (Finger and Kreinin, 1979), with $f(x) = min(x, y)$, capturing the least amount of overlap between the two trade shares.

          Fontagné et al (2018) use dissimularity measures for binary vectors, with $s_\{ip\}in \{0,1\}$, such as the Levenshtein distance and the Bray-Curtis measure.

          None of these indexes are based on economic theory. By contract assume that consumers have CES preferences over the individual products, with elasticity of substitution sigma. 
          ```
          f(x, y) = x^{1/sigma} y^{1-1/sigma}
          ```
          In the limite, when $sigma to 1$, this index converges to the Kullback-Leibler divergence.

          ### References
          - Krugman, Paul. 1991. Geography and Trade. Cambridge: MIT Press.
          - Finger, J. M., and M. E. Kreinin. 1979. “A Measure of 'Export Similarity' and Its Possible Uses.” The Economic Journal 89 (356): 905–12.
          - Fontagné, Lionel, Angelo Secchi, and Chiara Tomasi. 2018. “Exporters’ Product Vectors across Markets.” European Economic Review 110 (November): 150–80.
          ''', 
          className='container',
          style = {'maxWidth': '650px'}
        ),

        ], style={'align': "center"})

app.layout = layout

@app.callback(
    Output("heatmap", "figure"),
    [Input("selected-year", "value"),
    Input("selected-partner", "value")])

#@app.callback(
#    Output("slopechart", "figure"),
#    [Input("selected-partner", "value")])

def update_figure(selected, _):
    trace = go.Heatmap(heatmap_dict[selected], colorscale='Electric', colorbar={"title": "KDL"}, showscale=True, zauto=False, zmin=0, zmax=1)
    return {"data": [trace],
            "layout": go.Layout(width=800, height=750,  
                                xaxis={"title": "Partner"},
                                yaxis={"title": "Reporter"} )}



if __name__ == '__main__':
    app.run_server()
    
'''
FIXME:
- Write down and explain formula.
- Add Kullback-Leibler reference.
- Use MathJax to embed formulas.
- Allow for multiple inputs to update both graphs.
- Pick color for line graph.
- Annotate charts.
'''
