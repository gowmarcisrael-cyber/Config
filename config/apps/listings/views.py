from django.shortcuts import render, redirect,get_object_or_404
from .models import Listing
from django.core.paginator import Paginator
from .forms import ListingForm
from django.contrib.auth.decorators import login_required
# Create your views here.
def home(request):
    listings = Listing.objects.all()[:6]
    context = {
        'listings':listings,
        'types':Listing.TYPES,
        'statuses':Listing.STATUS[:2]
        }
    return render(request,'listings/index.html',context=context)

def search(request):
    listings = Listing.objects.filter(is_available=True)

    status = request.GET.get('status')
    city = request.GET.get('city')
    property_type = request.GET.get('property_type')
    price_max = request.GET.get('price_max')

    if status:
        listings = listings.filter(status=status)
    if city:
        listings = listings.filter(city__icontains=city)
    if property_type:
        listings = listings.filter(property_type=property_type)
    if price_max:
        listings = listings.filter(price__lte=price_max)

    page = request.GET.get('page')
    listings = Paginator(listings, 6).get_page(page)
    
    context = {
        'listings': listings,
        'types': Listing.TYPES,
        'statuses': Listing.STATUS[:2],
        'filters': request.GET,
    }
    return render(request, 'listings/search.html', context=context)

def detail(request,id):
    listing = get_object_or_404(Listing,id=id)
    images = listing.images.all()
    similars = Listing.objects.filter(
        property_type=listing.property_type,
        city=listing.city
    ).exclude(id=listing.id)[:4]
    context = {
        'listing': listing,
        'images': images,
        'similars': similars
    }
    return render(request, 'listings/details.html', context=context)

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        images = request.FILES.getlist('images')
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            for image in images:
                listing.images.create(image=image)
            return redirect('listing-detail', id=listing.id)
    else:
        form = ListingForm()
    return render(request, 'listings/create.html', {'form': form})