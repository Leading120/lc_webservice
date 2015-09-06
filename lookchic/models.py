# -*- coding: utf-8 -*-
import sys
from sqlalchemy import Table, ForeignKey
from sqlalchemy import *
from sqlalchemy import Column, Integer, String, DateTime, func, FLOAT
from sqlalchemy.orm import relationship
import pytz
from mysql.connector import MySQLConnection, Error
from sys import exc_info

from dbconnection import db_uri,userDB_engine, productDB_engine, Session, conn, productConn, Base

class Userinfo(Base):
    __tablename__ = 'userinfo'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Username = Column(String, primary_key=True, default="")
    Email = Column(String, primary_key=True, default="")
    Password = Column(String(50))
    Salt = Column(VARBINARY(50))
    Active = Column(Integer)
    LastLoginTime = Column(DateTime)


class Userdetails(Base):
    __tablename__ = 'userdetails'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('userinfo.ID'))
    AliasName = Column(String(50))
    Country = Column(String(50))
    About_me = Column(String(150))
    AgeRange = Column(Integer, ForeignKey('AgeRange.ID'))
    InterestArea = Column(Integer, ForeignKey('InterestArea.ID'))
    Update_Date = Column(DateTime)
    Height=Column(Integer)
    Weight=Column(FLOAT)
    Brithday=Column(DateTime)
    Gender=Column(INTEGER)
    Occupation=Column(String(255))



class AgeRange(Base):
    __tablename__ = 'agerange'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    AgeRangeStart = Column(Integer)
    AgeRangeEnd = Column(Integer)


class Tags(Base):
    __tablename__ = 'tags'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    TagName = Column(String)
    Tag_Text = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    TAddDate = Column(DateTime)


class InterestArea(Base):
    __tablename__ = 'interestarea'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String)
    Description = (String)


class RelationType(Base):
    __tablename__ = 'relationtype'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    RelationType = Column(String)


class PropertyType(Base):
    __tablename__ = 'propertytype'
    PropertyTypeID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String)
    DataType = Column(String)


class PhotoInfo(Base):
    __tablename__ = 'photoinfo'
    PhotoID = Column(Integer, primary_key=True)
    PhotoProperty = Column(Integer, ForeignKey('PropertyType.PropertyTypeID'))
    Value = Column(String)


class Photos(Base):
    __tablename__ = 'photos'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    UID = Column(Integer)
    Name = Column(String)
    Description = Column(String)
    Path = Column(String)
    Filename = Column(String)
    PAddDate = Column(DateTime)

    def create_activity(self):
        from stream_framework.activity import Activity
        from verbs import Pin as PinVerb, AddPhoto
        activity = Activity(
            actor=self.UID,
            verb=AddPhoto,
            object=self.ID,
            # target=self.influencer_id,
            time=self.PAddDate,
            # time=make_naive(self.created_at, pytz.utc),
            extra_context=dict(item_id=self.ID)
        )

        return activity

        # UserID=Column(Integer,ForeignKey('UserInfo.ID'))


class PhotoTag(Base):
    __tablename__ = 'PhotoTag'
    PhotoID = Column(Integer, primary_key=True)
    TagId = Column(Integer, primary_key=True)


class Likes(Base):
    __tablename__ = 'likes'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('userInfo.ID'))
    PhotoID = Column(Integer, ForeignKey('photos.ID'))


class Comments(Base):
    __tablename__ = 'comments'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Context = Column(String)
    UserID = Column(Integer, ForeignKey('UserInfo.ID'))
    PhotoID = Column(Integer, ForeignKey('Photos.ID'))
    AddDate = Column(DateTime)


class ProfilePhoto(Base):
    __tablename__ = 'profilephoto'
    UserID = Column(Integer, ForeignKey('userInfo.ID'), primary_key=True)
    PhotoID = Column(Integer, ForeignKey('photos.ID'), primary_key=True)


