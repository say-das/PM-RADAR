#!/bin/bash
# Collect RSS data locally and commit to repo for fallback system
# Usage: ./scripts/collect_and_commit.sh

set -e

cd "$(dirname "$0")/.."

echo "=========================================="
echo "PM Radar - Local Data Collection"
echo "=========================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run collection
echo "📡 Collecting RSS feeds..."
python3 -c "
import sys
sys.path.insert(0, '.')
from scripts.collect.rss_collector import RSSCollector
from datetime import datetime
import json

collector = RSSCollector()
articles = collector.collect(days_back=7)

# Save with today's date
date_str = datetime.now().strftime('%Y-%m-%d')
output_file = f'data/raw/{date_str}.json'

data = {'rss_articles': articles, 'reddit_posts': []}

with open(output_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f'\\n✓ Collected {len(articles)} articles')
print(f'✓ Saved to {output_file}')

# Count by category
telecom = sum(1 for a in articles if a.get('category') == 'telecom_fraud')
competitor = sum(1 for a in articles if a.get('category') == 'competitor')
general = len(articles) - telecom - competitor

print(f'\\n📊 Breakdown:')
print(f'  - Telecom fraud: {telecom}')
print(f'  - Competitor: {competitor}')
print(f'  - General: {general}')
print(f'\\nFile: {output_file}')
"

echo ""
echo "=========================================="
echo "🔍 Checking git status..."
git status --short data/raw/

echo ""
echo "=========================================="
read -p "Commit and push to repo? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    DATE=$(date +%Y-%m-%d)
    git add data/raw/${DATE}.json
    git commit -m "Add raw data for ${DATE} (for fallback system)

Collected locally to ensure fallback data available.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
    git push origin main
    echo ""
    echo "✅ Data committed and pushed!"
else
    echo ""
    echo "⚠️  Skipped commit. Run manually:"
    echo "   git add data/raw/*.json"
    echo "   git commit -m 'Add raw data for fallback'"
    echo "   git push"
fi

echo ""
echo "Done! This data will be available for fallback on April 30."
