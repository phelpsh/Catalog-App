# Catalog Application

Project created in Python with Bootstrap, Flask, Jinja2, SQL Alchemy, sqlite, and uses OAuth 2.0 for Google signin.

## Quickstart:

+ From the VM interface (vagrant ssh)
+ cd /vagrant
+ cd catalog
+ ls (to check filenames)
+ run using: python project.py
+ runs in localhost:5000
+ Public can view categories and items
+ Log in with Google ID to edit or delete categories and items belonging to you

## JSON:

JSON endpoints can be reached in three ways:
+ http://localhost:5000/catalog/<category_name>/JSON: information about the items in a category
+ http://localhost:5000/catalog/JSON: for a list of all categories in the database (public read-only)
+ http://localhost:5000/catalog/<category_name>/<item_id>/JSON: for information about a specific item in a category

## What’s included:

/:<br>
   - database_setup.py <br>
   - project.py <br>

/static: <br>
   - style.css <br>
   
/templates: <br>
   - base_logged.html <br>
   - base.html <br>
   - comments.html <br>
   - edit_post.html <br>
   - edit_post2.html <br>
   - editcomment.html <br>
   - index.html <br>
   - login.html <br>
   - newcomment.html <br>
   - noposts.html <br>
   - permacomment.html <br>
   - permalink.html <br>
   - signup.html <br>
   - success.html <br>
   - successlike.html <br>
   - welcome.html <br>
