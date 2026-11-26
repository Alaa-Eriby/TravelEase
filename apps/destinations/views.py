from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from rest_framework import viewsets, permissions, filters
from apps.destinations.models import Country, City, Destination, Review, FavoriteDestination
from apps.destinations.serializers import (
    CountrySerializer, CitySerializer, DestinationSerializer,
    ReviewSerializer, FavoriteDestinationSerializer
)

def destination_list_view(request):
    query = request.GET.get('q', '').strip()
    country_id = request.GET.get('country')
    city_id = request.GET.get('city')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    destinations = Destination.objects.all().select_related('city', 'country')

    if query:
        destinations = destinations.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(popular_attractions__icontains=query) |
            Q(city__name__icontains=query) |
            Q(country__name__icontains=query)
        )

    if country_id:
        destinations = destinations.filter(country_id=country_id)

    if city_id:
        destinations = destinations.filter(city_id=city_id)

    if min_price:
        try:
            destinations = destinations.filter(estimated_cost__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            destinations = destinations.filter(estimated_cost__lte=float(max_price))
        except ValueError:
            pass

    countries = Country.objects.all()
    cities = City.objects.all()

    # User favorite IDs
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(request.user.favorites.values_list('destination_id', flat=True))

    return render(request, 'destinations/list.html', {
        'destinations': destinations,
        'countries': countries,
        'cities': cities,
        'selected_country': country_id,
        'selected_city': city_id,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'favorite_ids': favorite_ids,
    })


def destination_detail_view(request, pk):
    destination = get_object_or_404(Destination.objects.select_related('city', 'country'), pk=pk)
    packages = destination.packages.filter(is_active=True).select_related('agent')
    hotels = destination.hotels.all().prefetch_related('rooms')
    reviews = destination.reviews.filter(is_approved=True).select_related('user')
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteDestination.objects.filter(user=request.user, destination=destination).exists()

    return render(request, 'destinations/detail.html', {
        'destination': destination,
        'packages': packages,
        'hotels': hotels,
        'reviews': reviews,
        'is_favorite': is_favorite,
    })


@login_required
def toggle_favorite_view(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    fav = FavoriteDestination.objects.filter(user=request.user, destination=destination).first()
    if fav:
        fav.delete()
        messages.info(request, f"Removed {destination.name} from your favorites.")
    else:
        FavoriteDestination.objects.create(user=request.user, destination=destination)
        messages.success(request, f"Added {destination.name} to your favorites!")
    
    next_url = request.META.get('HTTP_REFERER') or f'/destinations/{destination.pk}/'
    return redirect(next_url)


@login_required
def add_review_view(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        if comment:
            Review.objects.create(
                user=request.user,
                destination=destination,
                rating=rating,
                comment=comment,
                is_approved=True
            )
            messages.success(request, "Thank you! Your review has been published.")
        else:
            messages.error(request, "Review comment cannot be empty.")
    return redirect('destinations:detail', pk=destination.pk)


# --- REST API ViewSets ---

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]


class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all().select_related('city', 'country')
    serializer_class = DestinationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'city__name', 'country__name', 'popular_attractions']
    ordering_fields = ['estimated_cost', 'created_at', 'name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.filter(is_approved=True)
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteDestinationViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteDestinationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavoriteDestination.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
