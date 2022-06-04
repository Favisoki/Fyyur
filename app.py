#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
import os
import logging
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  venues = Venue.query.order_by(db.desc(Venue.created_at)).all()
  artists = Artist.query.order_by(db.desc(Artist.created_at)).all()
  return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  data=[]
  #get the distinct states and cities
  results = Venue.query.distinct(Venue.city, Venue.state).all()
  for result in results:
    city_state = {
      'city': result.city,
      'state': result.state
    }
    venues = Venue.query.filter_by(city=result.city, state=result.state).all()

    #format every venue
    venues_formatted = []
    for venue in venues:
      venues_formatted.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
      })
    city_state['venues']  = venues_formatted
    data.append(city_state)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '')
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={}
  venues = list(Venue.query.filter(
    Venue.name.ilike(f'%{search_term}%') | Venue.state.ilike(f'%{search_term}%') | Venue.city.ilike(f'%{search_term}%')
  ).all())
  response['count'] = len(venues)
  response['data'] = []

  for venue in venues:
    curr_venue = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
    }
    response['data'].append(curr_venue)

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue=Venue.query.get(venue_id)
  # convert the genre string to array
  setattr(venue, 'genres', venue.genres.split(','))

  #get the past shows
  past_shows = list(filter(lambda show: show.start_time < datetime.now(), venue.shows))
  curr_shows = []
  for show in past_shows:
    curr = {}
    curr['artist_name'] = show.artists.name
    curr['artist_id'] = show.artists.id
    curr['artist_image_link'] = show.artists.image_link
    curr['start_time'] = show.start_time
    curr_shows.append(curr)
  
  setattr(venue, 'past_shows', curr_shows)
  setattr(venue, 'past_shows_count', len(past_shows))

  #upcoming shows
  upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), venue.shows))
  curr_shows = []
  for show in curr_shows:
    curr = {}
    curr['artist_name'] = show.artists.name
    curr['artist_id'] = show.artists.id
    curr['artist_image_link'] = show.artists.image_link
    curr['start_time'] = show.start_time
    curr_shows.append(curr)
  
  setattr(venue, 'upcoming_shows', curr_shows)
  setattr(venue, 'upcoming_shows_count', len(upcoming_shows))

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)

  if form.validate():
    try:
      new_venue = Venue(
        name = form.name.data,
        city = Form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres=",".join(form.genres.data), # convert array to string separated by commas
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data,
        website=form.website.data
      )
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    print(form.errors)
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
  
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id=venue_id)
    db.session.selete(venue)
    db.session.sommit()
    flash("Venue " + venue.name + " was deleted successfully!")
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("Venue was not deleted successfully!")
  finally:
    db.session.close()

  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists=db.session.query(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=artists)
  #data=[{
  #  "id": 4,
  #  "name": "Guns N Petals",
  #}, {
  #  "id": 5,
  #  "name": "Matt Quevedo",
  #}, {
  #  "id": 6,
  #  "name": "The Wild Sax Band",
  #}]
  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = json(Artist.query.all())
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(Artist.id)
  setattr(artist, 'genres', artist.genres.split(','))

  # get past shows
  past_shows = list(filter(lambda show: show.start_time < datetime.now(), artist.shows))
  curr_shows = []
  for show in past_shows:
      curr = {}
      curr["venue_name"] = show.venues.name
      curr["venue_id"] = show.venues.id
      curr["venue_image_link"] = show.venues.image_link
      curr["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

      curr_shows.append(curr)

  setattr(artist, 'past_shows', curr_shows)
  setattr(artist, 'past_shows_count', len(past_shows))

  # get upcoming shows
  upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), artist.shows))
  curr_shows = []
  for show in upcoming_shows:
      curr = {}
      curr["venue_name"] = show.venues.name
      curr["venue_id"] = show.venues.id
      curr["venue_image_link"] = show.venues.image_link
      curr["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

      curr_shows.append(curr)

  setattr(artist, 'upcoming_shows', curr_shows)
  setattr(artist, 'upcoming_shows_count', len(upcoming_shows))

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  form.genres.data = artist.genres.split(',')
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  if form.validate():
      try:
          artist = Artist.query.get(artist_id)

          artist.name = form.name.data
          artist.city=form.city.data
          artist.state=form.state.data
          artist.phone=form.phone.data
          artist.genres=",".join(form.genres.data) # convert array to string separated by commas
          artist.facebook_link=form.facebook_link.data
          artist.image_link=form.image_link.data
          artist.seeking_venue=form.seeking_venue.data
          artist.seeking_description=form.seeking_description.data
          artist.website=form.website.data

          db.session.add(artist)
          db.session.commit()
          flash("Artist " + artist.name + " was successfully edited!")
      except:
          db.session.rollback()
          print(sys.exc_info())
          flash("Artist was not edited successfully.")
      finally:
          db.session.close()
  else:
      print(form.errors)
      flash("Artist was not edited successfully.")

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  form.genres.data = venue.genres.split(',')

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
    
  if form.validate():
      try:
          venue = Venue.query.get(venue_id)

          venue.name = form.name.data
          venue.city=form.city.data
          venue.state=form.state.data
          venue.address=form.address.data
          venue.phone=form.phone.data
          venue.genres=",".join(form.genres.data) # convert array to string separated by commas
          venue.facebook_link=form.facebook_link.data
          venue.image_link=form.image_link.data
          venue.seeking_talent=form.seeking_talent.data
          venue.seeking_description=form.seeking_description.data
          venue.website=form.website.data

          db.session.add(venue)
          db.session.commit()

          flash("Venue " + form.name.data + " edited successfully")
          
      except Exception:
          db.session.rollback()
          print(sys.exc_info())
          flash("Venue was not edited successfully.")
      finally:
          db.session.close()
  else: 
      print(form.errors)
      flash("Venue was not edited successfully.")
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  if form.validate():
    try:
      new_artist = Artist(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          genres=",".join(form.genres.data),
          image_link=form.image_link.data,
          facebook_link=form.facebook_link.data,
          website=form.website.data,
          seeking_venue=form.seeking_venue.data,
          seeking_description=form.seeking_description.data,
      )
      db.session.add(new_artist)
      db.session.commit()
      flash("Artist " + request.form["name"] + " was successfully listed!")
    except Exception:
      db.session.rollback()
      flash("Artist was not successfully listed.")
    finally:
      db.session.close()
  else:
    print(form.errors)
    flash("Artist was not successfully listed.")

  return redirect(url_for("index"))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]

  shows = Show.query.all()
  for show in shows:
    curr = {}
    curr['venue_id'] = show.venues.id
    curr["venue_name"] = show.venues.name
    curr["artist_id"] = show.artists.id
    curr["artist_name"] = show.artists.name
    curr["artist_image_link"] = show.artists.image_link
    curr["start_time"] = show.start_time

    data.append(curr)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm(request.form)
    
  if form.validate():
      try:
          new_show = Show(
              artist_id=form.artist_id.data,
              venue_id=form.venue_id.data,
              start_time=form.start_time.data
          )
          db.session.add(new_show)
          db.session.commit()
          flash('Show was successfully listed!')
      except Exception:
          db.session.rollback()
          print(sys.exc_info())
          flash('Show was not successfully listed.')
      finally:
          db.session.close()
  else:
      print(form.errors)
      flash('Show was not successfully listed.')
      
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
'''
if __name__ == '__main__':
    app.run()
'''

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
