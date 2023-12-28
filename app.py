from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# Database connection details
db_connection = psycopg2.connect(
    host="localhost",
    database="car_data",
    user="postgres",
    password="tanish@13579"
)

# Create a cursor for interacting with the database
cursor = db_connection.cursor()

# API Logic

# Route to get all cars
@app.route('/cars', methods=['GET'])
def get_all_cars():
    cursor.execute("SELECT * FROM car_data")
    cars = cursor.fetchall()

    car_list = []
    for car in cars:
        car_dict = {
            'id': car[0],
            'title': car[1],
            'price': car[2]
        }
        car_list.append(car_dict)

    return jsonify({'cars': car_list})

# Route to get a specific car by ID
@app.route('/cars/<int:car_id>', methods=['GET'])
def get_car_by_id(car_id):
    cursor.execute("SELECT * FROM car_data WHERE id = %s", (car_id,))
    car = cursor.fetchone()

    if car:
        car_dict = {
            'id': car[0],
            'title': car[1],
            'price': car[2]
        }
        return jsonify(car_dict)
    else:
        return jsonify({'error': 'Car not found'}), 404

# Route to update the title of a car by ID
@app.route('/cars/<int:car_id>', methods=['PUT'])
def update_car_title(car_id):
    new_title = request.json.get('title', None)

    if new_title:
        cursor.execute("UPDATE car_data SET title = %s WHERE id = %s", (new_title, car_id))
        db_connection.commit()
        return jsonify({'message': 'Car title updated successfully'})
    else:
        return jsonify({'error': 'Title is required'}), 400

if __name__ == '__main__':
    app.run(debug=True)
