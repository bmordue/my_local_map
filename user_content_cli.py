#!/usr/bin/env python3
"""
User Content Management CLI Tool
Command-line interface for managing user-generated content
"""

import sys
import argparse
import json
from pathlib import Path
from utils.user_content import UserContentManager
from utils.user_interface import UserContentInterface
from utils.moderation import ContentModerator


def submit_review_command(args):
    """Submit a review via command line"""
    manager = UserContentManager()
    
    review_id = manager.submit_review(
        poi_id=args.poi_id,
        poi_type=args.poi_type,
        user_name=args.user_name,
        user_email=args.user_email,
        rating=args.rating,
        review_text=args.review_text,
        visit_date=args.visit_date
    )
    
    print(f"✅ Review submitted successfully! Review ID: {review_id}")
    return 0


def submit_poi_command(args):
    """Submit a POI update via command line"""
    manager = UserContentManager()
    
    poi_data = {
        'name': args.name,
        'description': args.description,
        'lat': args.lat,
        'lon': args.lon,
        'opening_hours': args.opening_hours,
        'phone': args.phone,
        'website': args.website,
        'amenities': args.amenities,
        'additional_info': args.additional_info
    }
    
    # Remove None values
    poi_data = {k: v for k, v in poi_data.items() if v is not None}
    
    update_id = manager.submit_poi_update(
        poi_type=args.poi_type,
        update_type=args.update_type,
        user_name=args.user_name,
        user_email=args.user_email,
        poi_data=poi_data,
        poi_id=args.poi_id
    )
    
    print(f"✅ POI update submitted successfully! Update ID: {update_id}")
    return 0


def submit_tip_command(args):
    """Submit a tip via command line"""
    manager = UserContentManager()
    
    tip_id = manager.submit_tip(
        tip_category=args.category,
        user_name=args.user_name,
        tip_text=args.tip_text,
        poi_id=args.poi_id
    )
    
    print(f"✅ Tip submitted successfully! Tip ID: {tip_id}")
    return 0


def moderate_command(args):
    """Moderate content via command line"""
    manager = UserContentManager()
    
    if args.table not in ['user_reviews', 'user_photos', 'user_poi_updates', 'user_tips']:
        print(f"❌ Invalid table: {args.table}")
        return 1
    
    if args.status not in ['pending', 'approved', 'rejected']:
        print(f"❌ Invalid status: {args.status}")
        return 1
    
    success = manager.moderate_content(args.table, args.content_id, args.status, args.notes)
    
    if success:
        print(f"✅ Content {args.content_id} in {args.table} set to {args.status}")
        return 0
    else:
        print(f"❌ Failed to moderate content {args.content_id}")
        return 1


def stats_command(args):
    """Display content statistics"""
    manager = UserContentManager()
    stats = manager.get_content_statistics()
    
    print("\n📊 User Content Statistics")
    print("=" * 40)
    
    # Display stats by type
    for content_type, status_counts in stats.items():
        if content_type == 'top_contributors':
            continue
        
        print(f"\n{content_type.replace('_', ' ').title()}:")
        for status, count in status_counts.items():
            print(f"  {status.title()}: {count}")
    
    # Display top contributors
    print("\n🏆 Top Contributors:")
    for contributor in stats.get('top_contributors', []):
        print(f"  - {contributor['name']}: {contributor['contributions']} contributions")
    
    return 0


def export_command(args):
    """Export user content to GeoJSON"""
    manager = UserContentManager()
    
    geojson = manager.export_user_content_to_geojson(args.area)
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"✅ Exported {len(geojson['features'])} user contributions to: {output_path}")
    return 0


def interactive_command(args):
    """Run interactive interface"""
    interface = UserContentInterface()
    interface.run_interactive_menu()
    return 0


def moderate_interactive_command(args):
    """Run interactive moderation"""
    moderator = ContentModerator()
    moderator.moderate_content_interactive()
    return 0


def auto_moderate_command(args):
    """Run automated moderation"""
    moderator = ContentModerator()
    moderated_count = moderator.auto_moderate_content(strict=args.strict)
    print(f"✅ Auto-moderated {moderated_count} content items")
    return 0


