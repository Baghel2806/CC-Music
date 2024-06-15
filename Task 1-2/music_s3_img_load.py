import boto3
import json
import requests

# session varaible to store the session details of the aws lab ( has to be changed everytime a new lab is created)
session = boto3.session.Session(
    aws_access_key_id='ASIAZI2LIBDM3PZNKASB',
    aws_secret_access_key='wexneEjXrfmcTzzZoFoRJJm6epJCc/1+lMJRHSDt',
    aws_session_token='IQoJb3JpZ2luX2VjEF4aCXVzLXdlc3QtMiJIMEYCIQDXm0q7Qs/Jwss5fficIi8W4NJrgEdDL5Vlh/5ffc9HGQIhAM65rU754w/1QLHBHdRMGS+DjhtZcCj+JT7Xm1GuBYZKKr8CCJf//////////wEQABoMNjM3NDIzNTg1NDk3IgxFrsuVlV6Kqw/2Y/wqkwKOvhS/ReSUhIZsTh3A4IhNciUcwU7aGSoJpdSKN/lD0ZhZDosHn5sXP28o5izikuhCIJDehE1b9h6rW/E+yV2f9TqnBTZwUcMiLP1/dTJh5Og7jGgt35G/vuRMzTwP9dXT1rD7Nb3G3rs24QaONGqWY/A4CzZP+WknkUFzZCGY+jn377g2xGDUcWC0Nsnh+yDzX0CfEuBGDLtBTFZD0bwhumKUCIpdSlORVHgg4zySfbKQbh76Id2yjz2rQR9BnakHTprib0g8aQyI3PrZYXSbEJvAljmnjsLm7y13aAnCUKOMpiO1p2r3WHfH5riNdoO1Xgog2xS9qK474sYrX6d/LjpRDFpNrvRG8buaZSXqTHMb1jD9pPGwBjqcATv7z/Xu+vYnXQd3hpVEBBEvBceF8De1CwCbDkm6pdeGGApF1l+10MZV1luYOYcNxbwI6FuI+nhM6UAyRAyCN5irT3OqaqA6B6gn0P1I+uQDMuOxsVNFYS2/QRc3cNn6fZ8KSPafx93+ogYrcBYviqmmy177KOr0V2X59YUL601sma6sZz9bMjLb/cjDxIWaaH+4Xy0mjljCFXPWyw=='
)


dynamodb = session.client('dynamodb') #dynamodb client
s3 = session.client('s3') # s3 bucket client

#  function that is created to download image from the url
def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None

# function that uploads the image to the s3 bucket
def upload_to_s3(bucket_name, image_name, image_data):
    s3.put_object(Bucket=bucket_name, Key=image_name, Body=image_data)

# scans the music table and fetches the title of the song and it's image_url
response = dynamodb.scan(
    TableName = 'music',
     AttributesToGet=[
        'title','image_url',
    ],
)

# iterates across the titles and image urls and sends them to the upload function
for item in response['Items']:
    song_title = item['title']['S']
    song_image_url = item['image_url']['S']
    image_data = download_image(song_image_url)
    upload_to_s3('music-images-3882120',song_title+'.jpg',image_data)