from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import ( HTTPFound, HTTPNotFound )
from formencode import Schema, validators
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Quote,
    )

@view_config(route_name='home', renderer='home.jinja2')
def home(request):
    return dict()
        
class QuoteSchema(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    
    quote = validators.MinLength(5, not_empty=True)

@view_config(route_name='add', renderer='add.jinja2')
def add(request):
    form = Form(request,
                defaults={},
                schema=QuoteSchema())
    
    if form.validate():
        quote = form.bind(Quote())
        quote.votes = 0
        DBSession.add(quote)
        DBSession.flush()
        return HTTPFound(location=request.route_url('view',id=quote.id))

    return dict(renderer=FormRenderer(form), test=form.errors)

@view_config(route_name='view', renderer='view.jinja2')
def view(request):
    return dict()
    
@view_config(route_name='view_json', renderer='json')
def view_json(request):
    id = request.matchdict['id']
    
    quote = DBSession.query(Quote).filter_by(id=id).first()
    if not quote:
        return HTTPNotFound('Beep!')
    return dict(votes=quote.votes, quote=quote.quote)
    
@view_config(route_name='list', renderer='list.jinja2')
def list(request):
    return dict()

@view_config(route_name='list_json', renderer='json')
def list_json(request):
    quotes = DBSession.query(Quote).all()
    return [dict(id=quote.id,
                 quote=quote.quote) for quote in quotes]

@view_config(route_name='template', renderer='template.jinja2')
def template(request):
    return {}
    

@view_config(route_name='vote')
def vote_post(request):
    id = request.matchdict['id']
    direction = request.matchdict['direction']
    
    quote = DBSession.query(Quote).filter_by(id=id).first()
    if not quote:
        return HTTPNotFound('Beep!')
        
    if direction == 'up':
        quote.votes += 1
    elif direction == 'down':
        quote.votes -= 1
        
    return HTTPFound(location=request.route_url('view',id=quote.id))

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_quotes_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

