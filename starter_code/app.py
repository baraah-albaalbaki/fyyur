#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from flask_migrate import Migrate
from datetime import datetime
import sys
from models import db, app, Venue, Artist, Show


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
db.init_app(app)

# TODO: connect to a local postgresql database
# migrate = Migrate(app, db)

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
  # num_shows should be aggregated based on number of upcoming shows per venue.
  
  print(datetime.today())
  # print('2021-05-04 22:20:28.968967'==datetime.now())

  data = []
  citiesstates = Venue.query.with_entities(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
  # print(citiesstates)
  for citystate in citiesstates:
    # print(Venue.city.value)
    venues = Venue.query.filter(Venue.city==citystate.city, Venue.state==citystate.state).all()
    venuesindata=[]
    for venue in venues:
      # num_upcoming_shows = venue.query(func.count().filter(Show.start_time > db.DateTime.now()))
      upcoming_shows=venue.showss.filter(Show.start_time > datetime.now()).all()
      num_upcoming_shows=len(upcoming_shows)
      venuesindata.append(
        {
          "id": venue.id, 
          "name": venue.name,
          "num_upcoming_shows":num_upcoming_shows
        }
      )
    data.append({
      "city":citystate.city,
      "state":citystate.state,
      "venues": venuesindata 
    })
    # print(data)
  # if error:
  #   return render_template('errors/404.html')
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  items = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  data = []
  count = len(items)
  
  for item in items:
    num_upcoming_shows=len(item.showss.filter(Show.start_time > datetime.now()).all())
    data.append({
      "id":item.id,
      "name":item.name,
      "num_upcoming_shows":num_upcoming_shows
  })
  response=({"count":count,"data":data})

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # print(venue1)

  # The code joins tables from existing models to select Artists by Venues where they previously performed, 
  # successfully filling out the Venues page with a “Past Performances” section.
  
  venue1 = Venue.query.get(venue_id)
  # upcoming_shows = venue1.showss.filter(Show.start_time > datetime.now()).all()
  # num_upcoming_shows = len(upcoming_shows)

  # jnArSh = db.session.query(Show,Artist).join(Artist).filter(Show.venue_id==venue_id)
  upcoming_shows = db.session.query(Show,Artist).join(Artist,Show.artist_id==Artist.id).filter(Show.venue_id==venue_id,Show.start_time>datetime.now())
  num_upcoming_shows = 0 
  print(num_upcoming_shows)

  upcoming_shows_list = []
  for upcoming_show in upcoming_shows:
    num_upcoming_shows +=1
    upcoming_shows_list.append(
      {
      # "artist_id": upcoming_show.artist_id, 
      "artist_id": upcoming_show.Artist.id, 
      # "artist_name": upcoming_show.artist.name,
      "artist_name": upcoming_show.Artist.name,
      # "artist_image_link": upcoming_show.artist.image_link,
      "artist_image_link": upcoming_show.Artist.image_link,
      # "start_time": str(upcoming_show.start_time)
      "start_time": str(upcoming_show.Show.start_time)
      }
    )

  past_shows_list=[]

  # past_shows=venue1.showss.filter(Show.start_time < datetime.now()).all()
  # num_past_shows=len(past_shows)

  # past_shows = jnArSh.filter(Show.start_time < datetime.now()).all
  past_shows = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id==venue_id,Show.start_time<datetime.now())
  # num_past_shows = 0
  # print(past_shows)

  for past_show in past_shows:
    # num_past_shows +=1
    # print(past_show.artist)
    past_shows_list.append(
      {
      "artist_id": past_show.Artist.id, 
      "artist_name": past_show.Artist.name,
      "artist_image_link": past_show.Artist.image_link,
      "start_time": str(past_show.Show.start_time)
      }
    )
  num_past_shows = len(past_shows_list)
  # print(past_show.artist.name)
  # x="".join(venue1.genres)
  # print(x)
  # for genre in x:
  #   print( genre)
  data1 = {
    "id": venue1.id,
    "name": venue1.name,
    # "genres": "".join(venue1.genres).split(','),
    "genres": venue1.genres.split(','),
    "address": venue1.address,
    "city": venue1.city,
    "state": venue1.state,
    "phone": venue1.phone,
    "website": venue1.website,
    "facebook_link": venue1.facebook_link,
    "seeking_talent": venue1.seeking_talent,
    "seeking_description": venue1.seeking_description,
    "image_link": venue1.image_link,
    "past_shows":past_shows_list,
    "upcoming_shows":upcoming_shows_list,
    "past_shows_count":num_past_shows,
    "upcoming_shows_count":num_upcoming_shows
  }
  print(data1['genres'])
  
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data1)

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

  error = False
  # form = VenueForm()  
  data = request.form
  print(data)
  name = data['name']
  city = data['city']
  state = data['state']
  address = data['address']
  phone = data['phone']
  # print(request.form.genres.data)
  # genres = data.getlist('genres')
  genres = ",".join(data.getlist('genres'))
  print(genres)
  facebook_link = data['facebook_link']
  image_link = data['image_link']
  website = data['website_link']

  seeking_talent='seeking_talent' in data
  print(seeking_talent)
  seeking_description = data['seeking_description']
  
  try:
    venue = Venue(
      name = name,
      city = city, 
      state = state,
      address = address, 
      phone = phone,
      # genres = ','.join(genres),
      # genres=genres.split(','),
      genres = genres,
      facebook_link = facebook_link, 
      image_link = image_link,
      website = website,
      seeking_talent = seeking_talent, 
      seeking_description = seeking_description
    )
    print(venue.genres)
    # print(venue.genres.split(','))
    # form.populate_obj(venue)

    db.session.add(venue)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
    db.session.close()

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  if not error:
    flash('Venue ' + name + ' was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  venue = Venue.query.get(venue_id)
  error = False
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if not error:
    flash(f'Venue {venue.name} deleted')
  else:
    flash('Venue not deleted')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  # DELETE Button added in show_venues.html
  return redirect(url_for('index'))

# ADDED THING
# ----------------delete artist--------------------------#
@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
  artist = Artist.query.get(artist_id)
  error = False
  try:
    db.session.delete(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if not error:
    flash('Artist '+ artist.name + ' deleted')
  else:
    flash('not deleted!')

  # DELETE Button added on show_venues.html
  return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append(
      {
        "id": artist.id, 
        "name":artist.name
      }
    )
  # print(data)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term')
  items = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  data = []
  count = len(items)
  
  for item in items:
    num_upcoming_shows=len(item.showss.filter(Show.start_time > datetime.now()).all())
    data.append({
      "id":item.id,
      "name":item.name,
      "num_upcoming_shows":num_upcoming_shows
  })
  response=({"count":count,"data":data})

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # # TODO: replace with real artist data from the artist table, using artist_id
  artist1 = Artist.query.get(artist_id) 
  jnVnSh = db.session.query(Show,Venue).join(Venue, Show.venue_id==Venue.id)
  upcoming_shows = jnVnSh.filter(Show.artist_id==artist_id,Show.start_time>datetime.now())
  
  # upcoming_shows=artist1.showss.filter(Show.start_time > datetime.now()).all()
  # num_upcoming_shows=len(upcoming_shows)
  
  # num_upcoming_shows = 0

  upcoming_shows_list=[]
  for upcoming_show in upcoming_shows:
    # num_upcoming_shows +=1
    upcoming_shows_list.append(
      {
      "venue_id": upcoming_show.Venue.id, 
      "venue_name": upcoming_show.Venue.name,
      "venue_image_link": upcoming_show.Venue.image_link,
      "start_time": str(upcoming_show.Show.start_time)
      }
    )
  num_upcoming_shows=len(upcoming_shows_list)
  past_shows_list=[]

  # past_shows=artist1.showss.filter(Show.start_time < datetime.now()).all()
  # num_past_shows=len(past_shows)

  past_shows = jnVnSh.filter(Show.artist_id==artist_id,Show.start_time<datetime.now())

  for past_show in past_shows:
    # num_past_shows += 1
    past_shows_list.append(
      {
      "venue_id": past_show.Venue.id, 
      "venue_name": past_show.Venue.name,
      "venue_image_link": past_show.Venue.image_link,
      "start_time": str(past_show.Show.start_time)
      }
    )
  num_past_shows=len(past_shows_list)
  
  data1 = {
    "id": artist1.id,
    "name": artist1.name,
    "genres": artist1.genres.split(','),
    "city": artist1.city,
    "state": artist1.state,
    "phone": artist1.phone,
    "website": artist1.website,
    "facebook_link": artist1.facebook_link,
    "seeking_venue": artist1.seeking_venue,
    "seeking_description": artist1.seeking_description,
    "image_link": artist1.image_link,
    "past_shows":past_shows_list,
    "upcoming_shows":upcoming_shows_list,
    "past_shows_count":num_past_shows,
    "upcoming_shows_count":num_upcoming_shows
  }
  print(data1)
  print(data1['genres'])
  
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data1)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  # print(artist)
  form = ArtistForm()
  
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data= artist.phone
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  print(artist.seeking_venue)
  if artist.seeking_venue:
    form.seeking_venue.data ='y'
  form.seeking_description.data = artist.seeking_description

  # form = ArtistForm(obj=artist)
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  data = request.form
  artist = Artist.query.get(artist_id)

  if request.method == 'POST':
    
    try:
      name = data['name']
      city = data['city']
      state = data['state']
      phone = data['phone']
      genres = ",".join(data.getlist('genres'))
      facebook_link = data['facebook_link']
      image_link = data['image_link']
      website = data['website_link']
      seeking_venue = 'seeking_venue' in data
      seeking_description = data['seeking_description']

      artist.name = name
      artist.city = city
      artist.state = state
      artist.phone = phone
      artist.genres = genres
      artist.facebook_link = facebook_link
      artist.image_link = image_link
      artist.website = website
      artist.seeking_venue = seeking_venue
      artist.seeking_description = seeking_description

      db.session.commit()

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    
    finally:
      db.session.close()
    
    if not error:
      flash('successfully updated!')
    
    else:
      flash('could not be updated.')

  return redirect(url_for('show_artist', artist_id = artist_id))

@app.route('/venues/<int:venue_id>/edit', methods = ['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data= venue.phone
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  if venue.seeking_talent:
    form.seeking_talent.data ='y'
  form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  error = False
  # form = VenueForm(request.form)
  # form = VenueForm()

  data = request.form
  venue = Venue.query.get(venue_id)
  # if form.validate_on_submit():

  if request.method == 'POST':
    try:
      name = data['name']
      city = data['city']
      state = data['state']
      address = data['address']
      phone = data['phone']
      genres = ",".join(data.getlist('genres'))
      facebook_link = data['facebook_link']
      image_link = data['image_link']
      website = data['website_link']
      # seeking_talent = data['seeking_talent']
      # seeking_talent = False
      # if 'seeking_talent' in data =='y':
      #   seeking_talent = True
      seeking_talent = 'seeking_talent' in data
      seeking_description = data['seeking_description']

      # venue = Venue(
      venue.name = name
      venue.city = city
      venue.state = state
      venue.address = address
      venue.phone = phone
      venue.genres = genres
      venue.facebook_link = facebook_link
      venue.image_link = image_link
      venue.website = website
      venue.seeking_talent = seeking_talent
      venue.seeking_description = seeking_description
      # )
      # print(venue.seeking_talent)
      db.session.commit()
      print(venue.address)

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    
    finally:
      db.session.close()
    
    if not error:
      flash('Venue successfully updated!')
    
    else:
      flash('could not be updated.')
  # return render_template('forms/edit_venue.html', form=data, venue=venue)
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  data = request.form

  name = data['name']
  city = data['city']
  state = data['state']
  phone = data['phone']

  print(data.getlist('genres'))

  genres = ",".join(data.getlist('genres'))  
  print(genres)

  facebook_link = data['facebook_link']
  image_link = data['image_link']
  website = data['website_link']
  print('seeking venue?')
  print('seeking_venue' in data)
  seeking_venue='seeking_venue' in data
  seeking_description = data['seeking_description']
  try:
    artist = Artist(
      name = name,
      city = city, 
      state = state,
      phone = phone,
      genres = genres,
      facebook_link = facebook_link, 
      image_link = image_link,
      website = website,
      seeking_venue = seeking_venue, 
      seeking_description = seeking_description
    )
    db.session.add(artist)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
    db.session.close()

  # on successful db insert, flash success
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  # TODO: on unsuccessful db insert, flash an error instead.
  else:
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  print(seeking_venue)
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append ({
      "venue_id": show.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
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
  # TODO: insert form data as a new Show record in the db, instead

  error = False  
  data = request.form

  venue_id = data['venue_id']
  artist_id = data['artist_id']
  start_time = data['start_time']
  try:
    show = Show(
      venue_id = venue_id,
      artist_id = artist_id,
      start_time = start_time
    )
    db.session.add(show)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()
  
  if not error:
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  
  else:
    flash('An error occurred. Show could not be listed.')
  # e.g., flash('An error occurred. Show could not be listed.')
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
# '''
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)
# '''
