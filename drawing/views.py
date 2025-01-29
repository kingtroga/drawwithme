from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Artwork
import json
from django.core.files.base import ContentFile
import base64
import datetime

@login_required
def create_artwork(request):
    return render(request, 'drawing/create.html')

@login_required
def edit_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id, creator=request.user)
    return render(request, 'drawing/edit.html', {'artwork': artwork})

@login_required
def save_artwork(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled')
        canvas = request.POST.get('canvas', '{}')
        artwork_id = request.POST.get('artwork_id', '').strip()
        for file in request.FILES:
            print("File: ", file)
        # Handle PNG image upload
        image_file = request.FILES.get('image')

        print("image_file: ", image_file)

        if artwork_id:  # If updating an existing artwork
            artwork = get_object_or_404(Artwork, id=artwork_id, creator=request.user)
            artwork.title = title
            artwork.canvas_data = json.loads(canvas)
            if image_file:
                artwork.image = image_file
        else:  # Creating new artwork
            artwork = Artwork.objects.create(
                creator=request.user,
                title=title,
                canvas_data=json.loads(canvas),
                image=image_file  # Save uploaded image
            )

        artwork.save()
        return JsonResponse({'success': True, 'artwork_id': artwork.id})

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
@login_required
def collaborate_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    if request.user not in artwork.collaborators.all() and request.user != artwork.creator:
        return redirect('index')
    return render(request, 'drawing/collaborate.html', {'artwork: artwork'})