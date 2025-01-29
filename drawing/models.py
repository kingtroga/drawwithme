from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from .utils import get_embedding
from django.dispatch import receiver

class Artwork(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='artworks')
    collaborators = models.ManyToManyField(User, related_name='collaborations', blank=True)
    canvas_data = models.JSONField(blank=True, null=True)  # Fabric.js canvas state
    image = models.ImageField(upload_to='artworks/', blank=True, null=True)  # PNG export
    vector_embedding = models.JSONField(blank=True, null = True)
    is_game_artwork = models.BooleanField(default=False)
    game_words = models.TextField(blank=True, null=True)  # Store words as a JSON string (list)
    description = models.TextField(blank=True, null=True)
    processing = models.BooleanField(default=False)


    def __str__(self):
        return self.title
    
    def describe_picture(self):
        """
        Describes the picture and stores the 
        description and the vector embeddings 
        of the description.
        """
        if self.processing:
            return

        self.processing = True
        self.save(update_fields=['processing'])

        try:
            # Use Open AI to describe the image
            import base64
            from openai import OpenAI
            import os

            if "OPENAI_API_KEY" not in os.environ:
                os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

            client = OpenAI()

            # Function to encode the image
            def encode_image(image_path):
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")


            # Path to your image
            image_path = self.image.path

            # Getting the base64 string
            base64_image = encode_image(image_path)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What is in this image?",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
            )

            self.description = str(response.choices[0].message.content)

            # Handle embeddings
            try:
                cache_key = f'picture_embedding_{self.id}'
                embedding = cache.get(cache_key)

                if not embedding:
                    embedding = get_embedding(self.description)
                    if not embedding:
                        raise Exception("Failed to generate embedding from HuggingFace API")
                    cache.set(cache_key, embedding, 3600)

                self.vector_embedding = embedding
                self.processing = False
                self.save()

            except Exception as e:
                raise Exception(f"Error generating embeddings: {str(e)}")

        except Exception as e:
            self.processing = False
            self.save(update_fields=['processing'])
            raise e
    
    def game_words_as_list(self):
        if self.game_words:
            return self.game_words.split(',')
        return []

@receiver(post_save, sender=Artwork)
def describe_picture_on_save(sender, instance, created, **kwargs):
    if created and not instance.processing:
        instance.describe_picture()

@receiver(post_delete, sender=Artwork)
def delete_file(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
