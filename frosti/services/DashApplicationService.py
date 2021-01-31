import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from threading import Thread

from frosti.logging import log, handleException
from frosti.core import ServiceProvider, ServiceConsumer, EventBus


class DashApplicationService(ServiceConsumer):

    def __init__(self):
        self._app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.CERULEAN],
            meta_tags=[{"name": "viewport",
                        "content": "width=device-width, initial-scale=1"}],
        )
        self._server = self._app.server
        self._app.config["suppress_callback_exceptions"] = True

        def renderStatus():
            return html.P("status")

        @self._app.callback(
            Output("page-content", "children"),
            [Input("url", "pathname")])
        def render_page_content(pathname):
            if pathname == "/":
                return html.P("root")
            if pathname == "/setup":
                return html.P("setup!")
            if pathname == "/program":
                return html.P("program!")
            if pathname == "/status":
                return renderStatus()

            return dbc.Jumbotron(
                children=[
                    html.H1("404: Not found", className="text-danger"),
                    html.Hr(),
                    html.P(f"The pathname {pathname} was not recognised..."),
                ]
            )

        self._app.layout = html.Div([
            dcc.Location(id="url"),
            dbc.Navbar(
                children=[
                    html.A(
                        dbc.Row(
                            children=[
                                dbc.Col(dbc.NavbarBrand(
                                    "FROSTI", className="ml-2")),
                            ],
                            align="center",
                            no_gutters=True,
                        ),
                        href="/",
                    ),
                    dbc.Nav([
                        dbc.NavLink("Home", href="/", active="exact"),
                        dbc.NavLink("Setup", href="/setup", active="exact"),
                        dbc.NavLink("Program", href="/program",
                                    active="exact"),
                        dbc.NavLink("Status", href="/status", active="exact"),
                    ],
                        pills=True,
                    ),
                    dbc.NavbarToggler(id="navbar-toggler"),
                ],
                color='dark',
                dark=True,
            ),
            dbc.Container(id="page-content", className="pt-4"),
        ], style=dict(width='100%'))

        self.__dashThread = Thread(
            target=self.__dashEntryPoint,
            name='Dash Driver')
        self.__dashThread.daemon = True
        self.__dashThread.start()

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        self.__eventBus = self._getService(EventBus)

    def __dashEntryPoint(self):
        try:
            self._app.run_server("0.0.0.0", port=8050)
            log.error("Somehow we exited the Flask thread")
        except:
            handleException("starting flask")
