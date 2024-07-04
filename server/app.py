#!/usr/bin/env python3
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_encoder.compact = False

db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

# Ensure the database is created and initialized
with app.app_context():
    db.create_all()

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Restaurant not found"}), 404

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Routes
class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants])

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return jsonify(restaurant.to_dict(
                only=('id', 'name', 'address'),
                extra={
                    'restaurant_pizzas': [rp.to_dict() for rp in restaurant.restaurant_pizzas]
                }
            ))
        else:
            abort(404)

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            try:
                db.session.delete(restaurant)
                db.session.commit()
                return '', 204
            except IntegrityError:
                db.session.rollback()
                abort(500)
        else:
            abort(404)

class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas])

class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            # Validate price range
            if not (1 <= data['price'] <= 30):
                return jsonify({"errors": ["Price must be between 1 and 30"]}), 400
            
            restaurant = Restaurant.query.get(data['restaurant_id'])
            pizza = Pizza.query.get(data['pizza_id'])
            
            if not restaurant or not pizza:
                abort(404)

            restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(restaurant_pizza)
            db.session.commit()

            return jsonify(restaurant_pizza.to_dict(
                extra={
                    'pizza': pizza.to_dict(only=('id', 'name', 'ingredients')),
                    'restaurant': restaurant.to_dict(only=('id', 'name', 'address'))
                }
            )), 201
        except KeyError:
            abort(400)
        except Exception as e:
            print(str(e))
            abort(500)

# Add resources to API
api.add_resource(RestaurantsResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzasResource, '/pizzas')
api.add_resource(RestaurantPizzasResource, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
