from django.shortcuts import render, redirect, get_object_or_404
from drawing.models import Artwork
from django.contrib.auth.decorators import login_required

@login_required
def gallery(request):
    query = request.GET.get('q', '')
    
    personal = Artwork.objects.filter(creator=request.user, is_game_artwork=False)
    collaborations = Artwork.objects.filter(collaborators=request.user)
    game_artworks = Artwork.objects.filter(creator=request.user, is_game_artwork=True)
    
    if query:
        personal = personal.filter(title__icontains=query)
        collaborations = collaborations.filter(title__icontains=query)
        game_artworks = game_artworks.filter(title__icontains=query)
    
    context = {
        'artworks': personal,
        'collaborations': collaborations,
        'game_artworks': game_artworks,
        'query': query
    }
    return render(request, 'gallery/gallery.html', context)
    
