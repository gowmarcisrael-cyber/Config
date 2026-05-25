import os
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.listings.models import Images, Listing


class Command(BaseCommand):
    help = 'Créer des objets Listing de test dans la base de données.'

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'testuser@example.com',
            },
        )
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Utilisateur de test créé: testuser'))
        else:
            self.stdout.write('Utilisateur de test existant: testuser')

        sample_listings = [
            {
                'title': 'Appartement central avec balcon',
                'description': 'Bel appartement lumineux proche de toutes commodités.',
                'property_type': 'Appartement',
                'status': 'En vente',
                'price': 175000.00,
                'bathrooms': 2,
                'bedrooms': 3,
                'is_available': True,
                'city': 'Paris',
                'longitude': 2.352222,
                'latitude': 48.856614,
                'area': 75.00,
            },
            {
                'title': 'Maison familiale avec jardin',
                'description': 'Grande maison avec jardin et garage, idéale pour une famille.',
                'property_type': 'Maison',
                'status': 'En vente',
                'price': 325000.00,
                'bathrooms': 3,
                'bedrooms': 4,
                'is_available': True,
                'city': 'Lyon',
                'longitude': 4.835659,
                'latitude': 45.764043,
                'area': 120.00,
            },
            {
                'title': 'Local commercial au coeur de la ville',
                'description': 'Local spacieux avec vitrine, parfait pour commerce de détail.',
                'property_type': 'Local commercial',
                'status': 'A louer',
                'price': 2200.00,
                'bathrooms': 1,
                'bedrooms': 0,
                'is_available': True,
                'city': 'Marseille',
                'longitude': 5.36978,
                'latitude': 43.296482,
                'area': 95.00,
            },
            {
                'title': 'Terrain constructible calme',
                'description': 'Terrain plat et viabilisé dans un secteur résidentiel paisible.',
                'property_type': 'Terrain',
                'status': 'En vente',
                'price': 85000.00,
                'bathrooms': 0,
                'bedrooms': 0,
                'is_available': True,
                'city': 'Bordeaux',
                'longitude': -0.57918,
                'latitude': 44.837789,
                'area': 450.00,
            },
            {
                'title': 'Appartement studio moderne',
                'description': 'Studio neuf avec kitchenette, idéal pour étudiant ou jeune actif.',
                'property_type': 'Appartement',
                'status': 'Loué',
                'price': 640.00,
                'bathrooms': 1,
                'bedrooms': 1,
                'is_available': False,
                'city': 'Toulouse',
                'longitude': 1.444209,
                'latitude': 43.604652,
                'area': 28.00,
            },
            {
                'title': 'Appartement avec terrasse ensoleillée',
                'description': 'Appartement contemporain avec terrasse et vue dégagée.',
                'property_type': 'Appartement',
                'status': 'En vente',
                'price': 215000.00,
                'bathrooms': 2,
                'bedrooms': 2,
                'is_available': True,
                'city': 'Nice',
                'longitude': 7.261953,
                'latitude': 43.710173,
                'area': 68.00,
            },
            {
                'title': 'Maison de campagne rénovée',
                'description': 'Charme ancien avec jardin, idéale pour retraite paisible.',
                'property_type': 'Maison',
                'status': 'En vente',
                'price': 280000.00,
                'bathrooms': 2,
                'bedrooms': 3,
                'is_available': True,
                'city': 'Dijon',
                'longitude': 5.04148,
                'latitude': 47.322047,
                'area': 110.00,
            },
            {
                'title': 'Local professionnel avec parking',
                'description': 'Local moderne proche des transports, facile d’accès.',
                'property_type': 'Local commercial',
                'status': 'A louer',
                'price': 3200.00,
                'bathrooms': 1,
                'bedrooms': 0,
                'is_available': True,
                'city': 'Nantes',
                'longitude': -1.553621,
                'latitude': 47.218371,
                'area': 130.00,
            },
            {
                'title': 'Studio économique en centre-ville',
                'description': 'Petit studio bien situé, parfait pour une première acquisition.',
                'property_type': 'Appartement',
                'status': 'En vente',
                'price': 95000.00,
                'bathrooms': 1,
                'bedrooms': 1,
                'is_available': True,
                'city': 'Lille',
                'longitude': 3.057256,
                'latitude': 50.62925,
                'area': 30.00,
            },
            {
                'title': 'Villa moderne avec piscine',
                'description': 'Magnifique villa contemporaine avec grande piscine et jardin.',
                'property_type': 'Maison',
                'status': 'En vente',
                'price': 975000.00,
                'bathrooms': 4,
                'bedrooms': 5,
                'is_available': True,
                'city': 'Cannes',
                'longitude': 7.017369,
                'latitude': 43.552847,
                'area': 260.00,
            },
            {
                'title': 'Terrain agricole avec accès route',
                'description': 'Terrain idéal pour projet agricole ou potager.',
                'property_type': 'Terrain',
                'status': 'En vente',
                'price': 42000.00,
                'bathrooms': 0,
                'bedrooms': 0,
                'is_available': True,
                'city': 'Amiens',
                'longitude': 2.302043,
                'latitude': 49.894067,
                'area': 550.00,
            },
            {
                'title': 'Loft design en plein centre',
                'description': 'Loft spacieux avec hauteur sous plafond et grandes baies vitrées.',
                'property_type': 'Appartement',
                'status': 'A louer',
                'price': 1800.00,
                'bathrooms': 1,
                'bedrooms': 1,
                'is_available': True,
                'city': 'Bordeaux',
                'longitude': -0.57918,
                'latitude': 44.837789,
                'area': 85.00,
            },
            {
                'title': 'Résidence étudiante calme',
                'description': 'Studio fonctionnel avec services inclus et proche campus.',
                'property_type': 'Appartement',
                'status': 'A louer',
                'price': 720.00,
                'bathrooms': 1,
                'bedrooms': 1,
                'is_available': True,
                'city': 'Grenoble',
                'longitude': 5.724524,
                'latitude': 45.188529,
                'area': 25.00,
            },
            {
                'title': 'Duplex familial lumineux',
                'description': 'Duplex rénové avec deux chambres et balcon.',
                'property_type': 'Appartement',
                'status': 'Loué',
                'price': 1450.00,
                'bathrooms': 2,
                'bedrooms': 3,
                'is_available': False,
                'city': 'Reims',
                'longitude': 4.031696,
                'latitude': 49.258329,
                'area': 95.00,
            },
            {
                'title': 'Chalet montagnard près des pistes',
                'description': 'Chalet cosy dans les Alpes, idéal pour les vacances.',
                'property_type': 'Maison',
                'status': 'A louer',
                'price': 2600.00,
                'bathrooms': 2,
                'bedrooms': 4,
                'is_available': True,
                'city': 'Chamonix',
                'longitude': 6.869433,
                'latitude': 45.9237,
                'area': 140.00,
            },
            {
                'title': 'Bungalow bord de mer',
                'description': 'Bungalow cosy à deux pas de la plage avec vue panoramique.',
                'property_type': 'Maison',
                'status': 'En vente',
                'price': 450000.00,
                'bathrooms': 2,
                'bedrooms': 3,
                'is_available': True,
                'city': 'Biarritz',
                'longitude': -1.557678,
                'latitude': 43.483151,
                'area': 95.00,
            },
        ]

        images_root = os.path.join(settings.MEDIA_ROOT, 'listings', 'images')
        os.makedirs(images_root, exist_ok=True)

        for index, listing_data in enumerate(sample_listings, start=1):
            listing, created = Listing.objects.get_or_create(
                title=listing_data['title'],
                defaults={**listing_data, 'user': user},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Listing créé: {listing}'))
            else:
                self.stdout.write(f'Listing existant: {listing}')

                image_name = f'listing_{index}.jpg'
            image_rel_path = f'listings/images/{image_name}'
            if not listing.images.filter(image=image_rel_path).exists():
                image_path = os.path.join(images_root, image_name)
                if not os.path.exists(image_path):
                    self.stdout.write(self.style.WARNING(f'Image manquante: {image_path}'))
                Images.objects.get_or_create(
                    listing=listing,
                    image=image_rel_path,
                )
                self.stdout.write(self.style.SUCCESS(f'Image ajoutée pour {listing}'))
            else:
                self.stdout.write(f'Image déjà présente pour {listing}')

        self.stdout.write(self.style.SUCCESS('Import des listings de test terminé.'))
