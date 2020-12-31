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
from flask_migrate import Migrate
from forms import *
from datetime import datetime
from models import *
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
  data = Venue.query.order_by('id').all()
  q = db.session.query(Venue).distinct(Venue.city, Venue.state).all()
  #the distinct query has been sent to the view to be displayed  with a nested loop and if condition 
  #tp group veneues together
  return render_template('pages/venues.html', venues=data, locations=q)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search=request.form.get('search_term', '')
  counter = Venue.query.filter(Venue.name.ilike('%' + search + '%')).count()
  responses = Venue.query.filter(Venue.name.ilike('%' + search + '%')).all()
  return render_template('pages/search_venues.html', results=responses, search_term=search, count=counter)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.get(venue_id)
  data.genres = str(data.genres).split(",")
  shows = db.session.query(Show).join(Artist).join(Venue).filter(Venue.id == venue_id).all()
    #i retrevied the data with a join query as noted to me in the first submition
    # so it gets all the needed attributes,separted them to two lists to be displayed on the view
  
  upcoming = []
  past = []
  time = datetime.now()
  for show in shows:
    if show.start_time < time :
      show.start_time = str(show.start_time)
      past.append(show)
    else:
      show.start_time = str(show.start_time)
      upcoming.append(show)

  return render_template('pages/show_venue.html', venue=data,upcoming_shows=upcoming, past_shows=past)  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  try:
    venue = Venue()
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('Venue ' + request.form['name'] + ' had a trouble to be listed!')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/delete/<venue_id>', methods=['GET'])
def delete_venue(venue_id):   
  try:  
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('Venue ' + venue.name + ' could not be deleted!')
  finally:
    db.session.close()
  return redirect(url_for('index'))

  
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=Artist.query.order_by('id').all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search=request.form.get('search_term', '')
  counter = Artist.query.filter(Artist.name.ilike('%' + search + '%')).count()
  responses = Artist.query.filter(Artist.name.ilike('%' + search + '%')).all()
  return render_template('pages/search_artists.html', results=responses, search_term=search,count=counter)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.get(artist_id)
  data.genres = str(data.genres).split(",")
  shows = db.session.query(Show).join(Artist).join(Venue).filter(Artist.id == artist_id).all()
  #i retrevied the data with a join query as noted to me in the first submition
  # so it gets all the needed attributes,separted them to two lists to be displayed on the view
  upcoming = []
  past = []
  time = datetime.now()
  for show in shows:
    if show.start_time < time :
      show.start_time = str(show.start_time)
      past.append(show)
    else:
      show.start_time = str(show.start_time)
      upcoming.append(show)
  print(shows)
  print(upcoming)
  print(past)
  return render_template('pages/show_artist.html', artist=data, upcoming_shows=upcoming, past_shows=past)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)
  #here is proccessing on the uncritical data fields on the forms that can be left empty
  try:
    form.populate_obj(artist)
    if request.form['phone']:
      artist.phone= request.form['phone'] 
    if request.form['facebook_link']:
      artist.facebook_link = request.form['facebook_link'] 
    if not request.form['seeking_venue']:
      artist.seeking_venue = False
      artist.seeking_description = None
    db.session.commit()
    flash('Artist '+artist.name+' was updated successfully updated!')
  except:
    db.session.rollback()
    flash('Artist '+artist.name+' was not updated successfully updated!')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  #here is proccessing on the uncritical data fields on the forms that can be left empty
  try:
    form.populate_obj(venue)
    if request.form['phone']:
      venue.phone= request.form['phone'] 
    if request.form['facebook_link']:
      venue.facebook_link = request.form['facebook_link'] 
    if not request.form['seeking_talent']:
      venue.seeking_talent = False
      venue.seeking_description = None 
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback() 
    flash('Venue ' + request.form['name'] + ' was not successfully updated!')
  finally:
    db.session.rollback()
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
  try:
    artist = Artist()
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' had a trouble to be listed!')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    show.artist_name = artist.name
    show.artist_image_link = artist.image_link
    show.venue_name = venue.name
    show.start_time = str(show.start_time)
    print(show.artist_name)
    
  data=shows
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  venue_id = request.form['venue_id']
  artist_id = request.form['artist_id']
  start_time = request.form['start_time']
  try:
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Could not list the show!')
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