class UserRelation(Base):
    __tablename__ = 'userrelation'
    # Actor
    User1ID = Column(Integer, ForeignKey('userinfo.ID'), primary_key=True)
    # Target
    User2ID = Column(Integer, ForeignKey('userinfo.ID'), primary_key=True)
    # RelationType
    Type = Column(Integer, ForeignKey('relationtype.ID'))


class Pin(Base):
    __tablename__ = 'pin'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('userinfo.id'))
    item_id = Column(Integer, ForeignKey('photos.id'))
    # board_id = Column(Integer, ForeignKey('board.id'))
    # influencer_id=Column(Integer,ForeignKey('userinfo.id'))
    message = Column(String)
    created_at = Column(DateTime, default=func.now())

    def create_activity(self):
        from stream_framework.activity import Activity
        from verbs import Pin as PinVerb
        activity = Activity(
            actor=self.user_id,
            verb=PinVerb,
            object=self.item_id,
            # target=self.influencer_id,
            time=self.created_at,
            # time=make_naive(self.created_at, pytz.utc),
            extra_context=dict(item_id=self.item_id)
        )

        return activity

#region: User Operation

def AddNewUser(Username, Pword, salt, email):
    from datetime import datetime
    try:
        cursor=conn.cursor()
        timeFormat='%Y-%m-%d %H:%M:%S'
        args = [Username,Pword, 0, salt, email, datetime.utcnow().strftime(timeFormat),0]
        result_args = cursor.callproc('uspAddUser', args)
        conn.commit()
        cursor.close()
        #print(result_args[6])
        return result_args[6]
    except Error as e:
        conn.rollback()
        cursor.close()
        print(e)
    return 0


def AddUserDetail(UserId, UserNickName, Country, Aboutme, Age, InterestArea,height,weight,isF,occupation):
    from datetime import datetime
    sess = Session()
    birthFormat='%Y-%m-%d'
    ageRange = sess.query(AgeRange).filter(AgeRange.AgeRangeStart < Age and AgeRange.AgeRangeEnd < Age)
    detail = Userdetails(UserID=UserId, AliasName=UserNickName, Country=Country, About_me=Aboutme,
                         Agerange=ageRange[0].ID, InterestArea=InterestArea, Update_Date=datetime.utcnow(),
                         Height=height, Weight=weight, Brithday=datetime.strftime(birthFormat),Gender=(isF),
                         Occupation=occupation)
    try:
        sess.add(detail)
        sess.commit()
    except:
        print "Unexpect Exception:", sys.exc_info()[0]
        sess.rollback()
        sess.close()
        return False
    sess.close()
    return True


def get_user_follower_ids_fromDB(uid):
    if uid == 0:
        return None
    cursor=conn.cursor()
    try:
        sql=("select user1ID from userrelation"
             " where User2ID=%(uid)s")
        data={"uid":uid}
        cursor.execute(sql,data)
        result=cursor.fetchall()
    except:
        print (exc_info())
    finally:
        cursor.close()
    if result is not None and len(result)>0:
        return result

def checkAvailableUsername(username):
    if (username is None):
        return False
    else:
        try:
            cursor=conn.cursor()
            sql="select username in userdb.userinfo where username ==%(user)s "
            data={"user":username}
            cursor.execute(sql,data)
            if (cursor.rowcount>0):
                cursor.close()
                return False
            else:
                cursor.close()
                return true;
        except:
            print(exc_info())
            cursor.close()
            return False;

def CheckUser(Username, Pword):
    checksess = Session();
    user = checksess.query(Userinfo).filter(Userinfo.Username == Username).all()
    checksess.commit()
    checksess.close()

    if len(user) > 0:
        if (Pword == user[0].Password):
            return True
        else:
            return False
    else:
        return False
    return False
#endregion


#region: Photo and Comments

def addphoto(UID, PName, PDesc, PPath, FiName):
    newCursor = conn.cursor();
    try:
        args = [UID, PName, PDesc, PPath, FiName, 0]
        result_args = newCursor.callproc('uspAddPhoto', args)
        conn.commit()
        newCursor.close()
        return (result_args[5])
    except Error as e:
        conn.rollback()
        print(e)
        newCursor.close()
    return 0;


