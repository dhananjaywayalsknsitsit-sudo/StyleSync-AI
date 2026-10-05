# A transparent rule-based styling recommender for the first release.
# You can later replace this module with a trained ML recommendation model.
OUTFITS = {
 "casual": [
  {"name":"Everyday Casual","items":"Plain T-shirt + blue jeans + white sneakers","reason":"Simple pieces that work for daily activities.","colors":"White, blue, grey"},
  {"name":"Smart Casual","items":"Polo T-shirt + chinos + loafers","reason":"A neat look for college events and casual meetings.","colors":"Navy, beige, white"},
  {"name":"Weekend Layer","items":"Overshirt + basic tee + dark jeans","reason":"Layering adds style while staying comfortable.","colors":"Olive, black, cream"}
 ],
 "formal": [
  {"name":"Office Classic","items":"Solid shirt + formal trousers + leather shoes","reason":"Clean and structured for formal occasions.","colors":"White, navy, charcoal"},
  {"name":"Business Casual","items":"Oxford shirt + chinos + loafers","reason":"Smart without looking overly formal.","colors":"Light blue, beige, brown"}
 ],
 "streetwear": [
  {"name":"Urban Layer","items":"Oversized tee + cargo pants + sneakers","reason":"Relaxed proportions create a streetwear look.","colors":"Black, olive, grey"},
  {"name":"Graphic Street","items":"Graphic tee + straight jeans + high-tops","reason":"A graphic top becomes the main focus.","colors":"Black, denim, red"}
 ],
 "ethnic": [
  {"name":"Festive Classic","items":"Kurta + straight pants + traditional footwear","reason":"A balanced outfit for festive occasions.","colors":"Cream, maroon, navy"},
  {"name":"Fusion Look","items":"Short kurta + jeans + minimal sneakers","reason":"Combines traditional and casual elements.","colors":"White, indigo, beige"}
 ]
}
def recommend(style):
    return OUTFITS.get(style, OUTFITS["casual"])
