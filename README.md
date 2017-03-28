# Catalog Application

Developed a content management system using the Flask framework in Python. Authentication is provided via OAuth and all data is stored within a PostgreSQL database.

## Quickstart:

+ From the VM interface (vagrant ssh)
+ cd /vagrant
+ cd catalog
+ copy the files listed below to this location
+ ls (to check filenames)
+ set up database using: python database_setup.py
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
   - client_secrets.json <br>

/static: <br>
   - style.css <br>
   
/templates: <br>
   - base_unlogged.html <br>
   - base.html <br>
   - edititem.html <br>
   - deleteitem.html <br>
   - newitem.html <br>
   - deletecategory.html <br>
   - editcategory.html <br>
   - newcategory.html <br>
   - index.html <br>
   - login.html <br>
   - item_public.html <br>
   - category_public.html <br>
   - index_public.html <br>
   - item.html <br>
   - category.html <br>
   - category.html <br>
