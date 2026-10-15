# Card metrics: sunny-frontier (gpt/final_crop)

Reference norms by category, as the vision call classifies the 160 reference cards: median (middle half). Extent = the object's largest dimension as a share of the card.

| Category | Cards | Extent | Smallest margin | Room above | Detail lost at 66 px | Highlight share |
|---|---|---|---|---|---|---|
| C1 | 36 | 0.82 (0.76-0.87) | 0.08 (0.05-0.11) | 0.16 (0.11-0.18) | 8.46 (6.07-9.80) | 0.00 (0.00-0.04) |
| C2 | 20 | 0.85 (0.81-0.88) | 0.06 (0.04-0.09) | 0.13 (0.09-0.21) | 10.71 (7.99-15.06) | 0.02 (0.00-0.04) |
| C3 | 27 | 0.89 (0.83-0.93) | 0.05 (0.03-0.08) | 0.12 (0.09-0.20) | 11.79 (8.19-13.95) | 0.01 (0.00-0.04) |
| C4 | 46 | 0.85 (0.81-0.94) | 0.04 (0.00-0.08) | 0.14 (0.10-0.21) | 10.32 (7.44-13.03) | 0.03 (0.01-0.09) |

Our cards. A flag means the value is outside the reference middle half by more than a quarter of that range, or the vision call reads a different category than the plan. Highlight is shown for information only: white objects count as shine.

| Card | Name | Planned C | Seen C | Extent | Margin | Room above | Detail lost | Highlight | Flags |
|---|---|---|---|---|---|---|---|---|---|
| A01 | Cowboy Hat | C1 | C1 | 0.93 | 0.01 | 0.18 | 6.6 | 0.000 | too big, tight margins |
| A02 | Prickly Pal | C2 | C2 | 0.84 | 0.07 | 0.08 | 9.0 | 0.010 | - |
| A03 | Chow Time! | C1 | C1 | 0.88 | 0.04 | 0.05 | 11.4 | 0.000 | tight margins, little room above, fine detail lost |
| A04 | Coffee Pot | C3 | C3 | 0.84 | 0.07 | 0.07 | 10.7 | 0.020 | - |
| A05 | Lasso | C1 | C1 | 0.86 | 0.06 | 0.10 | 8.8 | 0.000 | - |
| A06 | Cowboy Boots | C2 | C2 | 0.88 | 0.05 | 0.07 | 14.7 | 0.003 | - |
| A07 | Saddle | C3 | C3 | 0.85 | 0.06 | 0.08 | 16.3 | 0.004 | fine detail lost |
| A08 | Windmill | C4 | C4 | 0.91 | 0.03 | 0.03 | 15.4 | 0.035 | little room above, fine detail lost |
| A09 | Horse Barn | C4 | C4 | 0.99 | 0.01 | 0.04 | 19.3 | 0.164 | too big, little room above, fine detail lost |
| A10 | Ranch Gate | C4 | C4 | 0.90 | 0.05 | 0.09 | 15.5 | 0.006 | fine detail lost |
| B01 | Sunbonnet | C1 | C1 | 0.83 | 0.04 | 0.13 | 10.0 | 0.028 | - |
| B02 | Flapjacks | C2 | C2 | 0.93 | 0.02 | 0.02 | 10.6 | 0.009 | too big, tight margins, little room above |
| B03 | Canteen | C1 | C1 | 0.81 | 0.06 | 0.06 | 13.5 | 0.004 | little room above, fine detail lost |
| B04 | Sunflower | C1 | C1 | 0.91 | 0.03 | 0.08 | 7.3 | 0.000 | too big, tight margins, little room above |
| B05 | Patchwork Quilt | C2 | C2 | 1.00 | 0.00 | 0.17 | 16.3 | 0.016 | too big, tight margins |
| B06 | Travel Trunk | C3 | C3 | 0.98 | 0.01 | 0.19 | 13.5 | 0.002 | too big, tight margins |
| B07 | Trail Guitar | C3 | C3 | 0.90 | 0.02 | 0.02 | 15.8 | 0.004 | tight margins, little room above, fine detail lost |
| B08 | Rock Arch | C4 | C4 | 1.00 | 0.00 | 0.09 | 8.8 | 0.023 | too big |
| B09 | Starry Camp | C4 | C4 | 0.84 | 0.00 | 0.06 | 11.6 | 0.001 | little room above |
| B10 | Covered Wagon | C4 | C4 | 0.85 | 0.07 | 0.09 | 14.6 | 0.066 | fine detail lost |
| C01 | Mail Pouch | C1 | C1 | 0.89 | 0.00 | 0.15 | 10.1 | 0.022 | tight margins |
| C02 | Prize Pie | C2 | C2 | 0.98 | 0.00 | 0.04 | 9.5 | 0.005 | too big, tight margins, little room above |
| C03 | Pickle Barrel | C2 | C2 | 0.87 | 0.04 | 0.08 | 11.3 | 0.002 | - |
| C04 | Lucky Horseshoe | C1 | C1 | 0.72 | 0.13 | 0.16 | 9.8 | 0.044 | small |
| C05 | Hoedown | C1 | C1 | 0.84 | 0.04 | 0.07 | 12.5 | 0.002 | little room above, fine detail lost |
| C06 | Anvil | C3 | C3 | 0.91 | 0.00 | 0.12 | 11.2 | 0.017 | tight margins |
| C07 | Cash Register | C3 | C3 | 0.96 | 0.00 | 0.11 | 16.8 | 0.016 | too big, tight margins, fine detail lost |
| C08 | General Store | C4 | C4 | 0.96 | 0.02 | 0.06 | 18.8 | 0.028 | little room above, fine detail lost |
| C09 | Schoolhouse | C4 | C4 | 0.86 | 0.02 | 0.02 | 19.8 | 0.077 | little room above, fine detail lost |
| C10 | Steam Train | C4 | C4 | 0.93 | 0.02 | 0.11 | 18.5 | 0.062 | fine detail lost |

Extent across these cards: median 0.89, middle half 0.85-0.94 (a narrower spread = more even sizes).

24 of 30 cards flagged.
