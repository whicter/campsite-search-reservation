# Usage Guide

How to use the Campsite Search application to find available campsites.

## Quick Start

1. Make sure both backend and frontend are running (see [SETUP.md](SETUP.md))
2. Open `http://localhost:3000` in your browser
3. Fill in the search form
4. View available date ranges

## Using the Search Form

### 1. Select Provider

Choose from the dropdown list:
- **Reserve California** ✓ (via camply)
- **Recreation.gov** ✓ (via camply)
- **Going To Camp** ✓ (via camply)
- **San Mateo County** (custom - example)

The ✓ indicates providers supported by camply. Others use custom crawlers.

### 2. Enter Campground Name

Enter the name or partial name of the campground:

**Examples:**
- "New Brighton"
- "Yosemite"
- "Big Sur"
- "Half Moon"

**Tips:**
- You don't need the exact name
- Partial matches work
- Case insensitive

**What happens:**
- System searches for matching campgrounds
- Uses the first match found
- If no match, you'll see an error

### 3. Specify Number of Nights

Enter how many nights you want to stay (1-14).

**Examples:**
- 2 nights = check-in Friday, check-out Sunday
- 3 nights = check-in Friday, check-out Monday

**Important:**
- Camply guarantees the same campsite for all nights
- You won't need to switch sites mid-stay

### 4. Click Search

The system will:
1. Find the campground ID
2. Scan the next 365 days
3. Check each possible date range
4. Return all available options

**This may take 1-2 minutes** depending on the provider and date range.

## Understanding Results

### Available Dates Found

You'll see cards showing:
- **Check-in date** (e.g., Mar 12, 2025)
- **Check-out date** (e.g., Mar 15, 2025)
- **Number of nights** badge

**Example Result:**
```
┌─────────────────────────────────┐
│  Check-in: Mar 12, 2025         │ 2 nights
│     →                            │
│  Check-out: Mar 14, 2025        │
└─────────────────────────────────┘
```

Each card represents a complete available booking.

### No Results

If no availability is found, you'll see:
- Why no results (no matching campground or no availability)
- Suggestions for what to try next

**Suggestions:**
- Try fewer nights
- Different campground
- Check back later (availability changes daily)

## Examples

### Example 1: Weekend at New Brighton State Beach

**Search:**
- Provider: `ReserveCalifornia`
- Campground: `New Brighton SB`
- Nights: `2`

**Results might show:**
- Apr 12-14, 2025
- Apr 19-21, 2025
- May 3-5, 2025
- etc.

### Example 2: Week-long Trip to Yosemite

**Search:**
- Provider: `RecreationDotGov`
- Campground: `Upper Pines`
- Nights: `7`

**Results might show:**
- Jun 15-22, 2025
- Jul 8-15, 2025
- Aug 20-27, 2025

### Example 3: Finding Campground ID First

If you're not sure about the exact campground name, use the camply CLI first:

```bash
camply campgrounds --provider ReserveCalifornia --search "Brighton"
```

This shows:
```
⛰  New Brighton SB: Northern End, CA (598)
⛰  New Brighton SB: Southern End, CA (597)
⛰  New Brighton SB: Group Camping, CA (596)
```

Then search with "New Brighton SB" in the UI.

## Tips & Tricks

### Finding the Right Campground

1. **Search on the provider's website first** to know the exact name
2. **Use camply CLI** to see available campgrounds:
   ```bash
   camply campgrounds --provider ReserveCalifornia --search "park name"
   ```

### Optimizing Search Time

- **Shorter stays = faster search** (fewer API calls)
- **Popular campgrounds** may take longer
- **Be patient** - searching 365 days can take 1-2 minutes

### Best Practices

1. **Start broad** - Search with general name, refine if needed
2. **Try variations** - "Big Sur" vs "Big Sur Campground"
3. **Check multiple providers** - Same park might be on different systems
4. **Search regularly** - Availability changes as people cancel

### Continuous Monitoring (Future Feature)

Currently, you need to manually re-run searches. Future versions will support:
- Email notifications
- Continuous monitoring
- Webhook alerts

For now, consider running searches periodically or using camply CLI's `--continuous` flag:

```bash
camply campsites \
  --provider ReserveCalifornia \
  --campground 598 \
  --start-date 2025-07-15 \
  --end-date 2025-07-17 \
  --notifications email \
  --continuous
```

## API Usage (Advanced)

You can also use the API directly:

### Get Providers
```bash
curl http://localhost:8000/api/providers
```

### Search Campgrounds
```bash
curl "http://localhost:8000/api/campgrounds?provider=ReserveCalifornia&search=New%20Brighton"
```

### Search Availability
```bash
curl -X POST http://localhost:8000/api/availability \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "ReserveCalifornia",
    "campground_id": "598",
    "nights": 2,
    "search_days": 365
  }'
```

## Common Questions

**Q: Why does search take so long?**
A: We're checking 365 days of availability. For 2 nights, that's ~363 API calls to the provider.

**Q: Can I search specific dates?**
A: Currently no. The system searches the next 365 days. We may add date filtering in the future.

**Q: Does this actually book the campsite?**
A: No! This only searches for availability. You'll need to book manually on the provider's website.

**Q: How often is availability updated?**
A: Real-time. Each search queries the provider's live system.

**Q: Can I search multiple campgrounds at once?**
A: Not yet. Search one campground at a time.

## Troubleshooting

**"No campgrounds found"**
- Check spelling
- Try partial name
- Use camply CLI to find exact name

**Search times out**
- Try fewer nights
- Check internet connection
- Provider system may be down

**Results seem wrong**
- Providers sometimes show conflicting availability
- Double-check on provider's official website before booking

## Next Steps

- Learn about [adding new providers](DEVELOPMENT.md)
- Understand the [architecture](README.md)
- Report issues on GitHub
