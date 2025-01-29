from django.shortcuts import render, redirect, get_object_or_404
from drawing.models import Artwork
from django.contrib.auth.decorators import login_required

@login_required
def gallery(request):
    query = request.GET.get('q', '')
    active_tab = request.GET.get('active_tab', 'personal')
    
    base_query = Artwork.objects.filter(title__icontains=query)
    
    context = {
        'artworks': base_query.filter(creator=request.user),
        'collaborations': request.user.collaborations.filter(title__icontains=query),
        'game_artworks': base_query.filter(is_game_artwork=True),
        'active_tab': active_tab,
        'request': request
    }
    return render(request, 'gallery/gallery.html', context)


