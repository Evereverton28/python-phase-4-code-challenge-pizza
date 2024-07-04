from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Add relationship
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    # Add serialization rules
    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

    def to_dict(self, only=None, exclude=None, extra=None):
        if only is None:
            only = []
        if exclude is None:
            exclude = []
        if extra is None:
            extra = {}
        result = {}
        for column in self.__table__.columns:
            if only and column.name not in only:
                continue
            if column.name in exclude:
                continue
            result[column.name] = getattr(self, column.name)
        result.update(extra)
        return result


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Add relationship
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan')
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    # Add serialization rules
    serialize_rules = ('-restaurant_pizzas.pizza',)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

    def to_dict(self, only=None, exclude=None, extra=None):
        if only is None:
            only = []
        if exclude is None:
            exclude = []
        if extra is None:
            extra = {}
        result = {}
        for column in self.__table__.columns:
            if only and column.name not in only:
                continue
            if column.name in exclude:
                continue
            result[column.name] = getattr(self, column.name)
        result.update(extra)
        return result


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id', ondelete='CASCADE'), nullable=False)

    # Add relationships
    restaurant = relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = relationship('Pizza', back_populates='restaurant_pizzas')

    # Add serialization rules
    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    # Add validation
    @validates('price')
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"

    def to_dict(self, only=None, exclude=None, extra=None):
        if only is None:
            only = []
        if exclude is None:
            exclude = []
        if extra is None:
            extra = {}
        result = {}
        for column in self.__table__.columns:
            if only and column.name not in only:
                continue
            if column.name in exclude:
                continue
            result[column.name] = getattr(self, column.name)
        result.update(extra)
        return result
