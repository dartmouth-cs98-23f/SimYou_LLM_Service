from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv, find_dotenv
import os
from .prompts import Prompts
from openai import OpenAI
import base64
import boto3

# Load environment variables
load_dotenv(find_dotenv())

# Get AWS keys from environment variables
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_public_key = os.getenv("AWS_ACCESS_KEY_ID")

# Initialize OpenAI and S3 clients
client = OpenAI()
s3 = boto3.resource('s3', region_name='us-east-2', aws_access_key_id=aws_public_key, aws_secret_access_key=aws_secret_key)

# Define S3 bucket name
bucket_name = 'sim-you-media'

secret_key = os.getenv("OPENAI_API_KEY")

# Initialize API router for thumbnails
thumbnails = APIRouter()

@thumbnails.post('/api/thumbnails')
def add_thumbnail(worldID: int):
    """
    This function generates a thumbnail image for a given world ID using OpenAI's DALL-E model.
    The generated image is then stored in an S3 bucket and the URL of the image is returned.

    Args:
    worldID (int): The ID of the world for which to generate a thumbnail.

    Returns:
    str: The URL of the generated thumbnail image.
    """
    # TODO get world description from db
    world_description = "Tatoine from Star Wars"

    # Get prompt for generating the thumbnail
    prompt = Prompts.get_world_thumbnail_prompt(world_description)

    # Generate image using OpenAI's DALL-E model
    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="256x256",
        quality="standard",
        n=1,
        response_format="b64_json",
    )

    # Build file name
    file_name = "thumbnails/" + str(worldID) + ".jpeg"

    # Put image in S3 bucket
    obj = s3.Object(bucket_name, file_name)
    obj.put(Body=base64.b64decode(response.data[0].b64_json))

    # Get bucket location
    location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)['LocationConstraint']

    # Get object URL
    object_url = "https://%s.s3-%s.amazonaws.com/%s" % (bucket_name,location, file_name)

    return object_url