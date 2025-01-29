from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Artwork
import json
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import base64
import datetime
import json
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http.multipartparser import MultiPartParser
from django.core.exceptions import PermissionDenied
from .models import Artwork, User

@login_required
def create_artwork(request):
    return render(request, 'drawing/create.html')

@login_required
@require_http_methods(["GET", "PUT"])
def edit_artwork(request, pk):
    artwork = get_object_or_404(Artwork, id=pk, creator=request.user)
    
    if request.method == 'PUT':
        try:
            # Parse PUT data based on content type
            if request.content_type == 'multipart/form-data':
                # Handle multipart form data (including files)
                parser = MultiPartParser(request.META, request, request.upload_handlers)
                data, files = parser.parse()
            else:
                # Handle other content types (e.g., application/x-www-form-urlencoded)
                data = QueryDict(request.body)
                files = {}

            # Update core fields
            artwork.title = data.get('title', artwork.title)
            artwork.description = data.get('description', artwork.description)

            # Handle canvas data
            if 'canvas_data' in data:
                try:
                    artwork.canvas_data = json.loads(data['canvas_data'])
                except json.JSONDecodeError:
                    pass  # Keep existing data if invalid

            # Handle image upload
            if 'image' in files:
                artwork.image = files['image']

            # Save artwork to update fields
            artwork.save()

            # Update collaborators
            collaborator_ids = [int(cid) for cid in data.get('collaborators', '').split(',') if cid.isdigit()]
            collaborators = User.objects.filter(id__in=collaborator_ids)
            artwork.collaborators.set(collaborators.exclude(id=request.user.id))

            return JsonResponse({
                'success': True,
                'artwork_id': artwork.id,
                'image_url': artwork.image.url if artwork.image else None
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    else:  # GET request
        context = {
            'artwork': artwork,
            'collaborators': User.objects.exclude(id=request.user.id)
        }
        return render(request, 'drawing/edit.html', context)

@login_required
def save_artwork(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled')
        canvas = request.POST.get('canvas', '{}')
        pk = request.POST.get('pk', '').strip()
        for file in request.FILES:
            print("File: ", file)
        # Handle PNG image upload
        image_file = request.FILES.get('image')

        print("image_file: ", image_file)

        if pk:  # If updating an existing artwork
            artwork = get_object_or_404(Artwork, id=pk, creator=request.user)
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
        return JsonResponse({'success': True, 'pk': artwork.id})

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
@login_required
def collaborate_artwork(request, pk):
    artwork = get_object_or_404(Artwork, id=pk)
    if request.user not in artwork.collaborators.all() and request.user != artwork.creator:
        return redirect('index')
    return render(request, 'drawing/collaborate.html', {'artwork: artwork'})


@login_required
def artwork_detail(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    
    # Check if user is creator or collaborator
    if request.user != artwork.creator and request.user not in artwork.collaborators.all():
        return redirect('gallery')
    
    context = {'artwork': artwork}
    return render(request, 'gallery/artwork_detail.html', context)

@login_required
def delete_artwork(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)

    if artwork.image:
        artwork.image.delete(save=False)

    artwork.delete()
    return redirect('gallery')
