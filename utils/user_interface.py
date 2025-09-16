#!/usr/bin/env python3
"""
User Content Interface for Lumsden Tourist Map
Provides command-line and programmatic interfaces for user content submission
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from utils.user_content import UserContentManager


class UserContentInterface:
    """Interface for users to submit content to the tourist map"""
    
    def __init__(self):
        """Initialize the user content interface"""
        self.manager = UserContentManager()
        print("🙋 Welcome to the Lumsden Tourist Map Community Contribution System!")
        
    def interactive_review_submission(self) -> Optional[int]:
        """Interactive command-line interface for submitting a review"""
        print("\n📝 Submit a Review")
        print("=" * 50)
        
        try:
            # Get POI information
            poi_types = ['attraction', 'accommodation', 'dining', 'activity']
            print(f"Available POI types: {', '.join(poi_types)}")
            poi_type = input("Enter POI type: ").strip().lower()
            
            if poi_type not in poi_types:
                print("❌ Invalid POI type")
                return None
            
            poi_id = int(input("Enter POI ID: ").strip())
            
            # Get user information
            user_name = input("Your name: ").strip()
            user_email = input("Your email (optional): ").strip() or None
            
            # Get review details
            rating = int(input("Rating (1-5): ").strip())
            if rating < 1 or rating > 5:
                print("❌ Rating must be between 1 and 5")
                return None
            
            review_text = input("Your review: ").strip()
            visit_date = input("Visit date (YYYY-MM-DD, optional): ").strip() or None
            
            # Submit review
            review_id = self.manager.submit_review(
                poi_id, poi_type, user_name, user_email, 
                rating, review_text, visit_date
            )
            
            print(f"✅ Review submitted successfully! Review ID: {review_id}")
            print("Your review is pending moderation and will appear once approved.")
            
            return review_id
            
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
            return None
        except Exception as e:
            print(f"❌ Error submitting review: {e}")
            return None
    
    def interactive_poi_submission(self) -> Optional[int]:
        """Interactive command-line interface for submitting a new POI or update"""
        print("\n🏪 Submit POI Information")
        print("=" * 50)
        
        try:
            # Get update type
            update_types = ['new', 'update', 'correction']
            print(f"Update types: {', '.join(update_types)}")
            update_type = input("Update type: ").strip().lower()
            
            if update_type not in update_types:
                print("❌ Invalid update type")
                return None
            
            # Get POI type
            poi_types = ['attraction', 'accommodation', 'dining', 'activity', 'facility']
            print(f"POI types: {', '.join(poi_types)}")
            poi_type = input("POI type: ").strip().lower()
            
            if poi_type not in poi_types:
                print("❌ Invalid POI type")
                return None
            
            # Get existing POI ID if updating
            poi_id = None
            if update_type in ['update', 'correction']:
                poi_id = int(input("Existing POI ID: ").strip())
            
            # Get user information
            user_name = input("Your name: ").strip()
            user_email = input("Your email (optional): ").strip() or None
            
            # Get POI data
            poi_data = {}
            poi_data['name'] = input("POI name: ").strip()
            poi_data['description'] = input("Description: ").strip()
            
            # Get coordinates for new POIs
            if update_type == 'new':
                poi_data['lat'] = float(input("Latitude: ").strip())
                poi_data['lon'] = float(input("Longitude: ").strip())
            
            # Optional fields
            poi_data['opening_hours'] = input("Opening hours (optional): ").strip() or None
            poi_data['phone'] = input("Phone number (optional): ").strip() or None
            poi_data['website'] = input("Website (optional): ").strip() or None
            poi_data['amenities'] = input("Amenities (optional): ").strip() or None
            poi_data['additional_info'] = input("Additional information (optional): ").strip() or None
            
            # Submit POI update
            update_id = self.manager.submit_poi_update(
                poi_type, update_type, user_name, user_email, poi_data, poi_id
            )
            
            print(f"✅ POI information submitted successfully! Update ID: {update_id}")
            print("Your submission is pending moderation and will be reviewed.")
            
            return update_id
            
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
            return None
        except Exception as e:
            print(f"❌ Error submitting POI: {e}")
            return None
    
    def interactive_tip_submission(self) -> Optional[int]:
        """Interactive command-line interface for submitting local tips"""
        print("\n💡 Share Local Knowledge")
        print("=" * 50)
        
        try:
            # Get tip category
            categories = ['access', 'seasonal', 'local_knowledge', 'safety', 'photography']
            print(f"Tip categories: {', '.join(categories)}")
            tip_category = input("Tip category: ").strip().lower()
            
            if tip_category not in categories:
                print("❌ Invalid tip category")
                return None
            
            # Get user information
            user_name = input("Your name: ").strip()
            
            # Get POI association (optional)
            poi_id = None
            poi_association = input("Associate with specific POI? (y/n): ").strip().lower()
            if poi_association == 'y':
                poi_id = int(input("POI ID: ").strip())
            
            # Get tip text
            tip_text = input("Your tip or local knowledge: ").strip()
            
            # Submit tip
            tip_id = self.manager.submit_tip(tip_category, user_name, tip_text, poi_id)
            
            print(f"✅ Tip submitted successfully! Tip ID: {tip_id}")
            print("Your tip is pending moderation and will help other visitors.")
            
            return tip_id
            
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
            return None
        except Exception as e:
            print(f"❌ Error submitting tip: {e}")
            return None
    
    def batch_import_reviews(self, review_file: str) -> int:
        """Import reviews from a JSON file"""
        try:
            with open(review_file, 'r') as f:
                reviews = json.load(f)
            
            imported_count = 0
            for review in reviews:
                try:
                    self.manager.submit_review(
                        review['poi_id'],
                        review['poi_type'],
                        review['user_name'],
                        review.get('user_email'),
                        review['rating'],
                        review['review_text'],
                        review.get('visit_date')
                    )
                    imported_count += 1
                except Exception as e:
                    print(f"Error importing review: {e}")
            
            print(f"✅ Imported {imported_count} reviews from {review_file}")
            return imported_count
            
        except Exception as e:
            print(f"❌ Error importing reviews: {e}")
            return 0
    
    def generate_sample_user_content(self) -> Dict[str, int]:
        """Generate sample user-generated content for demonstration"""
        print("\n🔄 Generating sample user content...")
        
        counts = {'reviews': 0, 'tips': 0, 'poi_updates': 0}
        
        # Sample reviews
        sample_reviews = [
            {
                'poi_id': 1, 'poi_type': 'attraction', 'user_name': 'Sarah M.',
                'user_email': 'sarah@example.com', 'rating': 5,
                'review_text': 'Absolutely stunning castle! The views from the walls are incredible. Highly recommend visiting in the morning when the light is best for photos.',
                'visit_date': '2024-07-15'
            },
            {
                'poi_id': 2, 'poi_type': 'attraction', 'user_name': 'John D.',
                'user_email': 'john@example.com', 'rating': 4,
                'review_text': 'Great heritage trail with informative signs. Easy walk suitable for families. Takes about 2 hours if you read all the information boards.',
                'visit_date': '2024-08-03'
            },
            {
                'poi_id': 1, 'poi_type': 'accommodation', 'user_name': 'Emma L.',
                'user_email': None, 'rating': 4,
                'review_text': 'Lovely traditional inn with excellent food. Rooms are comfortable and the staff are very helpful with local recommendations.',
                'visit_date': '2024-06-20'
            }
        ]
        
        for review in sample_reviews:
            self.manager.submit_review(**review)
            counts['reviews'] += 1
        
        # Sample local tips
        sample_tips = [
            {
                'poi_id': 1, 'tip_category': 'photography', 'user_name': 'Local Photographer',
                'tip_text': 'Best photos of Corgarff Castle are taken from the hill to the southeast around golden hour. There\'s a small parking area about 200m up the track.'
            },
            {
                'poi_id': None, 'tip_category': 'seasonal', 'user_name': 'Highland Guide',
                'tip_text': 'The area is particularly beautiful in early October when the heather is in full bloom and the trees are changing color. Perfect for hiking.'
            },
            {
                'poi_id': 3, 'tip_category': 'access', 'user_name': 'Local Walker',
                'tip_text': 'Forest walks can be muddy after rain. Waterproof boots recommended. There are wooden boardwalks on the main trails but side paths can be soggy.'
            }
        ]
        
        for tip in sample_tips:
            self.manager.submit_tip(**tip)
            counts['tips'] += 1
        
        # Sample POI update
        poi_update = {
            'poi_type': 'dining',
            'update_type': 'new',
            'user_name': 'Local Resident',
            'user_email': 'resident@lumsden.com',
            'poi_data': {
                'name': 'The Glenlivet Café',
                'description': 'Cozy local café serving homemade cakes and light lunches. Popular with cyclists and walkers.',
                'lat': 57.3180,
                'lon': -2.8800,
                'opening_hours': 'Tue-Sun: 9:00-16:00',
                'phone': '+44 1975 651999',
                'amenities': 'WiFi, Outdoor seating, Cycle parking',
                'additional_info': 'Dog-friendly, Local produce used'
            }
        }
        
        self.manager.submit_poi_update(**poi_update)
        counts['poi_updates'] += 1
        
        print(f"✅ Generated {counts['reviews']} reviews, {counts['tips']} tips, {counts['poi_updates']} POI updates")
        return counts
    
    def display_statistics(self):
        """Display user content statistics"""
        print("\n📊 Community Contribution Statistics")
        print("=" * 50)
        
        stats = self.manager.get_content_statistics()
        
        # Reviews
        print(f"Reviews: {stats.get('reviews', {})}")
        
        # Photos
        print(f"Photos: {stats.get('photos', {})}")
        
        # POI Updates
        print(f"POI Updates: {stats.get('poi_updates', {})}")
        
        # Tips
        print(f"Tips: {stats.get('tips', {})}")
        
        # Top Contributors
        print("\n🏆 Top Contributors:")
        for contributor in stats.get('top_contributors', []):
            print(f"  - {contributor['name']}: {contributor['contributions']} contributions")
    
    def run_interactive_menu(self):
        """Run the interactive command-line menu"""
        while True:
            print("\n🗺️ Lumsden Tourist Map - Community Contributions")
            print("=" * 60)
            print("1. Submit a review")
            print("2. Add/update POI information")
            print("3. Share local tip or knowledge")
            print("4. Generate sample content (demo)")
            print("5. View contribution statistics")
            print("6. Export user content to GeoJSON")
            print("7. Exit")
            
            try:
                choice = input("\nSelect an option (1-7): ").strip()
                
                if choice == '1':
                    self.interactive_review_submission()
                elif choice == '2':
                    self.interactive_poi_submission()
                elif choice == '3':
                    self.interactive_tip_submission()
                elif choice == '4':
                    self.generate_sample_user_content()
                elif choice == '5':
                    self.display_statistics()
                elif choice == '6':
                    geojson = self.manager.export_user_content_to_geojson()
                    output_path = Path("enhanced_data/user_contributions.geojson")
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_path, 'w') as f:
                        json.dump(geojson, f, indent=2)
                    
                    print(f"✅ User content exported to: {output_path}")
                    print(f"Features exported: {len(geojson['features'])}")
                elif choice == '7':
                    print("Thank you for contributing to the Lumsden Tourist Map! 👋")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-7.")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")


def main():
    """Main function to run the user content interface"""
    interface = UserContentInterface()
    interface.run_interactive_menu()


if __name__ == "__main__":
    main()