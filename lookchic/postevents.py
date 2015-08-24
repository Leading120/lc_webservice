__author__ = 'zoe'
from sys import exc_info


def addphotoEvent(userid, RelativePath, Saved_file_name):
    if (userid > 0 & RelativePath != '' & Saved_file_name != ''):
        from models import addphoto
        pic_id = addphoto(userid, 'photoname', 'photoDescription', RelativePath, Saved_file_name)
        from pin_feed import User
        user_pin = User(userid)
        # user_pin.add_pic(pic_id)
        from feed_managers import manager
        manager.add_user_activity(userid, user_pin.add_pic(pic_id))
        feeds = manager.get_feeds(1)['normal']
        print (feeds[:])
        return pic_id
    else:
        return 0


def adduserComment(userid, pic_id, comment):
    from models import addcomment
    if (userid > 0 and pic_id > 0 and comment != ''):
        try:
            result = addcomment(comment, userid, pic_id)
            return result
        except:
            print (exc_info())
            return 0

def removeuserComment(userid, pic_id,comment_id):
    from models import removeComment
    if (userid>0 and pic_id>0):
        try:
            result=removeComment(userid, pic_id,comment_id)
            return result
        except:
            print (exc_info())
            return False

def loaduserFeeds(userid, page):
    result = list()
    from models import getFeedsFromDb
    temp_list = getFeedsFromDb(userid)
    print temp_list
    if page == 1:
        from enrichlist import UserContent, richUserPictures
        user = UserContent(userid)
        content = richUserPictures(user.Pop())
        for pic in content.pics:
            feed = dict(username=pic.pic_userName, url=pic.pic_url, time=pic.pic_time)
            result.append(feed)
    else:
        from models import getFeedsFromDb
        from enrichlist import UserContent, richUserPictures
        db_feedList = getFeedsFromDb(userid)
        content = richUserPictures(db_feedList)
        for pic in content.pics:
            feed = dict(username=pic.pic_userName, url=pic.pic_url, time=pic.pic_time)
            result.append(feed)
    return result


result=removeuserComment(1,87,2)
print result