# addphoto('TestInsert1','','TestPath:','')

def addcomment(CText, UID, PID):
    if UID==0 or PID==0 or CText is None:
        return
    if len(CText) <1:
        return
    cursor = conn.cursor()
    try:

        args = [CText, UID, PID, 0]
        result_args = cursor.callproc('uspAddComment', args)
        conn.commit()
        #print(result_args[4])
        return result_args[3]
    except Error as e:
        conn.rollback()
        print(e)
    finally:
        cursor.close()

def removeComment(userid, pic_id, comment_id):
    if (userid<1 or pic_id<1):
        return False;
    try:
        cursor=conn.cursor()
        sql="Delete FROM userdb.comments where ID=%(c_id)s"
        data={'c_id':comment_id}
        cursor.execute(sql,data)
        #result=cursor.fetchall()
        cursor.close()
        return True
    except:
        print (exc_info())
        return False
    return False

def AddLike(UID, PID):
    if UID==0 or PID==0:
        return
    try:
        cursor = conn.cursor()
        args = [UID, PID, 0]
        result_args = cursor.callproc('uspAddLike', args)
        conn.commit()
        return True
        # print(result_args[3])
    except Error as e:
        conn.rollback()
        print(e)
        return False
    finally:
        cursor.close()
        # conn.close()

def UnlikePic(UID,PID):
    if UID==0 or PID==0:
        return False
    try:
        cursor = conn.cursor()
        args = [UID, PID, 0]
        result_args = cursor.callproc('uspAddLike', args)
        conn.commit()
        cursor.close()
        return True
        # print(result_args[3])
    except Error as e:
        conn.rollback()
        print(e)
        cursor.close()
        return False

#endregion

def AddUserRelation(u1id, u2id, Rtype):
    if u1id ==0 or u2id==0:
        return
    success=False
    try:
        cursor = conn.cursor()
        args = [u1id, u2id, Rtype, 0]
        result_args = cursor.callproc('uspAddUserRelation', args)
        conn.commit()
        # print(result_args[3])
        success=True
    except Error as e:
        conn.rollback()
        print(e)
    finally:
        cursor.close()
        return success


def GetPassword(uid):
    try:
        cursor = conn.cursor()
        args = [uid, 0]
        result_args = cursor.callproc('uspGetPassword', args)
        #print(result_args[1])
        return result_args[1]
    except Error as e:
        print(e)
    finally:
        cursor.close()
        # conn.close()

def getFeedsFromDb(uid):
    result=list()
    if uid ==0:
        return None
    try:
        cursor = conn.cursor()
        sql=("select photos.id as PhotoId from photos where photos.uid in (select userrelation.user2ID from userrelation"
             " where User1ID=%(uid)s) order by PAddDate desc")
        data={"uid":uid}
        cursor.execute(sql,data)
        rows=cursor.fetchall()
        cursor.close()
        for row in rows:
            if row[0] is not None:
                result.append(row[0])
        return result
    except:
            print (exc_info())

def searchProduct(keyword):
    try:
        cursor=productConn.cursor()
        sql=("select ID, Brand_id, ProductType_id, Name from productdb.Products where Brand_ID in (select Brand_ID from productdb.Brands where BrandName like CONCAT('%', %(key)s, '%'))"
						"or	ProductType_ID in (select ProductType_ID from productdb.productTypes where TypeName like concat('%',%(key)s,'%')"
                        "or  Name like concat('%',%(key)s,'%'))")
        data={"key":keyword}
        cursor.execute(sql,data)
        result=cursor.fetchall()
        cursor.close()
        if (result is not None):
            return result
    except:
        print(exc_info())
        cursor.close()

