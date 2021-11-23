#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from werkzeug import datastructures
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import Show, Artist, Venue, db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
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

def convertwtf(val):
  bool = True if val == 'y' else False
  return bool

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  query = db.session.query(Venue).all()

  for venue in db.session.query(Venue).distinct(Venue.city):
    data.append({
        'city': venue.city,
        'state': venue.state,
        'venues': []
      })

  for city in range(len(data)):    
    for venue in query:
      if venue.city == data[city]['city']:  
        data[city]['venues'].append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
        })
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search = db.session.query(Venue).filter(Venue.name.ilike(f"%{request.form.get('search_term', '')}%"))
  data = []

  for venue in search:
    data.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
    })
  
  response = {
    "count": search.count(),
    "data": data
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  
  venue = db.session.query(Venue).get(venue_id)
  past_shows = db.session.query(Show).filter(Show.venue_id == venue_id, Show.start_time < datetime.now())
  upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue_id, Show.start_time > datetime.now())
  PSdata = []
  USdata = []

  for show in past_shows:
    PSdata.append({
      'artist_id': show.artist_id,
      'artist_name': db.session.query(Artist).get(show.artist_id).name,
      'artist_image_link': db.session.query(Artist).get(show.artist_id).image_link,
      'start_time': str(show.start_time)
    })

  for show in upcoming_shows:
    USdata.append({
      'artist_id': show.artist_id,
      'artist_name': db.session.query(Artist).get(show.artist_id).name,
      'artist_image_link': db.session.query(Artist).get(show.artist_id).image_link,
      'start_time': str(show.start_time)
    })

  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website_link,
    'facebook_link': venue.facebook_link,
    'image_link': venue.image_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'past_shows': PSdata,
    'upcoming_shows': USdata,
    'past_shows_count': len(PSdata),
    'upcoming_shows_count': len(USdata)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  new_venue = Venue(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    phone = request.form['phone'],
    address = request.form['address'],
    genres = request.form.getlist('genres'),
    image_link = request.form['image_link'],
    facebook_link = request.form['facebook_link'],
    website_link = request.form['website_link'],
    seeking_talent = convertwtf(request.form.get('seeking_talent', False)),
    seeking_description = request.form['seeking_description']
  )
  
  try:
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!') 
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/remove', methods=['POST'])
def delete_venue(venue_id):

  selected_venue = db.session.query(Venue).get(venue_id)

  try:
    db.session.delete(selected_venue)
    db.session.commit()
    flash(f'Venue {selected_venue.name} was successfully removed!')
  except:
    db.session.rollback()
    flash(f'An error occurred. Venue {selected_venue.name} could not be removed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  query = db.session.query(Artist).all()
  
  for artist in query:
    data.append({
      'id': artist.id,
      'name': artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search = db.session.query(Artist).filter(Artist.name.ilike(f"%{request.form.get('search_term', '')}%"))
  data = []

  for artist in search:
    data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': db.session.query(Show).filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).count()
    })
  
  response = {
    "count": search.count(),
    "data": data
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  
  artist = db.session.query(Artist).get(artist_id)
  past_shows = db.session.query(Show).filter(Show.artist_id == artist_id, Show.start_time < datetime.now())
  upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist_id, Show.start_time > datetime.now())
  PSdata = []
  USdata = []

  for show in past_shows:
    PSdata.append({
      'venue_id': show.venue_id,
      'venue_name': db.session.query(Venue).get(show.venue_id).name,
      'venue_image_link': db.session.query(Venue).get(show.venue_id).image_link,
      'start_time': str(show.start_time)
    })

  for show in upcoming_shows:
    USdata.append({
      'venue_id': show.venue_id,
      'venue_name': db.session.query(Venue).get(show.venue_id).name,
      'venue_image_link': db.session.query(Venue).get(show.venue_id).image_link,
      'start_time': str(show.start_time)
    })

  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'website': artist.website_link,
    'facebook_link': artist.facebook_link,
    'past_shows': PSdata,
    'upcoming_shows': USdata,
    'past_shows_count': len(PSdata),
    'upcoming_shows_count': len(USdata)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = db.session.query(Artist).get(artist_id)
  form = ArtistForm(obj=artist)

  artist_attributes = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website_link,
    'facebook_link': artist.facebook_link,
    'image_link': artist.image_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description
  }

  return render_template('forms/edit_artist.html', form=form, artist=artist_attributes)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = db.session.query(Artist).get(artist_id)

  artist.name = request.form['name']
  artist.genres = request.form.getlist('genres')
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.website_link = request.form['website_link']
  artist.facebook_link = request.form['facebook_link']
  artist.image_link = request.form['image_link']
  artist.seeking_venue = convertwtf(request.form.get('seeking_venue', False))
  artist.seeking_description = request.form['seeking_description']

  try:
    db.session.commit()
    flash(f'Artist {artist.name} was successfully updated!')
  except:
    db.session.rollback()
    flash(f'An error occurred. Artist {artist.name} could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = db.session.query(Venue).get(venue_id)
  form = VenueForm(obj=venue)
  venue_attributes={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }

  return render_template('forms/edit_venue.html', form=form, venue=venue_attributes)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = db.session.query(Venue).get(venue_id)

  venue.name = request.form['name']
  venue.genres = request.form.getlist('genres')
  venue.address = request.form['address']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.phone = request.form['phone']
  venue.website_link = request.form['website_link']
  venue.facebook_link = request.form['facebook_link']
  venue.image_link = request.form['image_link']
  venue.seeking_venue = convertwtf(request.form.get('seeking_venue', False))
  venue.seeking_description = request.form['seeking_description']

  try:
    db.session.commit()
    flash(f'Venue {venue.name} was successfully updated!')
  except:
    db.session.rollback()
    flash(f'An error occurred. Venue {venue.name} could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form

  new_artist = Artist(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    phone = request.form['phone'],
    genres = request.form.getlist('genres'),
    image_link = request.form['image_link'],
    facebook_link = request.form['facebook_link'],
    website_link = request.form['website_link'],
    seeking_venue = convertwtf(request.form.get('seeking_venue', False)),
    seeking_description = request.form['seeking_description']
  )

  try:
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!') 
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Remove Artist
#  ----------------------------------------------------------------

@app.route('/artists/<artist_id>/remove', methods=['POST'])
def delete_artist(artist_id):
  selected_artist = db.session.query(Artist).get(artist_id)

  try:
    db.session.delete(selected_artist)
    db.session.commit()
    flash(f'Artist {selected_artist.name} was successfully removed!')
  except:
    db.session.rollback()
    flash(f'An error occurred. Artist {selected_artist.name} could not be removed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  data = []
  query = db.session.query(Show).all()

  for show in query:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': db.session.query(Venue).get(show.venue_id).name,
      'artist_id': show.artist_id,
      'artist_name': db.session.query(Artist).get(show.artist_id).name,
      'artist_image_link': db.session.query(Artist).get(show.artist_id).image_link,
      'start_time': show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form

  selected_venue = request.form['venue_id']
  selected_artist = request.form['artist_id']
  start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%d %H:%M:%S')

  new_show = Show(
    artist_id = selected_artist,
    venue_id = selected_venue,
    start_time = start_time
  )
  
  try:  
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
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
if __name__ == '__main__':
    app.run(debug='on')

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
