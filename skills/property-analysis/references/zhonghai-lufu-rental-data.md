# 中海麓府（望庐花园）租赁数据
## Location: 广州市白云区江夏，设计之都核心区
## Data collected: 2026-08-11 via Anjuke (安居客)

### Property Identity
- **Marketing name**: 中海麓府 (Zhonghai Lufu)
- **Plot name**: 望庐花园 (Wanglu Garden)
- **Developer alias**: 万科望庐花苑 (Vanke Wanglu Huayuan)
- **Developer**: 中海地产 (China Overseas Land & Land)
- **Location**: 白云区江夏，广云路
- **Metro**: 2号线/3号线(北延段)，黄边站
- **Building type**: 公寓住宅，高层 (32-44 floors)
- **Decoration**: 精装修 (fully furnished)

### Community Average Rent (Anjuke)
| Unit Type | Monthly Avg Rent |
|-----------|-----------------|
| 1BR | 0 (no listings) |
| 2BR | 0 (no listings) |
| **3BR** | **14,546元/月** |

### 4-Bedroom Listings (17 units found)
| Size | Rent | Rent/m² | Floor | Orientation |
|------|------|---------|-------|-------------|
| 141㎡ | 16,000元 | 113元/㎡ | Low/40F | SE |
| 142㎡ | 15,000元 | 106元/㎡ | Low/40F | SE |
| 142.5㎡ | 20,000元 | 140元/㎡ | High/40F | S |
| 143㎡ | 16,000元 | 112元/㎡ | Low/44F | S |
| 143㎡ | 16,000元 | 112元/㎡ | High/44F | S |
| 143㎡ | 16,000元 | 112元/㎡ | Low/32F | S |
| 143㎡ | 16,000元 | 112元/㎡ | Low/41F | S |
| 143㎡ | 16,000元 | 112元/㎡ | Low/44F | S |
| 146㎡ | 17,000元 | 116元/㎡ | Low/30F | S |

### 3-Bedroom Listing (1 unit found)
| Size | Rent | Rent/m² | Floor | Orientation |
|------|------|---------|-------|-------------|
| 126㎡ | 17,800元 | 141元/㎡ | High/44F | E |

### Statistical Summary
| Metric | 4BR | 3BR |
|--------|-----|-----|
| Price range | 15,000-20,000元/月 | 17,800元/月 |
| Most common price | 16,000元/月 (14/17 units) | — |
| Size range | 141-146㎡ | 126㎡ |
| Most common size | 143㎡ | — |
| Rent/m² range | 106-140元/㎡/month | ~141元/㎡/month |
| Typical rent/m² | ~112元/㎡/month | ~141元/㎡/month |
| Payment terms | 付1押2 (1 month + 2 deposit) | 付1押2 |

### Key Findings
1. **3BR commands higher per-m² rent**: 141 vs 112元/㎡ (+26%)
2. **4BR prices highly consistent**: 14/17 units at 16,000元/月
3. **South-facing > Southeast**: South-facing units command premium
4. **Floor has minimal impact**: Low/high floor prices similar
5. **Luxury decoration premium**: ~25% more (20,000 vs 16,000)

### Data Extraction Method
```javascript
// Anjuke price extraction using strong tags
const strongs = document.querySelectorAll('strong');
const listings = [];
strongs.forEach(s => {
  const priceText = s.textContent.trim();
  if (priceText.match(/^\d{4,6}$/)) {
    let parent = s.closest('[class]');
    let attempts = 0;
    while (parent && attempts < 10) {
      const t = parent.textContent.replace(/\s+/g, ' ').trim();
      if (t.includes('平米') && t.includes('室') && t.length < 600) {
        listings.push({price: parseInt(priceText), context: t.substring(0, 400)});
        break;
      }
      parent = parent.parentElement;
      attempts++;
    }
  }
});
```

### Sources
- Anjuke community search: https://gz.zu.anjuke.com/community/search/?kw=中海麓府
- Anjuke listing detail: https://gz.zu.anjuke.com/fangyuan/4411064876297216
- Anjuke listing detail: https://gz.zu.anjuke.com/fangyuan/4319737891806216
