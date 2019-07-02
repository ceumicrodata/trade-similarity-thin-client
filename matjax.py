import dash
import dash_html_components as html

app = dash.Dash(__name__)
mathjax = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'
app.scripts.append_script({ 'external_url' : mathjax })

app.layout = html.Div(id='main',children=[
  html.P(children='Delicious \(\pi\) is inline with my goals.'),
  html.P(children='$$ \lim_{t \\rightarrow \infty} \pi = 0$$'),
  html.P(style={'text-align':'left'}, children='\(\\leftarrow \pi\)'),
  html.P(style={'text-align':'left'}, children='not much left.'),
  html.P(style={'text-align':'right'},children='\(\pi \\rightarrow\)'),
  html.P(style={'text-align':'right'},children='but it feels so right.'),
])

if __name__ == '__main__':
  app.run_server(debug=True)
