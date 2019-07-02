import os
import dash_core_components as dcc
import dash_html_components as html
import json
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from dash import Dash
from flask import Flask


YEARS = json.load(open('data/years_EXP.json'))
PARTNERS = json.load(open('data/partners_EXP.json'))
NEW_MEMBER_STATES = json.load(open('data/new_member_states_EXP.json'))

country_codes = json.load(open('data/countries.json'))

slopechart_dict = dict(EXPORT=json.load(open('data/slopechart_EXP.json')), IMPORT=json.load(open('data/slopechart_IMP.json')))
heatmap_dict = dict(EXPORT=json.load(open('data/heatmap_EXP.json')), IMPORT=json.load(open('data/heatmap_IMP.json')))


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
          ***
          The Trade Similarity Index takes values between 0 and 1. A higher value indicates that the trade pattern of the Member State is *more similar* to the average of the European Union. A value of 0 means that there is no product overlap between the exports (or imports) of the Member State and the rest of the EU. A value of 1 means that the Member State exports (or imports) every product in the same proportion as the rest of the EU.

          ***
          # Cross Sectional Patterns

          The following chart displays the Trade Similarity Index for all 28 Member States. The index can be computed vis-a-vis any third country with which both the Member State and the rest of the EU trade. In the heatmap we display it for selected third countries.
          ***
          A low value of the index between a Member State and a third country means that that Member State has special trade relations with that country, with low similarity to other EU countries. For example, the exports of Malta to Montenegro in 2017 is the least similar to EU average, with a Trade Similarity Index of only 0.20. By contrast, German exports to Russia in 2017 are the most similar to exports of other EU countries to Russia (TSI=0.93). Looking for cases of dissimilarity can reveal country pairs where the trade patterns are least similar to the EU average, and the incentive to deviate from a common trade policy is the largest.

          ''', 
          className='container',
          style = {'maxWidth': '650px'}
        ),

        dcc.Dropdown(id="selected_flow", options=[{"label": i, "value": i} for i in ["EXPORT","IMPORT"]],
           value='EXPORT',
           style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "60%"}),

        dcc.Dropdown(id="selected_year", options=[{"label": i, "value": i} for i in YEARS],
                   value='2017',
                   style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "60%"}),

        dcc.Graph(id="heatmap", style={"margin-right": "auto", "margin-left": "auto", "width": "60%"}, className='row'),

        dcc.Markdown('''
          # Trends

          This chart shows the evolution of the Trade Similarity Index of new Member States vis-a-vis select third countries. Broadly speaking, the export composition of new Member States becomes more and more similar to the rest of the EU over time.
          ''', 
          className='container',
          style = {'maxWidth': '650px'}
        ),

        dcc.Dropdown(id="selected_partner", options=[{"label": country_codes[i], "value": i} for i in PARTNERS],
                   value='RU',
                   style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "60%"}),

        dcc.Graph(id="slopechart",
                style={"margin-right": "auto", "margin-left": "auto", "width": "60%"})],
                className="row"),

        dcc.Markdown('''
          ## Data and Methodology
          ### Data
          1. Data is downloaded from Eurostat Comext (Eurostat, 2019).
          2. We only keep trade flows in normal statistical regime (excluding, for example, processing trade).
          3. We aggregate all trade flows up to 6-digit Harmonized System products.
          4. There are cases when product codes are masked to protect confidentiality of individual sellers, affecting about 2--3 percent of trade value. Because these product codes are available at the Chapter (2-digit) level, we redistribute the total value of confidential trade across the reported, non-confidential product codes of the same Chapter.

          ### Computation
          We compare the export- and import-composition of a Member State vis-a-vis a third country with the EU average. Let *s(ijp)* denote the export share of product *p* in total exports of country *i* to country *j*. We compute a baseline export share *s(0jp)* as the export share of all other countries in the EU. We are interested in how similar is *s(ijp)* to *s(0jp)*.
          ***
          We first compute the Kullback-Leibler divergence (Kullback, 1987) between the two trade share vectors as
          ''', 
          className='container',
          style = {'maxWidth': '650px'}
        ),
        html.Div(html.Img(src=app.get_asset_url('KLD.png')),
          className='container',
          style = {'maxWidth': '650px', 'textAlign': 'center'}
        ),
        dcc.Markdown('''
          As the name suggests, the Kullback-Leibler divergence is a measure of distance.
          This measure takes a value of 0 if the two vectors are the same, and can be arbitrarily large for different vectors.

          We convert it into a Trade Similarity Index as  
          ''', 
          className='container',
          style = {'maxWidth': '650px'}
        ),
        html.Div(html.Img(src=app.get_asset_url('utility.png')),
          className='container',
          style = {'maxWidth': '650px', 'textAlign': 'center'}
        ),
        dcc.Markdown('''
          where theta is a positive parameter, capturing how substitutable the different products are in the eyes of the consumer.

          This is an index of *similarity*, taking larger values whenever the two vectors are more similar. The index is bounded between 0 and 1, being 0 if the two vectors have no common elements, and 1 if the two vectors are identical. 

          The theoretical justification of this index (as noted on the left-hand-side of the equation) is that consumers evaluating choices across products with an elasticity of substitution theta would value a forced substitution this much less. That is, if a consumer would prefer to consumer *s(ijp)* but is forced to consume *s(0jp)* instead, her utility is lower by a factor corresponding to the Trade Similarity Index. Hence an index of 0.75 means a utility loss of 25 percent.   

          ## State of the art

          All indexes of similarity start with a vector of sector/product shares *si* and *sj* and compute
          ''', 
          className='container',
          style = {'maxWidth': '650px'}
        ),

        html.Div(html.Img(src=app.get_asset_url('index.png')),
          className='container',
          style = {'maxWidth': '650px', 'textAlign': 'center'}
        ),

        dcc.Markdown('''
          for various functions *f*.

          The Krugman Specialization Index (Krugman, 1991) uses *f*(*x*, *y*) = |*x* - *y*|. This index captures the absolute percentage deviation between trade shares.

          An alternative measure is the Finger-Kreining index (Finger and Kreinin, 1979), with *f*(*x*) = min(*x*, *y*), capturing the least amount of overlap between the two trade shares.

          Fontagné et al (2018) use dissimularity measures for binary vectors, with *sip* in \{0,1\}, such as the Levenshtein distance and the Bray-Curtis measure.

          In contrast to our measure of similarity, none of these indexes are based on economic theory.
          ''', 
          className='container',
          style = {'maxWidth': '650px'}
        ),

         dcc.Markdown('''
         ### References
          - Eurostat. 2019. “COMEXT: International Trade in Goods.” http://epp.eurostat.ec.europa.eu/newxtweb/mainxtnet.do.
          - Finger, J. M., and M. E. Kreinin. 1979. “A Measure of 'Export Similarity' and Its Possible Uses.” The Economic Journal 89 (356): 905–12.
          - Fontagné, Lionel, Angelo Secchi, and Chiara Tomasi. 2018. “Exporters’ Product Vectors across Markets.” European Economic Review 110 (November): 150–80.
          - Krugman, Paul. 1991. Geography and Trade. Cambridge: MIT Press.
          - Kullback, Solomon. 1987. “Letters to the Editor: The Kullback-Leibler Distance.” The American Statistician 41 (4): 338–41.
          ''', 
          className='container',
          style = {'maxWidth': '650px'}
        ),

        ], style={'align': "center"})

app.layout = layout

@app.callback(
    Output("heatmap", "figure"),
    [Input("selected_year", "value"),
    Input("selected_flow","value")])

def update_figure(selected_year, selected_flow):
    print(selected_flow)
    trace = go.Heatmap(heatmap_dict[selected_flow][selected_year], colorscale='Electric', colorbar={"title": "KDL"}, showscale=True, zauto=False, zmin=0, zmax=1)
    return {"data": [trace],
            "layout": go.Layout(width=800, height=750, title=f"{selected_year.title()}", 
                                xaxis={"title": "Partner"},
                                yaxis={"title": "Reporter"} )}

@app.callback(
    Output("slopechart", "figure"),
    [Input("selected_partner", "value"),
    Input("selected_flow","value")])

def update_slopechart(selected_partner, selected_flow):
    Declarants, Emphasized = NEW_MEMBER_STATES, []
    return {
        'data': [go.Scatter(**line) for line in slopechart_dict[selected_flow][selected_partner]],
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
