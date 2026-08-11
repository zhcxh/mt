# Chinese Real Estate Rental Yield Calculation

## Overview
When researching Chinese residential properties for investment analysis, rental yield calculation requires specific data points and understanding of market conventions.

## Key Data Points

| Chinese Term | English | Unit | Notes |
|--------------|---------|------|-------|
| 成交均价 | Transaction price per sqm | 元/㎡ | Actual sale price, most accurate |
| 挂牌均价 | Listing price per sqm | 元/㎡ | Asking price, 15-30% above transaction |
| 月租金 | Monthly rent | 元/月 | Total monthly rental income |
| 租金单价 | Rent per sqm | 元/㎡/月 | Monthly rent ÷ floor area |
| 租售比 | Price-to-rent ratio | months | Property price ÷ monthly rent |
| 租金回报率 | Rental yield | % | Annual rent ÷ property value × 100% |

## Calculation Methods

### Method 1: By Transaction Price (Most Accurate)
```
Annual Rent = Monthly Rent × 12
Rental Yield = (Annual Rent / (Transaction Price × Area)) × 100%
```

**Example**: 87㎡ unit, 23,569元/㎡ transaction price, 4,500元/月 rent
```
Annual Rent = 4,500 × 12 = 54,000元
Total Property Value = 23,569 × 87 = 2,050,503元
Rental Yield = 54,000 / 2,050,503 × 100% ≈ 2.63%
```

### Method 2: By Rent per Sqm (Quick Estimate)
```
Annual Rent per Sqm = Monthly Rent per Sqm × 12
Rental Yield = Annual Rent per Sqm / Transaction Price per Sqm × 100%
```

**Example**: 45元/㎡/月 rent, 23,569元/㎡ transaction price
```
Annual Rent = 45 × 12 = 540元/㎡
Rental Yield = 540 / 23,569 × 100% ≈ 2.29%
```

### Method 3: By Listing Price (Conservative)
Same formulas but use listing price instead of transaction price. Result will be lower (typically 1.5-2.0%).

### Method 4: Price-to-Rent Ratio (Months to Recoup)
```
Price-to-Rent Ratio = Property Price / Monthly Rent
```
Example: 2,050,503元 / 4,500元 = 456 months (38 years)
- Good: < 200 months (< 17 years)
- Average: 200-400 months (17-33 years)
- Expensive: > 400 months (> 33 years)

## Chinese Market Benchmarks (2024-2026)

| City Tier | Average Rental Yield | Examples |
|-----------|---------------------|----------|
| Tier 1 | 1.7-2.0% | Beijing, Shanghai, Guangzhou, Shenzhen |
| Tier 2 | 2.0-2.5% | Chengdu, Hangzhou, Wuhan, Nanjing |
| Tier 3-4 | 2.5-4.5% | Smaller cities |
| Guangzhou specifically | ~1.79% (2024 H1) | - |

## Baidu Search Query Patterns for Rental Data

```
{小区名} + 租金 + 月租
{小区名} + 租售比
{小区名} + 租金回报率
{小区名} + 出租
{板块名} + 租金 + 均价
{区域名} + 租金 + 均价
```

## Important Caveats

1. **Transaction price ≠ listing price**: 15-30% gap is typical
2. **Villas vs regular apartments**: Vastly different yields
3. **"N+1" flexible layouts**: May command premium rents
4. **Subway proximity**: Affects both price and rent positively
5. **Management fees (物业费)**: Reduce net yield by ~2-5元/㎡/month
6. **Property age**: Older properties may have lower prices but similar rents
7. **Floor/orientation**: Affects both price and rent
8. **Furniture**: Furnished units rent for 10-20% more

## Example Analysis Template

```markdown
## Rental Yield Analysis: {Property Name}

### Property Details
- Location: {Address}
- Area: {X}㎡
- Layout: {N}室{N}厅
- Year Built: {Year}

### Price Data
- Transaction Price: {X}元/㎡
- Listing Price: {Y}元/㎡
- Total Value: {Z}万元

### Rental Data
- Monthly Rent: {A}元/月
- Rent per Sqm: {B}元/㎡/月

### Yield Calculation
- Annual Rent: {C}元
- Rental Yield (transaction): {D}%
- Rental Yield (listing): {E}%
- Price-to-Rent Ratio: {F} months

### Comparison
- Property yield vs area average: {higher/lower}
- Property yield vs city average: {higher/lower}
- Investment rating: {1-5 stars}
```

## Pitfalls

1. **Always use transaction price for yield calculation**: Listing prices are inflated
2. **Check for management fees**: They reduce net yield
3. **Consider vacancy rate**: 1-2 months/year is typical
4. **Factor in maintenance**: Older properties need more maintenance
5. **Tax implications**: Rental income may be taxed
6. **Currency**: All figures in CNY (元/RMB)
