from pyramid.request import Response
from pyramid.request import Request
from pyramid.view import view_config, view_defaults, notfound_view_config

from sqlalchemy.exc import DBAPIError
import mysql.connector
import bcrypt, datetime

import os
import uuid
import shutil

import cgi
import re
#from docutils.core import publish_parts

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)

from .models import (
    Userinfo,
    )

from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.security import (
    remember,
    forget,
    )

from .security import USERS

from dbconnection import Session
sess=Session()

@view_defaults(renderer='json')
class Views:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid

    # CUSTOM PREDICATES: LOGIN: account verified form confirm/{key}
    def verified(context, request):
        user = sess.query(Userinfo).filter(Userinfo.email==request.POST.get('email')).first()
        if user is None:
            return False
        #elif user.created is None:
            #return False
        return True

    #login
    @view_config(route_name='login', request_method='OPTIONS')
    def login_options(self):
        resp = self.request.response
        return resp

    @view_config(route_name='login',  request_method='POST')
    def login(self):
        request = self.request
        resp = request.response
        from sys import exc_info
        try:
            user = sess.query(Userinfo).filter(Userinfo.Email == request.json_body.get('email')).first() # request.json_body.get('email')).first()
            if user is None:
                return Response(json=dict(rc=400, msg="Login Error: no such user"), status_code=400)
            if user.Password == request.json_body.get('password'):
                #user.pwhash == bcrypt.hashpw(bytes(request.POST.get('password'), 'utf-8'), user.salt):
                #request.sess[request.POST.get('email')] = 'sessionstart'
                #request.session.save()
                #headers = remember(request, request.json_body.get('email'))
                #headers.append(('X-CSRF-token', request.session.new_csrf_token()))

                resp.status_code = 200
                #(json=dict(rc=200, msg="Login Successful", user=user.Email, userid=user.ID), status_code=200)
                #resp.headerlist.append(('Access-Control-Allow-Origin', '*'))
                return dict(rc=200, msg="Login Successful", user=user.Email, userid=user.ID)

            #sess.remove()
            #resp.status_code = 400
            return resp(json=dict(rc=400, msg="Login Error: Email and password don't match"), status_code=400)
        except DBAPIError:
            return resp(conn_err_msg, content_type='text/plain', status_int=400)
        except:
            print (exc_info())
            return resp(json=dict(rc=400, msg="Login Error: unknown error"), status_code=400)

    #Signup
    @view_config(route_name='signup', request_method='OPTIONS')
    def signup_options(self):
        resp = self.request.response
        return resp

    @view_config(route_name='signup')
    def signup(self):
        request = self.request
        resp = request.response
        user = Userinfo()
        username=request.json_body.get('username')
        email = request.json_body.get('email')
        pwd = request.json_body.get('password')
        salt = bcrypt.gensalt()
        #user.pwhash = bcrypt.hashpw(bytes(request.POST.get('password'), 'utf-8'), user.salt)
        #user.active = False

        #user.key = bcrypt.hashpw(bytes(request.POST.get('email'), 'utf-8'), bcrypt.gensalt())

        from models import AddNewUser
        Uid=AddNewUser(username,pwd,email,salt)
        if (Uid>0):
            return Response(json=dict(rc=200, msg="Sign up: Sign up successful"), status_code=200)
        else:
            return Response(json=dict(rc=200, msg="Sign up: Sign up fail"), status_code=200)

    # save a posted image

    @view_config(route_name='post', request_method='OPTIONS')
    def post_options(self):
        resp = self.request.response  # (json=dict(rc=200, msg="Options Successful"), status_code=200)
        # resp.headerlist.append(('Access-Control-Allow-Origin', 'http://localhost:8000'))
        return resp

    @view_config(route_name='post', request_method='POST')
    def post(self):
        request = self.request
        resp = request.response
        from sys import exc_info
        # ``filename`` contains the name of the file in string format.
        #
        # WARNING: this example does not deal with the fact that IE sends an
        # absolute file *path* as the filename.  This example is naive; it
        # trusts user input.
        try:
            filename = request.POST['file'].filename

            # ``input_file`` contains the actual file data which needs to be
            # stored somewhere.
            if (filename):
                input_file = request.POST['file'].file

                # strip leading path from file name to avoid directory traversal attacks
                fn = os.path.basename(filename)
                # open('../static/img/' + fn, 'wb').write(input_file.file.read())

                # Note that we are generating our own filename instead of trusting
                # the incoming filename since that might result in insecure paths.
                # Please note that in a real application you would not use /tmp,
                # and if you write to an untrusted location you will need to do
                # some extra work to prevent symlink attacks.
                RealPath = '/Users/zoe/Desktop/Projects/lc_frontend/app/lookchic/static/img'
                RelativePath = 'lookchic/static/img'
                Saved_file_name = '%s' % uuid.uuid4() + '.' + fn.rpartition('.')[2]
                file_path = os.path.join(RealPath, Saved_file_name)
                Relative_file_path = os.path.join(RelativePath, Saved_file_name)
                # We first write to a temporary file to prevent incomplete files from
                # being used.

                temp_file_path = file_path + '~'

                # Finally write the data to a temporary file
                input_file.seek(0)
                with open(temp_file_path, 'wb') as output_file:
                    shutil.copyfileobj(input_file, output_file)

                # Now that we know the file has been fully saved to disk move it into place.

                os.rename(temp_file_path, file_path)
                resp.status_code = 200
                import json
                user_object=json.loads(request.POST.get('username'))
                userid=user_object['userid']

                from postevents import addphotoEvent
                pic_id = addphotoEvent(userid, RelativePath,Saved_file_name)

                return dict(rc=200, msg="File uploaded")
            else:
                resp.status_code = 400
                return dict(rc=400, msg="no file name")
        except:
            print (exc_info())
            resp.status_code = 400
            return dict(rc=400, msg="Post Error: unknown error")

    #fetch feeds
    @view_config(route_name='main', request_method='OPTIONS')
    def main_options(self):
        resp = self.request.response
        return resp

    @view_config(route_name='main')
    def main(self):
        request = self.request
        resp = request.response

        userid = request.json_body.get('userid')
        page = request.json_body.get('page')

        result=list()
        #fake1 = dict(username="Yuan",url="images/test_img/sample2.jpg",time="June 18 2015")
        #fake2 = dict(username="Allen",url="images/test_img/sample4.jpg",time="August 18 2015")
        #result.append(fake1)
        #result.append(fake2)
        from postevents import loaduserFeeds
        result=loaduserFeeds(userid,page)

        from sys import exc_info
        try:
            # fetch feeds by using userid here
            return dict(rc=200, msg="Fetch Feeds Successful", feeds=result)
        except:
            print (exc_info())
            resp.status_code = 400
            return dict(rc=400, msg="Fetch Feeds Error: unknown error")

    # search
    @view_config(route_name='search', request_method='OPTIONS')
    def search_options(self):
        resp = self.request.response
        return resp

    @view_config(route_name='search', request_method='GET')
    def search(self):
        request = self.request
        resp = self.request.response
        keyword = self.request.params.get('keyword', 'No word Provided')
        if (keyword=='No word Provided'):
            return dict(rc=200, msg="No keyword")
        else:
            from ProductSearch import SearchProductByKeyword
            result=SearchProductByKeyword(keyword)
            #dict(name=product._productName,price=product._price,url=product._webUrl, brand=product._brand)
            return dict(rc=200, msg="result", results=result)

        return dict(rc=200, msg="result")


conn_err_msg = """
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_lookchic_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
