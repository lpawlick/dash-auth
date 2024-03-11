from dash import Dash, dcc, html, callback, Input, Output
import dash_auth

def authenticate(username, password, path):
    print(path)
    if (path.startswith('/_')): # Internal Dash requests
        return (username == 'hello' and password == 'world') or (username == 'world' and password == 'hello')
    elif (path == '/page-1'):
        return username == 'hello' and password == 'world'
    elif (path == '/page-2'):
        return username == 'world' and password == 'hello'
    elif (path == '/'):
        return (username == 'hello' and password == 'world') or (username == 'world' and password == 'hello')
    else: # Deny any other paths
        return False 
    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
auth = dash_auth.BasicAuth(
    app,
    auth_func=authenticate
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    dcc.Link('Only accessible to hello world', href='/page-1'),
    html.Br(),
    dcc.Link('Only accessible to world hello', href='/page-2'),
])

page_1_layout = html.Div([
    html.H1('Hello World'),
    dcc.Dropdown(['LA', 'NYC', 'MTL'], 'LA', id='page-1-dropdown'),
    html.Div(id='page-1-content'),
    html.Br(),
    dcc.Link('Only accessible to world hello', href='/page-2'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
])


@callback(Output('page-1-content', 'children'),
            Input('page-1-dropdown', 'value'))
def page_1_dropdown(value):
    return f'You have selected {value}'


page_2_layout = html.Div([
    html.H1('World Hello'),
    dcc.RadioItems(['Orange', 'Blue', 'Red'], 'Orange', id='page-2-radios'),
    html.Div(id='page-2-content'),
    html.Br(),
    dcc.Link('Only accessible to hello world', href='/page-1'),
    html.Br(),
    dcc.Link('Go back to home', href='/')
])


@callback(Output('page-2-content', 'children'), Input('page-2-radios', 'value'))
def page_2_radios(value):
    return f'You have selected {value}'


# Update the index
@callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run(debug=True)