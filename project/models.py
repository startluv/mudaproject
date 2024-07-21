from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import MetaData
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)


class User(db.Model,UserMixin):
    __tablename__  = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),nullable=False,unique=True) #사용자 이름
    email = db.Column(db.String(30),nullable=True) #사용자 이메일
    pw = db.Column(db.String(15),nullable=False) #사용자 패스워드
    
class Diary(db.Model):
    __tablename__ = "diary"
    id=db.Column(db.Integer,primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_diary_user_id'))    
    date = db.Column(db.Text())
    content = db.Column(db.Text(),nullable=False)
    emotiontext=db.Column(db.String(20))
    emotionimage_path = db.Column(db.String(255))
    #db는 이미지를 저장하기에 좋은 매체가 아니다. 그래서, 이미지를 폴더에 저장하고, 그 경로를 불러오는게 좋다고 한다.
    music = db.Column(db.Text())
    #music 도 이걸 어떻게 구현하지?
    
    
    
    
    