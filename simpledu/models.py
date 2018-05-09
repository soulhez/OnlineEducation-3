# coding:utf-8
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask import url_for

# 注意这里不再传app了，为什么？
# 因为要根据配置动态创建Flask app，官方推荐做法是使用一个工厂函数专门负责创建app
db = SQLAlchemy()


class Base(db.Model):
    """所有model的一个基类，默认添加了时间戳 """
    # 表示不要把这个类当作Model类
    __abstract__ = True
    # 设置了 default 和 onupdate 这两个时间戳，都不需要自己维护
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                    default=datetime.utcnow,
                    onupdate=datetime.utcnow)


class User(Base,UserMixin):
    __tablename__ = 'user'
    
    # 用数值表示角色，方便判断是否有权限，比如有个操作要角色为员工
    # 及以上权限的用户才可以做，那么只要判断 user,role >= ROLE_STAFF
    # 即可，数值之间设置了 10 的间隔是为了方便以后加入其它角色
    ROLE_USER = 10
    ROLE_STAFF = 20
    ROLE_ADMIN = 30

    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(32),unique=True,index=True,nullable=False)
    email = db.Column(db.String(64),unique=True,index=True,nullable=False)

    # 默认情况下，sqlalchemy 会以字段名来命名列，但是这里是 _password,所以明确指定数据库表列名为 password
    _password = db.Column('password',db.String(256),nullable=False)
    role = db.Column(db.SmallInteger,default=ROLE_USER)
    job = db.Column(db.String(64))
    publish_courses = db.relationship('Course')

    def __repr__(self):
        return '<User:{}>'.format(self.username)

    @property
    def password(self):
        """ Python 风格的 getter """
        return self._password

    @password.setter
    def password(self,orig_password):
        """
        Python 风格的setter，这样设置的话，
        user.password 就会自动为 password 生成哈希值存入_paaword字段 
        """
        self._password = generate_password_hash(orig_password)

    def check_password(self,password):
        """
        判断用户输入的密码和存储的 hash密码是否相等
        """
        return check_password_hash(self._password,password)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_staff(self):
        return self.role == self.ROLE_STAFF


class Course(Base):
    __tablename__ = 'course'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(128),unique=True,index=True,nullable=False)
    # ondelete='CASCASE' 表示如果用户被删除了，那么作者是他的课程也会被及联删除
    # 课程描述信息
    description = db.Column(db.String(256))
    # 课程图片url地址
    image_url = db.Column(db.String(256))
    author_id = db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'))
    author = db.relationship('User',uselist=False)
    chapters = db.relationship('Chapter')
    
    @property
    def url(self):
        return url_for('course.detail',course_id=self.id)
    
    def __repr__(self):
        return '<Course:{}>'.format(self.name)

class Chapter(Base):
    __tablename__='chapter'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(128),unique=True,index=True)
    description = db.Column(db.String(256))
    # 课程视频 url 地址
    video_url = db.Column(db.String(256))
    # 视频时长，格式：'30:15','1:15:20'
    video_duration = db.Column(db.String(24))
    # 关联到课程，并且客户曾删除及联删除相关章节
    course_id = db.Column(db.Integer,db.ForeignKey('course.id',ondelete='CASCADE'))
    course = db.relationship('Course',uselist=False)

    @property
    def url(self):
        return url_for('course.chapter',course_id=self.course.id,chapter_id=self.id)

    def __repr__(self):
        return '<Chapter:{}>'.format(self.name)


class Live(Base):
    __tablename__='live'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(128),unique=True,index=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'))
    user = db.relationship('User',uselist=False)

    def __repr__(self):
        return '<Live:{}>'.format(self.name)
