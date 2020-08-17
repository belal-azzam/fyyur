#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import time
from datetime import datetime
import json
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for
)
from .models import Artist
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from app.forms import *
from flask_migrate import Migrate
from app.models import db,Artist,Venue,Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
db.init_app(app)
moment = Moment(app)
app.config.from_object('app.config')
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

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
  venues = Venue.query.all()
  cityVenues = {}
  for venue in venues:
    key = venue.city + venue.state
    if key not in cityVenues:
      cityVenues[key] = {"city": venue.city, "state": venue.state, 'venues': []}  
    cityVenues[key]['venues'].append(venue)
    
  data = []
  for cityVenue in cityVenues:
    data.append(cityVenues[cityVenue])
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).paginate()
  response={
    "count": result.total,
    "data": result.items
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  dataItem = {
    "id": venue.id,
    "name": venue.name,
    "genres":  venue.genres_list,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "facebook_link": venue.facebook_link,
    "image_link": venue.image_link,
    "upcoming_shows": [],
    "past_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0
  }
  print(dataItem["genres"])
  for show in venue.shows:
    if show.start_time <= datetime.now() :
      dataItem['past_shows'].append(show) 
      dataItem['past_shows_count'] += 1
    else:
      dataItem['upcoming_shows'].append(show)
      dataItem['upcoming_shows_count'] += 1
  
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=dataItem)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    data = request.form
    venue = Venue(
      name=data['name'],
      city=data['city'],
      state=data['state'],
      address=data['address'],
      phone=data['phone'],
      facebook_link=data['facebook_link'],
      genres=  ",".join(request.form.getlist('genres'))
      )
    db.session.add(venue)
    db.session.commit()
    print(venue)
    flash('Venue ' + data['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
  finally:
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Veneue.query.get(venue_id)
  db.session.delete(venue)
  db.session.commit()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).paginate()
  data = []
  for resultItem in results.items:
    upcomingShows = 0
    for show in resultItem.shows:
      if show.start_time > datetime.now():
        upcomingShows += 1
    data.append({"id": resultItem.id, "name": resultItem.name, "num_upcoming_shows": upcomingShows})
  response={
    "count": results.total,
    "data": data
  }
 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
  dataItem = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.split(',') if artist.genres  else '',
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": [],
      "upcoming_shows": [],
      "past_shows_count": 0,
      "upcoming_shows_count": 0,
    }
  for show in artist.shows:
    if show.start_time <= datetime.now() :
      dataItem['past_shows'].append(show) 
      dataItem['past_shows_count'] += 1
    else:
      dataItem['upcoming_shows'].append(show)
    dataItem['upcoming_shows_count'] += 1
  
  # shows the venue page with the given venue_id
  
  data = dataItem
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  artist.genres = artist.genres_list
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  data = request.form
  editData = {
      'name': data['name'],
      'city': data['city'],
      'state': data['state'],
      'phone': data['phone'],
      'facebook_link': data['facebook_link'],
      'genres':  ",".join(request.form.getlist('genres')),
      'image_link': data['image_link'],
      'seeking_venue':  True if request.form.get('seeking_venue', False ) else False,
      'seeking_description': data['seeking_description'],
      'website': data['website']
  } 
  db.session.query(Artist).filter(Artist.id==artist_id).update(editData)
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  venue.genres = venue.genres_list
  form = VenueForm(obj=venue)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  data = request.form
  editData = {
      'name': data['name'],
      'city': data['city'],
      'state': data['state'],
      'address': data['address'],
      'phone': data['phone'],
      'facebook_link': data['facebook_link'],
      'genres': ",".join(request.form.getlist('genres')),
  } 
  return editData
  db.session.query(Venue).filter(Venue.id==venue_id).update(editData)
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    data = request.form
    artist = Artist(
      name=data['name'],
      city=data['city'],
      state=data['state'],
      phone=data['phone'],
      facebook_link=data['facebook_link'],
      genres= ",".join(request.form.getlist('genres')),
      image_link=data['image_link'],
      seeking_venue= True if request.form.get('seeking_venue', False ) else False,
      seeking_description=data['seeking_description'],
      website=data['website']
        )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + data['name'] + ' was successfully listed!')
  except:  
      flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
  finally:
    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    }) 
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm() 
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    data = request.form
    show = Show(artist_id=data['artist_id'], venue_id=data['venue_id'],start_time=data['start_time'])
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
  finally:
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
    app.run()

def run():
  app.run()
# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