def generate_sample_command(args):
    """Generate sample user content"""
    interface = UserContentInterface()
    counts = interface.generate_sample_user_content()
    
    print(f"Generated sample content:")
    for content_type, count in counts.items():
        print(f"  {content_type}: {count}")
    
    return 0


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="User Content Management for Lumsden Tourist Map",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Submit a review
  python user_content_cli.py submit-review --poi-id 1 --poi-type attraction \\
    --user-name "John Doe" --rating 5 --review-text "Amazing place!"
  
  # Submit a new POI
  python user_content_cli.py submit-poi --poi-type dining --update-type new \\
    --user-name "Local" --name "New Café" --description "Great coffee" \\
    --lat 57.3167 --lon -2.8833
  
  # Submit a tip
  python user_content_cli.py submit-tip --category local_knowledge \\
    --user-name "Guide" --tip-text "Best views at sunset"
  
  # Moderate content
  python user_content_cli.py moderate --table user_reviews --content-id 1 \\
    --status approved --notes "Good quality review"
  
  # View statistics
  python user_content_cli.py stats
  
  # Run interactive interface
  python user_content_cli.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Submit review command
    review_parser = subparsers.add_parser('submit-review', help='Submit a user review')
    review_parser.add_argument('--poi-id', type=int, required=True, help='POI ID')
    review_parser.add_argument('--poi-type', required=True, choices=['attraction', 'accommodation', 'dining', 'activity'], help='POI type')
    review_parser.add_argument('--user-name', required=True, help='User name')
    review_parser.add_argument('--user-email', help='User email (optional)')
    review_parser.add_argument('--rating', type=int, required=True, choices=[1,2,3,4,5], help='Rating (1-5)')
    review_parser.add_argument('--review-text', required=True, help='Review text')
    review_parser.add_argument('--visit-date', help='Visit date (YYYY-MM-DD)')
    review_parser.set_defaults(func=submit_review_command)
    
    # Submit POI command
    poi_parser = subparsers.add_parser('submit-poi', help='Submit POI information')
    poi_parser.add_argument('--poi-type', required=True, choices=['attraction', 'accommodation', 'dining', 'activity', 'facility'], help='POI type')
    poi_parser.add_argument('--update-type', required=True, choices=['new', 'update', 'correction'], help='Update type')
    poi_parser.add_argument('--user-name', required=True, help='User name')
    poi_parser.add_argument('--user-email', help='User email (optional)')
    poi_parser.add_argument('--poi-id', type=int, help='Existing POI ID (for updates)')
    poi_parser.add_argument('--name', required=True, help='POI name')
    poi_parser.add_argument('--description', required=True, help='POI description')
    poi_parser.add_argument('--lat', type=float, help='Latitude (required for new POIs)')
    poi_parser.add_argument('--lon', type=float, help='Longitude (required for new POIs)')
    poi_parser.add_argument('--opening-hours', help='Opening hours')
    poi_parser.add_argument('--phone', help='Phone number')
    poi_parser.add_argument('--website', help='Website URL')
    poi_parser.add_argument('--amenities', help='Amenities')
    poi_parser.add_argument('--additional-info', help='Additional information')
    poi_parser.set_defaults(func=submit_poi_command)
    
    # Submit tip command
    tip_parser = subparsers.add_parser('submit-tip', help='Submit a local tip')
    tip_parser.add_argument('--category', required=True, choices=['access', 'seasonal', 'local_knowledge', 'safety', 'photography'], help='Tip category')
    tip_parser.add_argument('--user-name', required=True, help='User name')
    tip_parser.add_argument('--tip-text', required=True, help='Tip text')
    tip_parser.add_argument('--poi-id', type=int, help='Associated POI ID (optional)')
    tip_parser.set_defaults(func=submit_tip_command)
    
    # Moderate command
    moderate_parser = subparsers.add_parser('moderate', help='Moderate content')
    moderate_parser.add_argument('--table', required=True, choices=['user_reviews', 'user_photos', 'user_poi_updates', 'user_tips'], help='Content table')
    moderate_parser.add_argument('--content-id', type=int, required=True, help='Content ID')
    moderate_parser.add_argument('--status', required=True, choices=['pending', 'approved', 'rejected'], help='New status')
    moderate_parser.add_argument('--notes', default='', help='Moderation notes')
    moderate_parser.set_defaults(func=moderate_command)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show content statistics')
    stats_parser.set_defaults(func=stats_command)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export user content to GeoJSON')
    export_parser.add_argument('--area', default='lumsden', help='Area name (default: lumsden)')
    export_parser.add_argument('--output', default='enhanced_data/user_contributions.geojson', help='Output file path')
    export_parser.set_defaults(func=export_command)
    
    # Interactive commands
    interactive_parser = subparsers.add_parser('interactive', help='Run interactive interface')
    interactive_parser.set_defaults(func=interactive_command)
    
    mod_interactive_parser = subparsers.add_parser('moderate-interactive', help='Run interactive moderation')
    mod_interactive_parser.set_defaults(func=moderate_interactive_command)
    
    # Auto-moderate command
    auto_mod_parser = subparsers.add_parser('auto-moderate', help='Run automated moderation')
    auto_mod_parser.add_argument('--strict', action='store_true', help='Use strict moderation criteria')
    auto_mod_parser.set_defaults(func=auto_moderate_command)
    
    # Generate sample command
    sample_parser = subparsers.add_parser('generate-sample', help='Generate sample user content')
    sample_parser.set_defaults(func=generate_sample_command)
    
    # Parse arguments and run command
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())