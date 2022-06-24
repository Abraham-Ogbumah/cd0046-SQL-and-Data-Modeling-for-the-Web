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

with app.app_context():
    db.create_all()

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
  results = Venue.query.distinct(Venue.city,Venue.state).all()
  data=[]
  for area in results:
    location_info = {
      "city": area.city,
      "state": area.state,
    }
    
    venues = Venue.query.filter_by(city=area.city, state=area.state).all()

    location_info_ordered = []
    for venue in venues:
      upcoming_shows = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).all()
      num_upcoming_shows = len(upcoming_shows)
      location_info_ordered.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
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
  
  venue = Venue.query.filter_by(id=venue_id).first()
  upcoming_shows_query = Show.query.join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_shows_query:
    upcoming_shows.append({
      #object.backref.attribute
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })
  past_shows_query = Show.query.join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []
  for show in past_shows_query:
    past_shows.append({
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })
  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)

  venue = {
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
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = VenueForm(request.form)

  if form.validate_on_submit():
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
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
    )

    db.session.add(venue)
    db.session.commit()
  
  else:
    db.session.rollback()
  
  db.session.close()

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
  # data=[]
  # result = Artist.query.distinct(Artist.city, Artist.name).all()
  # for artist in result:
  #   artist_info = {
  #     "city": artist.city,
  #     "name": artist.name
  #   }

  #   artist_filter = Artist.query.filter_by(city=artist.city, state=artist.state).all()

  #   artist_info_requested = []
  #   for artist_name in artist_filter:
  #     artist_info_requested.append({
  #       "id": artist_name.id,
  #       "name": artist_name.name
  #     })

  #   artist_info['artist_filter'] = artist_info_requested
  #   data.append(artist_info)
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

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
  
  artist = Artist.query.filter_by(id=artist_id).first()
  upcoming_shows_query = Show.query.join(Artist).filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_shows_query:
    upcoming_shows.append({
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time
    })
  past_shows_query = Show.query.join(Artist).filter(Show.artist_id==artist.id).filter(Show.start_time<datetime.now()).all()
  past_shows = []
  for show in past_shows_query:
    past_shows.append({
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time
    })
  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)

  artist = {
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "website": artist.website_link,
    "seeking_venue": artist.seeking_venue,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  form = ArtistForm()   
  artist = Artist.query.get(artist_id)
  # artist.name = request.form['name']
  # artist.city = request.form['city']
  # artist.state = request.form['state']
  # artist.phone = request.form['phone']
  # artist.facebook_link = request.form['facebook_link']
  # artist.genres = request.form['genres']
  # artist.image_link = request.form['image_link']
  # artist.website = request.form['website']
  # try:
  #   db.session.add(artist)
  #   db.session.commit()
  #   flash("Artist {} is updated successfully".format(artist.name))
  # except:
  #   db.session.rollback()
  #   flash("Artist was not updated successfully")
  # finally:
  #   db.session.close()
  # # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if form.validate_on_submit():
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.seeking_venue = form.seeking_venue.data
    artist.website_link = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.seeking_description = form.seeking_description.data

    db.session.add(artist)
    db.session.commit()
  else:
    db.session.rollback()
    flash('Sorry, artist' + str(form['name']) + 'could not be updated.')
  
  db.session.close()

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

  # venue = Venue.query.get(venue_id)
  # venue.name = request.form['name']
  # venue.city = request.form['city']
  # venue.state = request.form['state']
  # venue.address = request.form['address']
  # venue.phone = request.form['phone']
  # venue.facebook_link = request.form['facebook_link']
  # venue.genres = request.form['genres']
  # venue.image_link = request.form['image_link']
  # venue.website = request.form['website_link']
  
  # try:
  #   db.session.add(venue)
  #   db.session.commit()
  #   flash('Venue ' + venue.name + ' was successfully updated!')
  # except:
  #   db.session.rollback()
  #   flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
  # finally:
  #   db.session.close()

  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if form.validate_on_submit():
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + str(form['name']) + ' updated successfully.')
  else:
    db.session.rollback()
    flash('Venue' + str(form['name']) + 'could not be updated.')
  db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm(request.form)

  # try:
  #   artist = Artist(
  #     name = form.name.data,
  #     city = form.city.data,
  #     state = form.state.data,
  #     phone = form.phone.data,
  #     facebook_link = form.facebook_link.data,
  #     genres = form.genres.data,
  #     website = form.website_link.data,
  #     image_link = form.image_link.data,
  #     # venue.looking_for_talent = request.form['looking_for_talent']
  #     seeking_description = form.seeking_description.data
  #   )
  #   db.session.add(artist)
  #   db.session.commit()  
  # except:
  #   db.session.rollback()
  # finally:
  #   db.session.close()

  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

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
      seeking_venue = form.seeking_venue,
      seeking_description = form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()  

     #   # on successful db insert, flash success
    flash('Artist ' + artist.name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
    db.session.close()

  # artist = Artist()
  # artist.name = request.form['name']
  # artist.city = request.form['city']
  # artist.state = request.form['state']
  # artist.phone = request.form['phone']
  # artist.genres = request.form['genres']
  # artist.facebook_link = request.form['facebook_link']
  # artist.image_link = request.form['image_link']
  # artist.website = request.form['website_link']
  # # venue.looking_for_talent = request.form['looking_for_talent']
  # artist.seeking_description = request.form['seeking_description']

  # try:
  #   db.session.add(artist)
  #   db.session.commit()
  #   # on successful db insert, flash success
  #   flash('Artist ' + artist.name + ' was successfully listed!')
  # # TODO: on unsuccessful db insert, flash an error instead.
  # except:
  #   db.session.rollback()
  #   flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  # finally:
  #   db.session.close()

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
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_ink": show.artist.image_link,
      "start_time": show.start_time
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm(request.form)

  # try:
  #   show = Show(
  #     artist_id = form.artist_id.data,
  #     venue_id = form.venue_id.data,
  #     start_time = form.start_time.data
  #   )
  #   db.session.add(show)
  #   db.session.commit()  
  # except:
  #   db.session.rollback()
  # finally:
  #   db.session.close()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()

  if form.validate_on_submit():
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  
  else:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  
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
