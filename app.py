#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
from models import db, Venue, Artist, Show
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
  url_for ,
  jsonify
)
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# with app.app_context():
#     db.create_all()

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    # instead of just date = dateutil.parser.parse(value)
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

# def format_datetime(value, format='medium'):
#   date = dateutil.parser.parse(value)
#   if format == 'full':
#       format="EEEE MMMM, d, y 'at' h:mma"
#   elif format == 'medium':
#       format="EE MM, dd, y h:mma"
#   return babel.dates.format_datetime(date, format, locale='en')

# app.jinja_env.filters['datetime'] = format_datetime

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # locals = []
  # venue_new = Venue.query.all()

  # places = Venue.query.distinct(Venue.city, Venue.state).all()

  # for place in places:
  #   locals.append({
  #     'city': place.city,
  #     'state': place.state,
  #     'venue': ({
  #       'id': venue_new.id,
  #       'name': venue_new.name,
  #       'num_upcoming_shows': len([show for show in venue_new.shows if show.start_time > datetime.now()])
  #     } for venue in venue_new if 
  #         venue.city == place.city and venue.state == place.state)
  #   })
  
  data=[]
  results = Venue.query.distinct(Venue.city,Venue.state).all()
  for area in results:
    location_info = {
      "city": area.city,
      "state": area.state,
    }
    
    venues = Venue.query.filter_by(city=area.city, state=area.state).all()
    current_time = datetime.now()
    # upcoming_shows = Venue.shows.filter()

    location_info_ordered = []
    for venue in venues:
      location_info_ordered.append({
        "id": venue.id,
        "name": venue.name,
      })
    
    location_info["venues"] = location_info_ordered
    data.append(location_info)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  results = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
  response={
    "count": len(results),
    "data": []
  }
  for venue in results:
    response['data'].append({
      "id": venue.id,
      "name": venue.name,
    })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  data = Venue.query.get(venue_id)
  setattr(data, "genres", data.genres.split(","))

  past_shows = list(filter(lambda show: show.start_time < datetime.now(), data.shows))
  temp_shows = []
  for show in past_shows:
    temp = {}
    temp["artist_name"] = show.venue.name
    temp["artist_id"] = show.venue.id
    temp["artist_image_link"] = show.venue.image_link
    temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    temp_shows.append(temp)

  setattr(data, "past_shows", temp_shows)
  setattr(data,"past_shows_count", len(past_shows))

  upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), data.shows))
  temp_shows = []
  for show in upcoming_shows:
      temp = {}
      temp["artist_name"] = show.artists.name
      temp["artist_id"] = show.artists.id
      temp["artist_image_link"] = show.artists.image_link
      temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      temp_shows.append(temp)

  setattr(data, "upcoming_shows", temp_shows)    
  setattr(data,"upcoming_shows_count", len(upcoming_shows))

  # venue = Venue.query.filter_by(id=venue_id).one()
  # shows = Show.query.filter_by(venue_id=venue_id).all()
  
  # past_shows = []
  # upcoming_shows = []
  # current_time = datetime.now()
  
  # for show in shows:
  #   data = {
  #     "artist_id": show.artist_id,
  #     "artist_name": show.artist_name,
  #     "artist_image_link": show.artist.image_link,
  #     "start_time": format_datetime(str(show.start_time))}
  #   if show.start_time > current_time:
  #     upcoming_shows.append(data)
  #   else:
  #     past_shows.append(data)
    
  # data={
  #   "id": venue.id,
  #   "name": venue.name,
  #   "genres": venue.genres,
  #   "address": venue.address,
  #   "city": venue.city,
  #   "state": venue.state,
  #   "phone": venue.phone,
  #   "website": venue.website,
  #   "facebook_link": venue.facebook_link,
  #   "seeking_talent": venue.seeking_talent,
  #   "seeking_description":venue.description,
  #   "image_link": venue.image_link,
  #   "past_shows": past_shows,
  #   "upcoming_shows": upcoming_shows,
  #   "past_shows_count": len(past_shows),"upcoming_shows_count": len(upcoming_shows)
  # }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm(request.form)

  try:
    venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      facebook_link = form.facebook_link.data,
      genres = form.genres.data,
      website = form.website_link.data,
      image_link = form.image_link.data,
      # venue.looking_for_talent = request.form['looking_for_talent']
      seeking_description = form.seeking_description.data
    )

    db.session.add(venue)
    db.session.commit()
  
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  venue = Venue()
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.facebook_link = request.form['facebook_link']
  venue.genres = request.form['genres']
  venue.website = request.form['website']
  venue.image_link = request.form['image_link']
  # venue.looking_for_talent = request.form['looking_for_talent']
  venue.seeking_description = request.form['seeking_description']

  try:
    db.session.add(venue)
    db.session.commit()
    
    # on successful db insert, flash success
    flash('Venue ' + venue.name + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({'success': True})

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  result = Artist.query.distinct(Artist.city, Artist.name).all()
  for artist in result:
    artist_info = {
      "city": artist.city,
      "name": artist.name
    }

    artist_filter = Artist.query.filter_by(city=artist.city, state=artist.state).all()

    artist_info_requested = []
    for artist_name in artist_filter:
      artist_info_requested.append({
        "id": artist_name.id,
        "name": artist_name.name
      })

    artist_info['artist_filter'] = artist_info_requested
    data.append(artist_info)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  results = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()
  response={
    "count": len(results),
    "data": []
  }
  for artist in results:
    response['data'].append({
      "id": artist.id,
      "name": artist.name,
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
    
  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.facebook_link = request.form['facebook_link']
  artist.genres = request.form['genres']
  artist.image_link = request.form['image_link']
  artist.website = request.form['website']
  try:
    db.session.add(artist)
    db.session.commit()
    flash("Artist {} is updated successfully".format(artist.name))
  except:
    db.session.rollback()
    flash("Artist was not updated successfully")
  finally:
    db.session.close()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.facebook_link = request.form['facebook_link']
  venue.genres = request.form['genres']
  venue.image_link = request.form['image_link']
  venue.website = request.form['website']
  
  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm(request.form)

  try:
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      facebook_link = form.facebook_link.data,
      genres = form.genres.data,
      website = form.website_link.data,
      image_link = form.image_link.data,
      # venue.looking_for_talent = request.form['looking_for_talent']
      seeking_description = form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()  
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  artist = Artist()
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = request.form['genres']
  artist.facebook_link = request.form['facebook_link']
  artist.image_link = request.form['image_link']
  artist.website = request.form['website_link']
  # venue.looking_for_talent = request.form['looking_for_talent']
  artist.seeking_description = request.form['seeking_description']

  try:
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + artist.name + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]
  shows_list = Show.query.all()

  for show in shows_list:
    show_item = {}
    show_item["venue_id"] = show.Venue.id,
    show_item["venue_name"] = show.Venue.name,
    show_item["artist_name"] = show.Artist.name,
    show_item["artist_image_ink"] = show.Artist.image_link,
    show_item["start_time"] = show.start_time

    data.append(show_item)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm(request.form)

  try:
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    db.session.add(show)
    db.session.commit()  
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  show = Show()
  show.artist_id = request.form['artist_id']
  show.venue_id = request.form['venue_id']
  show.start_time = request.form['start_time']

  try:
    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
