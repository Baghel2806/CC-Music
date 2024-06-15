from flask import Flask, request, jsonify, session, render_template, redirect, url_for
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
from functools import reduce
import time


app = Flask(__name__)
app.secret_key = '2806'  

# session varaible to store the session details of the aws lab ( has to be changed everytime a new lab is created)
aws_session = boto3.session.Session(
    aws_access_key_id='ASIAZI2LIBDM3PZNKASB',
    aws_secret_access_key='wexneEjXrfmcTzzZoFoRJJm6epJCc/1+lMJRHSDt',
    aws_session_token='IQoJb3JpZ2luX2VjEF4aCXVzLXdlc3QtMiJIMEYCIQDXm0q7Qs/Jwss5fficIi8W4NJrgEdDL5Vlh/5ffc9HGQIhAM65rU754w/1QLHBHdRMGS+DjhtZcCj+JT7Xm1GuBYZKKr8CCJf//////////wEQABoMNjM3NDIzNTg1NDk3IgxFrsuVlV6Kqw/2Y/wqkwKOvhS/ReSUhIZsTh3A4IhNciUcwU7aGSoJpdSKN/lD0ZhZDosHn5sXP28o5izikuhCIJDehE1b9h6rW/E+yV2f9TqnBTZwUcMiLP1/dTJh5Og7jGgt35G/vuRMzTwP9dXT1rD7Nb3G3rs24QaONGqWY/A4CzZP+WknkUFzZCGY+jn377g2xGDUcWC0Nsnh+yDzX0CfEuBGDLtBTFZD0bwhumKUCIpdSlORVHgg4zySfbKQbh76Id2yjz2rQR9BnakHTprib0g8aQyI3PrZYXSbEJvAljmnjsLm7y13aAnCUKOMpiO1p2r3WHfH5riNdoO1Xgog2xS9qK474sYrX6d/LjpRDFpNrvRG8buaZSXqTHMb1jD9pPGwBjqcATv7z/Xu+vYnXQd3hpVEBBEvBceF8De1CwCbDkm6pdeGGApF1l+10MZV1luYOYcNxbwI6FuI+nhM6UAyRAyCN5irT3OqaqA6B6gn0P1I+uQDMuOxsVNFYS2/QRc3cNn6fZ8KSPafx93+ogYrcBYviqmmy177KOr0V2X59YUL601sma6sZz9bMjLb/cjDxIWaaH+4Xy0mjljCFXPWyw=='
)

dynamodb = aws_session.client('dynamodb', region_name = 'us-east-1') # dynamodb client
s3 = aws_session.client('s3', region_name = 'us-east-1') # s3 client

# Route to the index page
@app.route('/')
def index():
    return render_template('index.html')

def home():
    # Redirect to main dashboard if logged in, otherwise login page
    if 'user_email' in session:
        return redirect(url_for('main_page'))
    return redirect(url_for('index'))

# Route to the login page
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        return login()
    return render_template('login.html')

# Route to the login API
@app.route('/api/login', methods=['POST'])
def login():
    # Extract email and password from the JSON request
    email = request.json.get('email')
    password = request.json.get('password')

    try:
        response = dynamodb.get_item(
            TableName='login',
            Key={
            'email': {
                'S': email
            },
            }  
        )
        print(response)
        user = response['Item']
        if user['password']['S'] == password:
                session['user_email'] = email 
                session['user_name'] = user['user_name']['S'] 
                return jsonify({'message': 'Login successful', 'user_name': user['user_name']['S']}), 200
        else:
            return jsonify({'message': 'Invalid email or password'}), 401
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error accessing login data'}), 500

        
# Route to the register page
@app.route('/register', methods=['GET','POST'])
def register_page():
    if request.method == 'POST':
        return register()
    return render_template('register.html')

# Route to the register API
@app.route('/api/register', methods=['POST'])
def register():
    reg_email = request.json.get('email')
    reg_username = request.json.get('user_name')
    reg_password = request.json.get('password')
    
    try:
        response = dynamodb.get_item(
            TableName='login',
            Key={
            'email': {
                'S': reg_email
            },
            }  
        )
        if 'Item' in response:
            return jsonify({'message': 'Email already exists'}), 409
            
        dynamodb.put_item(
            TableName='login',
            Item={
                'email': {'S': reg_email},
                'user_name': {'S': reg_username},
                'password': {'S': reg_password}
                
            }
        )
        return jsonify({'message': 'User registered successfully'}), 201
    
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error'})
    

# Route to the main page
@app.route('/main')
def main_page():
    if 'user_email' not in session:
        return redirect(url_for('login_page'))
    
    user_email = session['user_email']
    user_name = session['user_name']
    
    # Fetch subscriptions from DynamoDB
    try:
        response = dynamodb.scan(
            TableName='user_subscriptions',
            FilterExpression='user_email = :email',
            ExpressionAttributeValues={':email': {'S': user_email}}
        )
        subscriptions = response.get('Items', [])
        for result in subscriptions:
            bucket_name = "music-images-3882120"
            region_name = "us-east-1"
            result['image_url'] = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{result['music_title']['S'].replace(' ', '+').replace('#','%23')}.jpg"
            result['id'] = result['id']['S']
            result['artist'] = result['artist']['S']
            result['music_title'] = result['music_title']['S']
            result['year'] = result['year']['S']
            result['user_email'] = result['user_email']['S']
    except Exception as e:
        print(f"Error fetching subscriptions: {e}")
        subscriptions = []
    print(subscriptions)
    return render_template('main.html', user_email=user_email, user_name=user_name, subscriptions=subscriptions, query_result = [])
    
