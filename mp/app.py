import lists

import model

from flask import Flask
from flask_migrate import Migrate

app = Flask(__name__)

app.config['TITLE'] = "Mapas - mlp"
app.secret_key = b'guerra aos senhores'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

db = model.db  
migrate = Migrate(app, db)  


db.init_app(app)


lists.configure(app)

