from . import views


async def setup(app):
    app.router.add_static('/static/', path='./static/', name='static')
    app.router.add_get('/', views.index, name='index')
    app.router.add_get('/oauth/login', views.oauth_login, name='oauth:login')
    app.router.add_get('/oauth/complete', views.oauth_complete, name='oauth:complete')
    app.router.add_get('/out', views.sign_out, name='sign:out')
    app.router.add_get('/user/info', views.user_info, name='user:info')