# Route to the subscription API that handles the user subscriptions
@app.route('/api/subscriptions', methods=['POST'])
def user_subs():
    data = request.json #stores the data from the request
    user_email = data.get('email')
    # Building the filter expression manually
    filter_expressions = []
    expression_attribute_values = {}
    expression_attribute_names = {}

    # acesses the user email and modifies it 
    if user_email:
        filter_expressions.append("#t = :user_email")
        expression_attribute_values[":user_email"] = {'S': user_email}
        expression_attribute_names["#t"] = "user_email"

    filter_expression = "".join(filter_expressions)

    try:
        results = dynamodb.scan(
            TableName='user_subscriptions',
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names
        ).get('Items', [])
        
        if not results:
            return jsonify({'message': 'No results found'}), 404

        for result in results:
            bucket_name = "music-images-3882120"
            region_name = "us-east-1"
            result['image_url'] = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{result['music_title']['S'].replace(' ', '+').replace('#','%23')}.jpg"
            result['id'] = result['id']['S']
            result['artist'] = result['artist']['S']
            result['music_title'] = result['music_title']['S']
            result['year'] = result['year']['S']
            result['user_email'] = result['user_email']['S']
            
        return jsonify(results), 200

    except Exception as e:
        print(e)
        return jsonify({'message': 'Error querying music'}), 500

# Route to the Subscription Addition Endpoint
@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    # stores the data recieved into seperate variables
    sub_list_email = request.json.get('email')
    sub_list_musictitle = request.json.get('music_title')
    sub_list_artist = request.json.get('artist')
    sub_list_year = request.json.get('year')
    print(sub_list_artist)
    print(sub_list_email)
    print(sub_list_musictitle)
    print(sub_list_year)
    
    # checks is user is logged in
    if len(sub_list_email) == 0:
        return jsonify({'message': 'Not logged in'}), 401
    try:
        dynamodb.put_item(
            TableName='user_subscriptions',
            Item={
                'id': {'S': str(time.time())},
                'user_email': {'S': sub_list_email},
                'music_title': {'S': sub_list_musictitle},
                'artist': {'S': sub_list_artist },
                'year': {'S': sub_list_year}
            }
        )
        return jsonify({'message': 'Subscribed successfully'}), 201
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed to subscribe due to server error'}), 500

# Route for Unsubscribe API
@app.route('/api/unsubscribe', methods=['POST'])
def unsubscribe():
    sub_id = request.json.get('id')
    
    try:
        dynamodb.delete_item(
            TableName='user_subscriptions',
            Key={'id': {'S': sub_id}}
        )
        return jsonify({'message': 'Unsubscribed successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed to unsubscribe'}), 500

# Route for Query API
@app.route('/api/query', methods=['POST'])
def query_music():
    # data = request.json
    data = request.form
    print(data)
    title = data.get('title')
    artist = data.get('artist')
    year = data.get('year')
    
    # Building the filter expression manually
    filter_expressions = []
    expression_attribute_values = {}
    expression_attribute_names = {}

    if title:
        filter_expressions.append("#t = :title")
        expression_attribute_values[":title"] = {'S': title}
        expression_attribute_names["#t"] = "title"
    if artist:
        filter_expressions.append("#a = :artist")
        expression_attribute_values[":artist"] = {'S': artist}
        expression_attribute_names["#a"] = "artist"
    if year:
        filter_expressions.append("#y = :year")
        expression_attribute_values[":year"] = {'S': year}
        expression_attribute_names["#y"] = "year"

    filter_expression = " AND ".join(filter_expressions)

    if 'user_email' not in session:
        return redirect(url_for('login_page'))
    
    user_email = session['user_email']
    user_name = session['user_name']
    
    # Fetch subscriptions from DynamoDB
    try:
        response = dynamodb.scan(
            TableName='user_subscriptions',
            FilterExpression='user_email = :email',
            ExpressionAttributeValues={':email': {'S': user_email}}
        )
        subscriptions = response.get('Items', [])
        for result in subscriptions:
            bucket_name = "music-images-3882120"
            region_name = "us-east-1"
            result['image_url'] = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{result['music_title']['S'].replace(' ', '+').replace('#','%23')}.jpg"
            result['id'] = result['id']['S']
            result['artist'] = result['artist']['S']
            result['music_title'] = result['music_title']['S']
            result['year'] = result['year']['S']
            result['user_email'] = result['user_email']['S']
            
            
        query_results = dynamodb.scan(
            TableName='music',
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names
        ).get('Items', [])
        
        if not query_results:
            return jsonify({'message': 'No results found'}), 404

        # Assume you have a method to construct image URLs
        for result in query_results:
            bucket_name = "music-images-3882120"
            region_name = "us-east-1"
            result['image_url'] = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{result['title']['S'].replace(' ', '+').replace('#','%23')}.jpg"
            result['web_url'] = result['web_url']['S']
            result['artist'] = result['artist']['S']
            result['title'] = result['title']['S']
            result['year'] = result['year']['S']
        # return jsonify(results), 200
        print(query_results)
        return render_template('main.html', user_email=user_email, user_name=user_name, subscriptions=subscriptions, query_results = query_results)

    except Exception as e:
        print(e)
        return jsonify({'message': 'Error querying music'}), 500

    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)