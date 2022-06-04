#----------------------------------------------------------------------------#
# Imports

import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(), nullable=False)
    website = db.Column(db.String(), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(400), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    shows = db.relationship('Show', backref='venues', lazy=True)


    def __repr__(self):
      return f'<Venue id={self.id} name={self.name} city={self.city} state={self.state}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.utcnow,nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True)
    show_id = db.Column(db.Integer, db.ForeignKey('Show.id'), nullable=True)
    shows = db.relationship('Show', backref='artists', lazy=True)



class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key = True, nullable=False)
  name = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(), nullable=False)
  state = db.Column(db.String(), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=True)
  start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

  def __repr__(self):
    return f'<Show id={self.id} venue_id={self.venue_id} artist_id={self.artist_id} statr_time={self.start_time}>'
