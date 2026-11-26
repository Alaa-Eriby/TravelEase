import os
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import CustomerProfile, TravelAgentProfile
from apps.destinations.models import Country, City, Destination, DestinationImage, Review, FavoriteDestination
from apps.packages.models import TravelPackage, PackageDeparture
from apps.hotels.models import Hotel, HotelRoom
from apps.bookings.models import PackageBooking, Traveler, HotelBooking, BookingStatus
from apps.payments.models import PaymentRecord
from apps.core.models import ContactMessage, AuditLog, Notification

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds realistic demonstration data for TravelEase academic evaluation'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding TravelEase demonstration database..."))

        # 1. Accounts
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@travelease.local',
                'first_name': 'Alexander',
                'last_name': 'Vance',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone': '+1 (555) 019-2831'
            }
        )
        admin_user.set_password('AdminPass123!')
        admin_user.save()

        # Agents
        agent_sarah, _ = User.objects.get_or_create(
            username='agent_sarah',
            defaults={
                'email': 'sarah.jenkins@travelease.local',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'role': User.Role.AGENT,
                'phone': '+1 (555) 302-9911'
            }
        )
        agent_sarah.set_password('AgentPass123!')
        agent_sarah.save()
        TravelAgentProfile.objects.get_or_create(
            user=agent_sarah,
            defaults={
                'agency_name': 'Alpine & European Escapes',
                'license_number': 'LIC-EUR-8891',
                'business_email': 'bookings@alpineescapes.local',
                'bio': 'Specialist in luxury European adventures and alpine treks for over 12 years.',
                'rating': Decimal('4.95')
            }
        )

        agent_marco, _ = User.objects.get_or_create(
            username='agent_marco',
            defaults={
                'email': 'marco.rossi@travelease.local',
                'first_name': 'Marco',
                'last_name': 'Rossi',
                'role': User.Role.AGENT,
                'phone': '+39 06 698 1234'
            }
        )
        agent_marco.set_password('AgentPass123!')
        agent_marco.save()
        TravelAgentProfile.objects.get_or_create(
            user=agent_marco,
            defaults={
                'agency_name': 'Mediterranean Horizons Ltd',
                'license_number': 'LIC-MED-4420',
                'business_email': 'info@medhorizons.local',
                'bio': 'Crafting unforgettable coastal journeys and cultural expeditions across the Mediterranean and Middle East.',
                'rating': Decimal('4.88')
            }
        )

        # Customers
        traveler_john, _ = User.objects.get_or_create(
            username='traveler_john',
            defaults={
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': User.Role.CUSTOMER,
                'phone': '+1 (555) 441-8890'
            }
        )
        traveler_john.set_password('TravelerPass123!')
        traveler_john.save()
        CustomerProfile.objects.get_or_create(
            user=traveler_john,
            defaults={
                'passport_number': 'USA-9988123A',
                'nationality': 'United States',
                'date_of_birth': date(1992, 5, 14),
                'address': '742 Evergreen Terrace, Springfield',
                'emergency_contact': 'Mary Doe (Mother)',
                'emergency_phone': '+1 (555) 441-8899'
            }
        )

        traveler_emma, _ = User.objects.get_or_create(
            username='traveler_emma',
            defaults={
                'email': 'emma.watson@example.co.uk',
                'first_name': 'Emma',
                'last_name': 'Watson',
                'role': User.Role.CUSTOMER,
                'phone': '+44 20 7946 0192'
            }
        )
        traveler_emma.set_password('TravelerPass123!')
        traveler_emma.save()
        CustomerProfile.objects.get_or_create(
            user=traveler_emma,
            defaults={
                'passport_number': 'GBR-4412098B',
                'nationality': 'United Kingdom',
                'date_of_birth': date(1995, 8, 22),
                'address': '221B Baker Street, London',
                'emergency_contact': 'George Watson (Brother)',
                'emergency_phone': '+44 20 7946 0190'
            }
        )

        # 2. Countries & Cities
        countries_data = [
            {'name': 'Switzerland', 'code': 'CHE', 'desc': 'Heart of the Alps featuring pristine lakes and alpine glaciers.'},
            {'name': 'Japan', 'code': 'JPN', 'desc': 'Harmonious blend of futuristic megacities and ancient shrines.'},
            {'name': 'France', 'code': 'FRA', 'desc': 'World-renowned art, cuisine, architecture, and romantic landscapes.'},
            {'name': 'United Arab Emirates', 'code': 'ARE', 'desc': 'Futuristic architecture, desert adventures, and lavish hospitality.'},
            {'name': 'Italy', 'code': 'ITA', 'desc': 'Cradle of the Renaissance, ancient ruins, and culinary excellence.'},
            {'name': 'Greece', 'code': 'GRC', 'desc': 'Aegean gems, sun-drenched islands, and classical history.'},
        ]
        created_countries = {}
        for c in countries_data:
            country_obj, _ = Country.objects.get_or_create(name=c['name'], defaults={'code': c['code'], 'description': c['desc']})
            created_countries[c['name']] = country_obj

        cities_data = [
            ('Interlaken', 'Switzerland'),
            ('Zurich', 'Switzerland'),
            ('Tokyo', 'Japan'),
            ('Kyoto', 'Japan'),
            ('Paris', 'France'),
            ('Dubai', 'United Arab Emirates'),
            ('Rome', 'Italy'),
            ('Santorini', 'Greece'),
        ]
        created_cities = {}
        for city_name, country_name in cities_data:
            city_obj, _ = City.objects.get_or_create(
                name=city_name,
                country=created_countries[country_name]
            )
            created_cities[city_name] = city_obj

        # 3. Destinations
        destinations_data = [
            {
                'name': 'Swiss Alps & Jungfrau Region',
                'city': 'Interlaken',
                'country': 'Switzerland',
                'desc': 'Discover the crown jewel of Europe with dramatic mountain peaks, panoramic cogwheel railways, and crystal-clear mountain lakes.',
                'attractions': 'Jungfraujoch Top of Europe, Lake Brienz cruise, Grindelwald First Cliff Walk, Trummelbach Falls',
                'cost': Decimal('1850.00'),
                'image_url': 'https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
            {
                'name': 'Tokyo Metropolis & Mount Fuji',
                'city': 'Tokyo',
                'country': 'Japan',
                'desc': 'Experience neon-lit Shibuya crossings, historic Asakusa Senso-ji temple, and breathtaking viewpoints of iconic Mount Fuji.',
                'attractions': 'Shibuya Crossing, Mount Fuji 5th Station, Senso-ji Temple, Akihabara Electric Town',
                'cost': Decimal('2100.00'),
                'image_url': 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
            {
                'name': 'Parisian Romance & Cultural Splendors',
                'city': 'Paris',
                'country': 'France',
                'desc': 'Stroll along the Seine, explore world-class art at the Louvre, and savor authentic French cuisine beneath the Eiffel Tower.',
                'attractions': 'Eiffel Tower, Louvre Museum, Seine River Cruise, Palace of Versailles, Montmartre',
                'cost': Decimal('1650.00'),
                'image_url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
            {
                'name': 'Dubai Skyline & Desert Safari Oasis',
                'city': 'Dubai',
                'country': 'United Arab Emirates',
                'desc': 'Immerse in unparalleled luxury, futuristic architecture, exhilarating red-dune safaris, and Arabian Gulf beaches.',
                'attractions': 'Burj Khalifa Observation Deck, Palm Jumeirah, Desert Dune Safari, Dubai Mall, Dubai Marina',
                'cost': Decimal('1450.00'),
                'image_url': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
            {
                'name': 'Eternal Rome & Ancient Wonders',
                'city': 'Rome',
                'country': 'Italy',
                'desc': 'Walk in the footsteps of emperors through the Colosseum, Roman Forum, Vatican Museums, and enchanting piazzas.',
                'attractions': 'Colosseum, Vatican City & Sistine Chapel, Trevi Fountain, Pantheon, Piazza Navona',
                'cost': Decimal('1550.00'),
                'image_url': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
            {
                'name': 'Santorini Caldera & Sunset Terraces',
                'city': 'Santorini',
                'country': 'Greece',
                'desc': 'Whitewashed villages perched high above the Aegean sea, iconic blue-domed churches, and world-famous Oia sunsets.',
                'attractions': 'Oia Sunset Point, Red Beach, Akrotiri Archaeological Site, Caldera Catamaran Cruise',
                'cost': Decimal('1750.00'),
                'image_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
        ]
        created_destinations = {}
        for d in destinations_data:
            dest_obj, _ = Destination.objects.get_or_create(
                name=d['name'],
                defaults={
                    'city': created_cities[d['city']],
                    'country': created_countries[d['country']],
                    'description': d['desc'],
                    'popular_attractions': d['attractions'],
                    'estimated_cost': d['cost'],
                    'image_url': d['image_url'],
                    'is_featured': d['featured']
                }
            )
            created_destinations[d['name']] = dest_obj

        # 4. Travel Packages
        packages_data = [
            {
                'title': 'Grand Swiss Alpine 7-Day Expedition',
                'agent': agent_sarah,
                'destination': created_destinations['Swiss Alps & Jungfrau Region'],
                'duration': 7,
                'price': Decimal('2299.00'),
                'desc': 'An all-inclusive 7-day voyage covering Jungfraujoch, Grindelwald First, scenic cogwheel trains, and luxury 4-star mountain lodge stays.',
                'included': 'Swiss Travel Pass, 4-Star Lodge Hotel, Daily Breakfast & Alpine Dinners, Certified Mountain Guide, Jungfraujoch Train Ticket',
                'excluded': 'International flights, Personal mountain gear, Travel insurance',
                'image_url': 'https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
            {
                'title': 'Tokyo Lights & Mount Fuji Serenity 8-Day Tour',
                'agent': agent_sarah,
                'destination': created_destinations['Tokyo Metropolis & Mount Fuji'],
                'duration': 8,
                'price': Decimal('2799.00'),
                'desc': 'Comprehensive Japanese journey blending futuristic technology in Akihabara with traditional tea ceremonies and Mount Fuji vistas.',
                'included': 'Shinkansen Bullet Train Pass, 4-Star Ginza Hotel, Daily Breakfast, Private Tea Ceremony, English-speaking Local Guide',
                'excluded': 'Lunch and non-included dinners, International airfare, Souvenirs',
                'image_url': 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
            {
                'title': 'Romantic Paris & Versailles 5-Day Escape',
                'agent': agent_sarah,
                'destination': created_destinations['Parisian Romance & Cultural Splendors'],
                'duration': 5,
                'price': Decimal('1899.00'),
                'desc': 'Curated Parisian getaway with skip-the-line Louvre access, Seine gourmet dinner cruise, and full-day Versailles excursion.',
                'included': '4-Star Boutique Hotel in Saint-Germain, Daily Breakfast, Seine Dinner Cruise, Priority Louvre & Eiffel Tower Tickets',
                'excluded': 'Airport transfers, Tips for guides, Optional excursions',
                'image_url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
            {
                'title': 'Ultimate Dubai Luxury & Desert Safari 6-Day Tour',
                'agent': agent_marco,
                'destination': created_destinations['Dubai Skyline & Desert Safari Oasis'],
                'duration': 6,
                'price': Decimal('1950.00'),
                'desc': '5-star Marina accommodation, VIP Burj Khalifa 148th floor access, red dune safari with BBQ dinner, and luxury yacht cruise.',
                'included': '5-Star Beach Resort Hotel, Daily Gourmet Breakfast, 4x4 Desert Safari, Burj Khalifa At The Top Sky, Private Yacht Cruise',
                'excluded': 'Tourism Dirham fee, Alcoholic beverages, Travel insurance',
                'image_url': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
            {
                'title': 'Classical Rome & Imperial Wonders 6-Day Odyssey',
                'agent': agent_marco,
                'destination': created_destinations['Rome Historic Wonders' if 'Rome Historic Wonders' in created_destinations else 'Eternal Rome & Ancient Wonders'],
                'duration': 6,
                'price': Decimal('1799.00'),
                'desc': 'Deep exploration of ancient Rome with archaeologist-led Colosseum underground access, Vatican Museums, and authentic Italian cooking classes.',
                'included': 'Central Historic Hotel, Daily Italian Breakfast, Colosseum & Vatican Skip-The-Line Access, Pasta Making Masterclass',
                'excluded': 'City tourist tax (payable at hotel), Flight tickets, Personal expenses',
                'image_url': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
            {
                'title': 'Santorini Sunset & Aegean Yachting 5-Day Retreat',
                'agent': agent_marco,
                'destination': created_destinations['Santorini Caldera & Sunset Terraces'],
                'duration': 5,
                'price': Decimal('2150.00'),
                'desc': 'Caldera-facing cliffside suites, semi-private luxury catamaran cruise with Greek buffet, and wine tasting tour.',
                'included': 'Caldera Cave Suite with Breakfast, Private Airport Transfers, Catamaran Sunset Cruise with BBQ, Santorini Wine Tour',
                'excluded': 'International flights, Ferry tickets between islands',
                'image_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=1000&q=80',
                'featured': True
            },
        ]

        created_packages = []
        today = timezone.now().date()
        for p in packages_data:
            pkg_obj, _ = TravelPackage.objects.get_or_create(
                title=p['title'],
                defaults={
                    'agent': p['agent'],
                    'destination': p['destination'],
                    'duration_days': p['duration'],
                    'price_per_person': p['price'],
                    'description': p['desc'],
                    'included_services': p['included'],
                    'excluded_services': p['excluded'],
                    'image_url': p['image_url'],
                    'is_featured': p['featured'],
                    'is_active': True
                }
            )
            created_packages.append(pkg_obj)

            # Create upcoming departures for each package
            for offset_weeks in [2, 4, 6, 8]:
                dep_date = today + timedelta(weeks=offset_weeks)
                ret_date = dep_date + timedelta(days=pkg_obj.duration_days)
                PackageDeparture.objects.get_or_create(
                    package=pkg_obj,
                    departure_date=dep_date,
                    defaults={
                        'return_date': ret_date,
                        'total_capacity': 20,
                        'booked_seats': 4 if offset_weeks == 2 else 0,
                    }
                )

        # 5. Hotels & Rooms
        hotels_data = [
            {
                'name': 'The Alpina Grand Lodge & Spa',
                'destination': created_destinations['Swiss Alps & Jungfrau Region'],
                'address': 'Hoheweg 115, 3800 Interlaken',
                'rating': 5,
                'desc': 'World-class 5-star alpine resort offering panoramic views of the Eiger and Jungfrau, heated infinity pool, and Michelin-starred dining.',
                'amenities': 'Indoor & Outdoor Pool, Full Spa & Wellness Center, High-Speed Wi-Fi, Mountain View Balconies, Gourmet Restaurant, Ski Storage',
                'phone': '+41 33 828 28 28',
                'email': 'concierge@alpinagrandlodge.local',
                'image_url': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1000&q=80',
                'featured': True,
                'rooms': [
                    ('Deluxe Alpine King Room', 'DELUXE', 2, Decimal('380.00'), 8, 'https://images.unsplash.com/photo-1591088398332-8a7791972843?auto=format&fit=crop&w=800&q=80'),
                    ('Panoramic Executive Mountain Suite', 'PRESIDENTIAL', 4, Decimal('750.00'), 4, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80'),
                    ('Standard Double Room', 'DOUBLE', 2, Decimal('260.00'), 12, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80'),
                ]
            },
            {
                'name': 'Tokyo Skyview Imperial Palace Hotel',
                'destination': created_destinations['Tokyo Metropolis & Mount Fuji'],
                'address': '1-1-1 Marunouchi, Chiyoda-ku, Tokyo',
                'rating': 5,
                'desc': 'Overlooking the serene Imperial Palace gardens, combining quintessential Japanese hospitality with cutting-edge luxury.',
                'amenities': 'Rooftop Sky Bar, Teppanyaki Restaurant, Luxury Spa, Fitness Center, 24/7 Concierge, Free Wi-Fi',
                'phone': '+81 3 3211 5211',
                'email': 'reservations@tokyoskyview.local',
                'image_url': 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1000&q=80',
                'featured': True,
                'rooms': [
                    ('Modern Imperial Double', 'DOUBLE', 2, Decimal('320.00'), 10, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80'),
                    ('Skyline View Suite', 'DELUXE', 3, Decimal('580.00'), 6, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80'),
                ]
            },
            {
                'name': 'Hôtel de la Seine & Gardens',
                'destination': created_destinations['Parisian Romance & Cultural Splendors'],
                'address': '52 Quai des Grands Augustins, 75006 Paris',
                'rating': 4,
                'desc': 'Charming 4-star boutique hotel in the historic Latin Quarter overlooking the Seine and Notre-Dame cathedral.',
                'amenities': 'Courtyard Breakfast Garden, French Bistro, Free Wi-Fi, Air Conditioning, Airport Shuttle',
                'phone': '+33 1 43 26 88 90',
                'email': 'bonjour@hoteldelaseine.local',
                'image_url': 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1000&q=80',
                'featured': True,
                'rooms': [
                    ('Classic French Room', 'DOUBLE', 2, Decimal('240.00'), 15, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80'),
                    ('Seine River View Balcony Suite', 'DELUXE', 2, Decimal('420.00'), 5, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80'),
                ]
            },
            {
                'name': 'The Royal Marina Palm Resort',
                'destination': created_destinations['Dubai Skyline & Desert Safari Oasis'],
                'address': 'The Palm Jumeirah Crescent, Dubai',
                'rating': 5,
                'desc': 'Ultra-luxurious beachfront resort featuring private white sandy beach, underwater dining, and world-class infinity pools.',
                'amenities': 'Private Beach Access, Infinity Pools, Water Sports, Michelin-Star Dining, Kids Club, Luxury Spa',
                'phone': '+971 4 426 2000',
                'email': 'info@royalmarinapalm.local',
                'image_url': 'https://images.unsplash.com/photo-1580674684081-7617fbf3d745?auto=format&fit=crop&w=1000&q=80',
                'featured': True,
                'rooms': [
                    ('Palm Sea View King Room', 'DOUBLE', 2, Decimal('450.00'), 20, 'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80'),
                    ('Royal Beachfront Family Suite', 'FAMILY', 5, Decimal('890.00'), 8, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80'),
                ]
            },
        ]

        created_rooms = []
        for h in hotels_data:
            hotel_obj, _ = Hotel.objects.get_or_create(
                name=h['name'],
                defaults={
                    'destination': h['destination'],
                    'address': h['address'],
                    'star_rating': h['rating'],
                    'description': h['desc'],
                    'amenities': h['amenities'],
                    'phone': h['phone'],
                    'email': h['email'],
                    'image_url': h['image_url'],
                    'is_featured': h['featured']
                }
            )
            for room_name, r_type, cap, price, total_cnt, img_url in h['rooms']:
                rm, _ = HotelRoom.objects.get_or_create(
                    hotel=hotel_obj,
                    name=room_name,
                    defaults={
                        'room_type': r_type,
                        'capacity': cap,
                        'price_per_night': price,
                        'total_rooms': total_cnt,
                        'image_url': img_url,
                        'is_active': True
                    }
                )
                created_rooms.append(rm)

        # 6. Sample Confirmed Bookings & Payments
        # John books the Swiss package
        first_pkg = created_packages[0]
        first_dep = first_pkg.departures.first()
        if first_dep and not PackageBooking.objects.filter(customer=traveler_john, departure=first_dep).exists():
            pkg_b = PackageBooking.objects.create(
                booking_reference="TE-PKG-DEMO-001",
                customer=traveler_john,
                departure=first_dep,
                travelers_count=2,
                unit_price=first_dep.current_price,
                total_price=first_dep.current_price * 2,
                status=BookingStatus.CONFIRMED,
                special_requests="Vegetarian meals requested on trains"
            )
            Traveler.objects.create(booking=pkg_b, first_name="John", last_name="Doe", passport_number="USA-9988123A", age=32, gender="M")
            Traveler.objects.create(booking=pkg_b, first_name="Mary", last_name="Doe", passport_number="USA-9988124B", age=30, gender="F")
            
            PaymentRecord.objects.create(
                transaction_id="TXN-SIM-DEMO-PKG1",
                user=traveler_john,
                booking_type=PaymentRecord.BookingType.PACKAGE,
                booking_reference=pkg_b.booking_reference,
                amount=pkg_b.total_price,
                status=PaymentRecord.PaymentStatus.SUCCESS,
                card_last_four="4242",
                is_demo_simulation=True,
                notes="Academic demonstration payment record"
            )

        # Emma books a Hotel
        first_room = created_rooms[0]
        ci_date = today + timedelta(days=20)
        co_date = ci_date + timedelta(days=4)
        if not HotelBooking.objects.filter(customer=traveler_emma, room=first_room).exists():
            htl_b = HotelBooking.objects.create(
                booking_reference="TE-HTL-DEMO-002",
                customer=traveler_emma,
                room=first_room,
                check_in=ci_date,
                check_out=co_date,
                guests_count=2,
                rooms_count=1,
                price_per_night=first_room.price_per_night,
                total_price=first_room.price_per_night * 4,
                status=BookingStatus.CONFIRMED,
                special_requests="High floor with quiet mountain view please"
            )
            PaymentRecord.objects.create(
                transaction_id="TXN-SIM-DEMO-HTL1",
                user=traveler_emma,
                booking_type=PaymentRecord.BookingType.HOTEL,
                booking_reference=htl_b.booking_reference,
                amount=htl_b.total_price,
                status=PaymentRecord.PaymentStatus.SUCCESS,
                card_last_four="8810",
                is_demo_simulation=True,
                notes="Academic demonstration payment record"
            )

        # 7. Reviews
        Review.objects.get_or_create(
            user=traveler_john,
            destination=created_destinations['Swiss Alps & Jungfrau Region'],
            defaults={
                'rating': 5,
                'comment': 'The Swiss Alps tour was absolutely breathtaking! Booking with TravelEase was seamless, from cogwheel train vouchers to the lodge check-in.',
                'is_approved': True
            }
        )
        Review.objects.get_or_create(
            user=traveler_emma,
            destination=created_destinations['Parisian Romance & Cultural Splendors'],
            defaults={
                'rating': 5,
                'comment': 'A magical weekend in Paris. The Seine river dinner cruise included in the package was the highlight of our anniversary trip.',
                'is_approved': True
            }
        )

        # 8. Favorites
        FavoriteDestination.objects.get_or_create(
            user=traveler_john,
            destination=created_destinations['Tokyo Metropolis & Mount Fuji']
        )
        FavoriteDestination.objects.get_or_create(
            user=traveler_emma,
            destination=created_destinations['Santorini Caldera & Sunset Terraces']
        )

        # 9. Contact Messages
        ContactMessage.objects.get_or_create(
            email='corporate@globaltech.com',
            subject='Corporate Group Booking for 25 travelers in Dubai',
            defaults={
                'name': 'David Richardson',
                'message': 'Hello TravelEase team, we are planning a company summit in Dubai next month and would like a custom quote for 25 attendees.',
                'is_read': False
            }
        )
        ContactMessage.objects.get_or_create(
            email='alice.m@travelblog.io',
            subject='Inquiry about Travel Agent partnership on Mediterranean packages',
            defaults={
                'name': 'Alice Moreau',
                'message': 'We love your platform interface and would like to integrate our regional southern France boutique tours.',
                'is_read': True
            }
        )

        # 10. Audit Logs & Notifications
        AuditLog.objects.create(
            user=admin_user,
            action="SYSTEM_SEEDED",
            target_model="Core",
            target_id="1",
            details="Seeded initial realistic demonstration data for academic presentation"
        )
        Notification.objects.create(
            recipient=traveler_john,
            title="Booking Confirmation",
            message="Your Swiss Alps Expedition reservation TE-PKG-DEMO-001 has been confirmed.",
            notification_type='booking',
            is_read=False
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("Credentials available:"))
        self.stdout.write("  Admin: admin / AdminPass123!")
        self.stdout.write("  Agent: agent_sarah / AgentPass123!")
        self.stdout.write("  Traveler: traveler_john / TravelerPass123!")
