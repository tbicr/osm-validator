from . import views


async def setup(app):
    app.router.add_get('/', views.index, name='index')
    app.router.add_get('/oauth/login', views.oauth_login, name='oauth:login')
    app.router.add_get('/oauth/complete', views.oauth_complete, name='oauth:complete')
