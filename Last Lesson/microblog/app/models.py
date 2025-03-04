from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

followers = sa.Table('followers',
                     db.metadata, 
                     sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
                     sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True))

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime, default=lambda: datetime.now())

    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')

    following:so.WriteOnlyMapped['User'] = so.relationship('User', 
                                                           secondary=followers, primaryjoin=(followers.c.follower_id == id), 
                                                           secondaryjoin=(followers.c.followed_id == id), back_populates='followers')

    followers: so.WriteOnlyMapped['User'] = so.relationship('User',
                                                              secondary=followers, primaryjoin=(followers.c.followed_id == id),
                                                              secondaryjoin=(followers.c.follower_id == id), back_populates='following')
    def __repr__(self):
        return '<User {} {}>'.format(self.username, self.email)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self,user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self,user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self,user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(self.followers.select().subquery())
        print(query)
        return db.session.scalar(query)
    
    def following_count(self):
        query = sa.select(sa.func.count()).select_from(self.following.select().subquery())
        return db.session.scalar(query)
    
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)

        return sa.select(Post).join(Post.author.of_type(Author)
            ).join(Author.followers.of_type(Follower), isouter=True
            ).where(sa.or_(Follower.id == self.id, Author.id == self.id)
            ).group_by(Post).order_by(Post.timestamp.desc())


        
@login.user_loader
def load_user(id):

    return db.session.get(User, int(id))

class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[Optional[str]] = so.mapped_column(sa.DateTime)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