def get_product_detail(id):
    if (id<1):
        return
    try:
        cursor=productConn.cursor()
        sql=("select Value as price from Productdb.productdetail where ProductID=%(pid)s")
        data={"pid":id}
        cursor.execute(sql,data)
        result=cursor.fetchall()
        cursor.close()
        return result;
    except:
        print (exc_info())
        cursor.close()

def get_product_brand(id):
    if (id<1):
        return
    try:
        cursor=productConn.cursor()
        sql=("select brandname from productdb.brands where brand_id=%(bid)s")
        data ={"bid":id}
        cursor.execute(sql,data)
        result=cursor.fetchall()
        cursor.close()
        return result
    except:
        print (exc_info())
        cursor.close()

def get_product_link(id):

    if (id<1):
        return
    try:
        cursor=productConn.cursor()
        sql=("select Url from Productdb.links where ProductID=%(pid)s")
        data={"pid":id}
        cursor.execute(sql,data)
        result=cursor.fetchall()
        cursor.close()
        return result;
    except:
        print (exc_info())
        cursor.close()

def addPhotoFavoriteToDB(userid, photoid):
    cursor=conn.cursor()
    from datetime import datetime
    try:
        if cursor is not None:
            sql = ("select * from favorite where Userid=%(uid)s and Photoid=%(pic)s")
            data={'uid':userid, 'pic':photoid}
            cursor.execute(sql,data)
            result=cursor.fetchall()
            if (len(result)>0):
                return true
            else:
                sql=("Insert into favorite "
                     "Values(%(uid)s, %(pic)s, %(time)s)")
                data={'uid':userid, 'pic':photoid,'time':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                cursor.execute(sql,data)
                result=cursor.rowcount
                cursor.close()
                if (result>0):
                    return true
                else:
                    return false;
    except:
        print (exc_info())
        cursor.close()
        return false

#addPhotoFavoriteToDB(2,91)


# a=sess.query(Photos).all()
# output="PhotoID:{ID}; Description:{Description}"
# print  output.format(ID=a[0].ID, Description=a[0].Description)
#
# if CheckUser('LD','120'):
#     print 'logined'
# else:
#     print 'wrong'
#
# if CheckUser('LD','000'):
#     print 'Login'
# else:
#     print 'wrong'

'''
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    password = Column(String)


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    image = Column(String)
    source_url = Column(String)
    message = Column(String)
    pin_count = Column(Integer, default=0)
'''

'''
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    image = models.ImageField(upload_to='items')
    source_url = models.TextField()
    message = models.TextField(blank=True, null=True)
    pin_count = models.IntegerField(default=0)
'''
    # class Meta:
    #    db_table = 'pinterest_example_item'

'''
class Board(Base):
    __tablename__ = 'board'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String)
    description = Column(String)
    slug = Column(String)
'''

'''
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField()
'''

'''
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    item = models.ForeignKey(Item)
    board = models.ForeignKey(Board)
    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='influenced_pins')
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
'''

'''
class Follow(Base):


    __tablename__ = 'Follow'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey('user.id'))
    target = Column(Integer, ForeignKey('user.id'))
    created_at = Column(DateTime, default=func.now())
'''

'''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='following_set')
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='follower_set')
    created_at = models.DateTimeField(auto_now_add=True)
'''

'''
stmt = text("""select *
               from test_usertable
               where username=:username""")
            # s is instance of Session() class factory
            '''
# results = sess.execute(stmt, params=dict(username=username))


##result=AddNewUser('username','123123','w13se123','asdf@asdf.com')
#print result


#
# cnx = mysql.connector.connect(user="allen",password="yao0702",host="localhost",database="userdb")
# cursor = cnx.cursor()
# cursor.callproc("uspTest_usertable",args=("allen5","allenTest"))
# #cursor.execute("select * from test_usertable")
# #cursor.fetchall()
# cnx.commit()

# results = exec_procedure(sess,"uspTest_usertable",['allen2','allenpw'], **t)
# results = exec

# sess.execute("select * from test_usertable")
# Base.metadata.create_all(engine)