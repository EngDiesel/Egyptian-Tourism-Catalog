# Egyptian Tourism Catalog
Udacity's Full-Stack Nanodegree's 2nd project.
This web application meant to collect the types of [tourism in Egypt](https://en.wikipedia.org/wiki/Tourism_in_Egypt) and the best items in each of them.

### Project Description on [Udacity](https://www.udacity.com)
The Item Catalog project consists of developing an application that provides a list of items within a variety of categories, as well as provide a user registration and authentication system.
In this sample project, the homepage displays all current categories along with the latest added items.

## Project Requirements

#### JSON
  - The project implements a JSON endpoint that serves the same information as displayed in the HTML endpoints for an arbitrary item in the catalog.

#### CRUD Operations
- Website reads category and item information from a database.
- Website includes a form allowing users to add new items and correctly processes submitted forms.
- Website does include a form to edit/update a current record in the database table and correctly processes submitted forms.
- Website does include a function to delete a current record.

#### Authentication and Authorization
- Create, delete and update operations do consider authorization status prior to execution.
- Page implements a third-party authentication & authorization service (like Google Accounts or Mozilla Persona) instead of implementing its own authentication & authorization spec.
- Make sure there is a 'Login' and 'Logout' button/link in the project. The aesthetics of this button/link is up to the discretion of the student.

#### Code Quality
- Code is ready for personal review and neatly formatted and compliant with the Python [pycodestyle](https://www.python.org/dev/peps/pep-0008/) style guide.

#### Comments
- Comments are present and effectively explain longer code procedures.

#### Documentation
- `README.md` file includes details of all the steps required to successfully run the application.

## Dependencies.
This program requires some other software programs to run properly .

* **Udacity's FSND VM**  the virtual machine to run the project on it [click here](https://github.com/udacity/fullstack-nanodegree-vm) to download
* **Virtual Box** to manage virtual machines [click here ](https://www.virtualbox.org/wiki/Downloads) to download .
* **Vagrant** development environment [click here](https://www.vagrantup.com/) to download .

## Installation
After downloading the [Dependencies](##dependencies)
* Go to the **Vagrant** folder using the command `cd /vagrant`  
* Clone this project using command
```bash
git clone https://github.com/EngDiesel/Catalog-beta.git
```
* Run the virtual machine using the command `vagrant up` you have to wait because it's downloading an OS from the internet.
* After finishing downloading, now run `vagrant ssh` to login to your VM
* Go to **catalog** folder using `cd /vagrant/catalog/`
* Run the **models.py** file to setup the database using this command `python models.py`
* Now you can run the application using command `python views.py`
* On your browser, Visit `http://localhost:8000` to see the Home Page.

## Application Pages
| Link | Result |
| :-- | :------------- |
| http://localhost:8000 **OR** http://localhost:8000/categories | The home Page which have two areas, one of the is the **_Latest Items_** added to the database, and the **_Categories_** area contains all Categories in the database. |
| http://localhost:8000/login | Login page, you can login with your _facebook account_ **or** _Google Account_ |
| http://localhost/categories/<category_id> http://localhost/categories/<category_id>/items | Displays the items page for the category of id number <category_id> |
| http://localhost/categories/<category_id>/items/<item_id> | Displays a page contains the name, image and description for the item has id number <item_id>  |
| http://localhost:8000/<category_id>/items/<item_id>/edit | **(Login Required)** Displays a page helps you to edit the item of id <item_id> |
| http://localhost:8000/<category_id>/items/<item_id>/delete | **(Login Required)** Displays a page helps you to delete the item of id <item_id> |
| http://localhost:8000/addItem | **(Login Required)**Displays a page helps to create a new item |

## JSON Endpoints
This application provides a JSON API.

| Request | Response |
| :----- | :------------------------------------------- |
| http://localhost/json/categories | JSON Object includes all of the Categories in the DB. |
| http://localhost/json/categories/<int:category_id> | JSON Object includes details for the category of id number <category_id> |
| http://localhost/json/categories/<int:category_id>/items | JSON Object includes all items in the category of id number <category_id> |
| http://localhost/json/categories/<category_id>/items/<item_id> | JSON Object includes details of the item of id number <item_id> |

## References
- **[w3schools](https://www.w3schools.com/)** is a great web Reference.
- **[MDN](https://developer.mozilla.org/bm/docs/Web)** is also a great web Reference.
- **[SASS](https://sass-lang.com/)** Documentation helped a lot.
- **[Flask Documentation](http://flask.pocoo.org/docs/1.0/)** is an awesome Reference when developing a flask application.
- **[Unsplash](https://unsplash.com/)** is a fantastic website for Beautiful, free photos.
- **[Google](http://www.google.com)** is always my friend in the development journey or any activity of my life.
- **[Stack Overflow]()** has an answer for about every bug or problem.
