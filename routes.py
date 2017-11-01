from views import index, oauth_login, oauth_complete


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/oauth/login', oauth_login)
    app.router.add_get('/oauth/complete', oauth_complete)
