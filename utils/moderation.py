#!/usr/bin/env python3
"""
Content Moderation System for User-Generated Content
Provides tools for moderating and managing community contributions
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from utils.user_content import UserContentManager


class ContentModerator:
    """System for moderating user-generated content"""
    
    def __init__(self):
        """Initialize the content moderation system"""
        self.manager = UserContentManager()
        print("🛡️ Content Moderation System initialized")
    
    def display_pending_reviews(self) -> List[Dict]:
        """Display pending reviews for moderation"""
        pending_reviews = self.manager.get_pending_content('user_reviews')
        
        print(f"\n📝 Pending Reviews ({len(pending_reviews)})")
        print("=" * 60)
        
        for i, review in enumerate(pending_reviews, 1):
            print(f"\n{i}. Review ID: {review['id']}")
            print(f"   POI: {review['poi_type']} #{review['poi_id']}")
            print(f"   User: {review['user_name']} ({review['user_email'] or 'No email'})")
            print(f"   Rating: {review['rating']}/5")
            print(f"   Date: {review['visit_date'] or 'Not specified'}")
            print(f"   Review: {review['review_text']}")
            print(f"   Submitted: {review['created_at']}")
        
        return pending_reviews
    
    def display_pending_poi_updates(self) -> List[Dict]:
        """Display pending POI updates for moderation"""
        pending_updates = self.manager.get_pending_content('user_poi_updates')
        
        print(f"\n🏪 Pending POI Updates ({len(pending_updates)})")
        print("=" * 60)
        
        for i, update in enumerate(pending_updates, 1):
            print(f"\n{i}. Update ID: {update['id']}")
            print(f"   Type: {update['update_type']} {update['poi_type']}")
            print(f"   User: {update['user_name']} ({update['user_email'] or 'No email'})")
            print(f"   Name: {update['name']}")
            print(f"   Description: {update['description']}")
            
            if update['lat'] and update['lon']:
                print(f"   Location: {update['lat']:.4f}, {update['lon']:.4f}")
            
            if update['opening_hours']:
                print(f"   Hours: {update['opening_hours']}")
            
            if update['phone']:
                print(f"   Phone: {update['phone']}")
            
            if update['website']:
                print(f"   Website: {update['website']}")
            
            if update['amenities']:
                print(f"   Amenities: {update['amenities']}")
            
            if update['additional_info']:
                print(f"   Additional: {update['additional_info']}")
            
            print(f"   Submitted: {update['submitted_at']}")
        
        return pending_updates
    
    def display_pending_tips(self) -> List[Dict]:
        """Display pending tips for moderation"""
        pending_tips = self.manager.get_pending_content('user_tips')
        
        print(f"\n💡 Pending Tips ({len(pending_tips)})")
        print("=" * 60)
        
        for i, tip in enumerate(pending_tips, 1):
            print(f"\n{i}. Tip ID: {tip['id']}")
            print(f"   Category: {tip['tip_category']}")
            print(f"   User: {tip['user_name']}")
            
            if tip['poi_id']:
                print(f"   Associated POI: #{tip['poi_id']}")
            else:
                print(f"   General area tip")
            
            print(f"   Tip: {tip['tip_text']}")
            print(f"   Submitted: {tip['submitted_at']}")
        
        return pending_tips
    
    def moderate_content_interactive(self):
        """Interactive moderation interface"""
        while True:
            print("\n🛡️ Content Moderation Menu")
            print("=" * 40)
            print("1. Review pending reviews")
            print("2. Review pending POI updates")
            print("3. Review pending tips")
            print("4. View moderation statistics")
            print("5. Bulk approve safe content")
            print("6. Export approved content")
            print("7. Back to main menu")
            
            try:
                choice = input("\nSelect option (1-7): ").strip()
                
                if choice == '1':
                    self._moderate_reviews()
                elif choice == '2':
                    self._moderate_poi_updates()
                elif choice == '3':
                    self._moderate_tips()
                elif choice == '4':
                    self._show_moderation_stats()
                elif choice == '5':
                    self._bulk_approve_safe_content()
                elif choice == '6':
                    self._export_approved_content()
                elif choice == '7':
                    break
                else:
                    print("❌ Invalid choice. Please select 1-7.")
                    
            except KeyboardInterrupt:
                print("\nExiting moderation system...")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
    
    def _moderate_reviews(self):
        """Moderate pending reviews"""
        pending_reviews = self.display_pending_reviews()
        
        if not pending_reviews:
            print("✅ No pending reviews to moderate")
            return
        
        for review in pending_reviews:
            print(f"\n--- Moderating Review ID: {review['id']} ---")
            print(f"Review: {review['review_text']}")
            print(f"Rating: {review['rating']}/5")
            
            action = input("Action (approve/reject/skip): ").strip().lower()
            
            if action == 'approve':
                notes = input("Moderation notes (optional): ").strip()
                self.manager.moderate_content('user_reviews', review['id'], 'approved', notes)
                print("✅ Review approved")
                
            elif action == 'reject':
                notes = input("Reason for rejection: ").strip()
                self.manager.moderate_content('user_reviews', review['id'], 'rejected', notes)
                print("❌ Review rejected")
                
            elif action == 'skip':
                print("⏭️ Skipped")
                continue
            else:
                print("❓ Unknown action, skipping")
    
    def _moderate_poi_updates(self):
        """Moderate pending POI updates"""
        pending_updates = self.display_pending_poi_updates()
        
        if not pending_updates:
            print("✅ No pending POI updates to moderate")
            return
        
        for update in pending_updates:
            print(f"\n--- Moderating POI Update ID: {update['id']} ---")
            print(f"Type: {update['update_type']} {update['poi_type']}")
            print(f"Name: {update['name']}")
            print(f"Description: {update['description']}")
            
            action = input("Action (approve/reject/skip): ").strip().lower()
            
            if action == 'approve':
                notes = input("Moderation notes (optional): ").strip()
                self.manager.moderate_content('user_poi_updates', update['id'], 'approved', notes)
                print("✅ POI update approved")
                
            elif action == 'reject':
                notes = input("Reason for rejection: ").strip()
                self.manager.moderate_content('user_poi_updates', update['id'], 'rejected', notes)
                print("❌ POI update rejected")
                
            elif action == 'skip':
                print("⏭️ Skipped")
                continue
            else:
                print("❓ Unknown action, skipping")
    
    def _moderate_tips(self):
        """Moderate pending tips"""
        pending_tips = self.display_pending_tips()
        
        if not pending_tips:
            print("✅ No pending tips to moderate")
            return
        
        for tip in pending_tips:
            print(f"\n--- Moderating Tip ID: {tip['id']} ---")
            print(f"Category: {tip['tip_category']}")
            print(f"Tip: {tip['tip_text']}")
            
            action = input("Action (approve/reject/skip): ").strip().lower()
            
            if action == 'approve':
                notes = input("Moderation notes (optional): ").strip()
                self.manager.moderate_content('user_tips', tip['id'], 'approved', notes)
                print("✅ Tip approved")
                
            elif action == 'reject':
                notes = input("Reason for rejection: ").strip()
                self.manager.moderate_content('user_tips', tip['id'], 'rejected', notes)
                print("❌ Tip rejected")
                
            elif action == 'skip':
                print("⏭️ Skipped")
                continue
            else:
                print("❓ Unknown action, skipping")
    
    def _show_moderation_stats(self):
        """Show moderation statistics"""
        stats = self.manager.get_content_statistics()
        
        print("\n📊 Moderation Statistics")
        print("=" * 40)
        
        total_content = 0
        for content_type, status_counts in stats.items():
            if content_type == 'top_contributors':
                continue
            
            print(f"\n{content_type.replace('_', ' ').title()}:")
            for status, count in status_counts.items():
                print(f"  {status.title()}: {count}")
                total_content += count
        
        print(f"\nTotal content items: {total_content}")
        
        pending_total = sum(stats.get(ct, {}).get('pending', 0) for ct in ['reviews', 'photos', 'poi_updates', 'tips'])
        approved_total = sum(stats.get(ct, {}).get('approved', 0) for ct in ['reviews', 'photos', 'poi_updates', 'tips'])
        
        if total_content > 0:
            approval_rate = (approved_total / total_content) * 100
            print(f"Approval rate: {approval_rate:.1f}%")
            print(f"Pending items: {pending_total}")
    
    def _bulk_approve_safe_content(self):
        """Bulk approve content that appears safe (basic automation)"""
        print("\n🚀 Bulk Approve Safe Content")
        print("This will auto-approve content based on basic safety criteria...")
        
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Bulk approval cancelled")
            return
        
        approved_count = 0
        
        # Auto-approve reviews with rating 3-5 and reasonable length
        pending_reviews = self.manager.get_pending_content('user_reviews')
        for review in pending_reviews:
            if (review['rating'] >= 3 and 
                len(review['review_text']) >= 10 and 
                len(review['review_text']) <= 500 and
                not any(word in review['review_text'].lower() for word in ['spam', 'fake', 'scam'])):
                
                self.manager.moderate_content('user_reviews', review['id'], 'approved', 'Auto-approved: Safe content')
                approved_count += 1
        
        # Auto-approve tips with reasonable length and safe categories
        safe_categories = ['access', 'seasonal', 'local_knowledge', 'photography']
        pending_tips = self.manager.get_pending_content('user_tips')
        for tip in pending_tips:
            if (tip['tip_category'] in safe_categories and
                len(tip['tip_text']) >= 10 and
                len(tip['tip_text']) <= 300):
                
                self.manager.moderate_content('user_tips', tip['id'], 'approved', 'Auto-approved: Safe content')
                approved_count += 1
        
        print(f"✅ Bulk approved {approved_count} content items")
    
    def _export_approved_content(self):
        """Export all approved content for integration"""
        output_dir = Path("enhanced_data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export user content as GeoJSON
        geojson = self.manager.export_user_content_to_geojson()
        
        geojson_path = output_dir / "user_contributions.geojson"
        with open(geojson_path, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        # Export statistics
        stats = self.manager.get_content_statistics()
        stats_path = output_dir / "user_content_stats.json"
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✅ Exported user content to:")
        print(f"   GeoJSON: {geojson_path}")
        print(f"   Statistics: {stats_path}")
        print(f"   Features: {len(geojson['features'])}")
    
    def auto_moderate_content(self, strict: bool = False):
        """Automated content moderation with configurable strictness"""
        print(f"\n🤖 Running automated moderation (strict={strict})")
        
        moderated_count = 0
        
        # Moderate reviews
        pending_reviews = self.manager.get_pending_content('user_reviews')
        for review in pending_reviews:
            if self._is_review_safe(review, strict):
                self.manager.moderate_content('user_reviews', review['id'], 'approved', 'Auto-approved')
                moderated_count += 1
            elif self._is_review_unsafe(review):
                self.manager.moderate_content('user_reviews', review['id'], 'rejected', 'Auto-rejected: unsafe content')
                moderated_count += 1
        
        # Moderate tips
        pending_tips = self.manager.get_pending_content('user_tips')
        for tip in pending_tips:
            if self._is_tip_safe(tip, strict):
                self.manager.moderate_content('user_tips', tip['id'], 'approved', 'Auto-approved')
                moderated_count += 1
            elif self._is_tip_unsafe(tip):
                self.manager.moderate_content('user_tips', tip['id'], 'rejected', 'Auto-rejected: unsafe content')
                moderated_count += 1
        
        print(f"✅ Auto-moderated {moderated_count} content items")
        return moderated_count
    
    def _is_review_safe(self, review: Dict, strict: bool = False) -> bool:
        """Check if a review is safe for auto-approval"""
        text = review['review_text'].lower()
        
        # Basic safety checks
        if len(text) < 5 or len(text) > 1000:
            return False
        
        # Rating checks
        if review['rating'] < 2:
            return False if strict else True
        
        # Content checks
        unsafe_words = ['spam', 'fake', 'scam', 'hate', 'offensive']
        if any(word in text for word in unsafe_words):
            return False
        
        # Length and coherence
        if strict:
            return len(text) >= 20 and review['rating'] >= 3
        else:
            return True
    
    def _is_review_unsafe(self, review: Dict) -> bool:
        """Check if a review should be auto-rejected"""
        text = review['review_text'].lower()
        
        unsafe_words = ['spam', 'fake', 'scam', 'hate', 'offensive', 'advertisement', 'buy now']
        if any(word in text for word in unsafe_words):
            return True
        
        # Check for extremely short or long content
        if len(text) < 3 or len(text) > 2000:
            return True
        
        return False
    
    def _is_tip_safe(self, tip: Dict, strict: bool = False) -> bool:
        """Check if a tip is safe for auto-approval"""
        text = tip['tip_text'].lower()
        
        # Length checks
        if len(text) < 10 or len(text) > 500:
            return False
        
        # Category checks
        safe_categories = ['access', 'seasonal', 'local_knowledge', 'photography', 'safety']
        if tip['tip_category'] not in safe_categories:
            return False if strict else True
        
        return True
    
    def _is_tip_unsafe(self, tip: Dict) -> bool:
        """Check if a tip should be auto-rejected"""
        text = tip['tip_text'].lower()
        
        unsafe_words = ['spam', 'advertisement', 'buy', 'click here']
        if any(word in text for word in unsafe_words):
            return True
        
        if len(text) < 5 or len(text) > 1000:
            return True
        
        return False


def main():
    """Main function for running content moderation"""
    moderator = ContentModerator()
    moderator.moderate_content_interactive()


if __name__ == "__main__":
    main()