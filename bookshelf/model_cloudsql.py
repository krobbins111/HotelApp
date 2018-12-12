# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene


builtin_list = list


db = SQLAlchemy()


def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)


def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data


# [START model]
class Hotel(db.Model):
    __tablename__ = 'hotels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    address = db.Column(db.String(255))
    imageUrl = db.Column(db.String(999))
    amenities = db.Column(db.String(999))
    website = db.Column(db.String(255))
    description = db.Column(db.String(999))

    def __repr__(self):
        return "<Hotel(name='%s', id=%s)" % (self.name, self.id)

class HotelAPI(SQLAlchemyObjectType):
    class Meta:
        model = Hotel
        only_fields = ("id", "name", "address", "city", "state", "zip_code")

class hotelQuery(graphene.ObjectType):
    users = graphene.List(HotelAPI)

    def resolve_users(self, info):
        query = HotelAPI.get_query(info)
        return query.all()

hotelSchema = graphene.Schema(query=hotelQuery)

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(255))
    lname = db.Column(db.String(255))
    email = db.Column(db.String(255))
    payment_id = db.Column(db.Integer) #make foreign key to payment info or just add all payment fields to customer entity

    def __repr__(self):
        return "<Customer(lname='%s', fname='%s'   id=%s)" % (self.lname, self.fname, self.id)

class CustomerAPI(SQLAlchemyObjectType):
    class Meta:
        model = Customer
        only_fields = ("id", "fname", "lname" ,"email")

class customerQuery(graphene.ObjectType):
    users = graphene.List(CustomerAPI)

    def resolve_users(self, info):
        query = CustomerAPI.get_query(info)
        return query.all()

customerSchema = graphene.Schema(query=customerQuery)
# [END model]


# [START list]
def hotelList(limit=10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (Hotel.query
             .order_by(Hotel.name)
             .limit(limit)
             .offset(cursor))
    hotels = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(hotels) == limit else None
    return (hotels, next_page)

def customerList(limit=10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (Customer.query
             .order_by(Customer.name)
             .limit(limit)
             .offset(cursor))
    customer = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(customers) == limit else None
    return (customers, next_page)
# [END list]


# [START read]
def hotelRead(id):
    result = Hotel.query.get(id)
    if not result:
        return None
    return from_sql(result)

def customerRead(id):
    result = Customer.query.get(id) 
    if not result:
        return None
    return from_sql(result)
# [END read]


# [START create]
def hotelCreate(data):
    hotel = Hotel(**data)
    db.session.add(hotel)
    db.session.commit()
    return from_sql(hotel)

def customerCreate(data):
    customer = Customer(**data) #costumer object is assignment class from Costumer(db.model)
    db.session.add(customer)
    db.session.commit()
    return from_sql(customer)
# [END create]


# [START update]
def hotelUpdate(data, id):
    hotel = Hotel.query.get(id)
    for k, v in data.items():
        setattr(hotel, k, v)
    db.session.commit()
    return from_sql(hotel)

def customerUpdate(data, id):
    customer = Customer.query.get(id)
    for k, v in data.items():
        setattr(customer, k, v)
    db.session.commit()
    return from_sql(customer)
# [END update]


def hotelDelete(id):
    Hotel.query.filter_by(id=id).delete()
    db.session.commit()

def customerDelete(id):
    Customer.query.filter_by(id=id).delete()
    db.session.commit()


def _create_database():
    """
    If this script is run directly, create all the tables necessary to run the
    application.
    """
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    init_app(app)
    with app.app_context():
        db.create_all()
    print("All tables created")


if __name__ == '__main__':
    _create_database()
    