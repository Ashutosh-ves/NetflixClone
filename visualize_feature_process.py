def visualize_feature_combination():
    """Create a visual representation of how features are combined"""
    
    print("🎬 VISUAL GUIDE: HOW MOVIE FEATURES ARE COMBINED")
    print("=" * 70)
    
    print("""
📝 MOVIE: "Toy Story" (Animation, Comedy, Family)
Overview: "A cowboy doll is profoundly threatened when a new spaceman figure supplants him as top toy"

┌─────────────────────────────────────────────────────────────────────┐
│                    FEATURE EXTRACTION PROCESS                      │
└─────────────────────────────────────────────────────────────────────┘

🔤 TEXT FEATURES (TF-IDF):
   Input: "A cowboy doll is profoundly threatened when a new spaceman..."
   ↓ TF-IDF Vectorizer (500 features)
   Output: [0.12, 0.00, 0.34, 0.00, 0.56, ..., 0.00, 0.23]
   Weight: ×1.0

🏷️  GENRE FEATURES (One-Hot):
   Input: Animation=1, Comedy=1, Family=1, Action=0, Drama=0, ...
   ↓ Already encoded
   Output: [1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
   Weight: ×3.0 (MOST IMPORTANT!)

🌍 LANGUAGE FEATURES (One-Hot):
   Input: English=1, French=0, Spanish=0, German=0, ...
   ↓ Already encoded  
   Output: [1, 0, 0, 0, 0, 0, 0, 0]
   Weight: ×0.5

🔢 NUMERICAL FEATURES (Scaled):
   Input: budget_norm=0.3, adult=0
   ↓ StandardScaler (mean=0, std=1)
   Output: [-0.85, -0.5]
   Weight: ×0.5

┌─────────────────────────────────────────────────────────────────────┐
│                      FEATURE CONCATENATION                         │
└─────────────────────────────────────────────────────────────────────┘

Final Vector = [Text Features] + [Genre Features] + [Language] + [Numerical]
             = [500 features] + [17 features]    + [8 features] + [2 features]
             = 527 total features per movie

Example final vector for Toy Story:
[0.12, 0.00, 0.34, ..., 3.0, 0.0, 3.0, 3.0, ..., 0.5, 0.0, ..., -0.85, -0.5]
 ↑                      ↑                        ↑              ↑
 Text features          Genre features           Language       Numerical
 (weighted ×1.0)        (weighted ×3.0)         (×0.5)         (×0.5)
""")

    print("""
┌─────────────────────────────────────────────────────────────────────┐
│                    SIMILARITY CALCULATION                          │
└─────────────────────────────────────────────────────────────────────┘

Given two movies A and B with feature vectors:
Movie A: [a₁, a₂, a₃, ..., a₅₂₇]
Movie B: [b₁, b₂, b₃, ..., b₅₂₇]

🔺 EUCLIDEAN DISTANCE:
   Formula: √[(a₁-b₁)² + (a₂-b₂)² + ... + (a₅₂₇-b₅₂₇)²]
   
   Problem: Sensitive to feature magnitude
   Example: If text features are large, they dominate the calculation
   
   Movie A: [100, 200, 1, 1, 1]  (large text values)
   Movie B: [10,  20,  1, 1, 1]  (small text values, same genres)
   Distance: √[(100-10)² + (200-20)² + 0² + 0² + 0²] = √[8100 + 32400] = 201.2
   → Movies seem very different despite same genres!

📐 COSINE SIMILARITY:
   Formula: (A·B) / (||A|| × ||B||)
   Where A·B = a₁×b₁ + a₂×b₂ + ... + a₅₂₇×b₅₂₇
   
   Advantage: Focuses on direction/pattern, not magnitude
   
   Same example:
   Movie A: [100, 200, 1, 1, 1]
   Movie B: [10,  20,  1, 1, 1]
   
   A·B = 100×10 + 200×20 + 1×1 + 1×1 + 1×1 = 1000 + 4000 + 3 = 5003
   ||A|| = √[100² + 200² + 1² + 1² + 1²] = √50003 ≈ 223.6
   ||B|| = √[10² + 20² + 1² + 1² + 1²] = √503 ≈ 22.4
   
   Cosine = 5003 / (223.6 × 22.4) ≈ 0.998
   → Movies are very similar! ✅
""")

    print("""
┌─────────────────────────────────────────────────────────────────────┐
│                         WHY IT WORKS                               │
└─────────────────────────────────────────────────────────────────────┘

🎯 FEATURE WEIGHTING STRATEGY:
   • Genres ×3.0: Most important for movie similarity
   • Text ×1.0: Important but shouldn't dominate
   • Language ×0.5: Less important (most movies are English)
   • Numerical ×0.5: Budget/adult flag are minor factors

🔍 COSINE SIMILARITY BENEFITS:
   ✅ Ignores vector magnitude (text length doesn't matter)
   ✅ Focuses on feature patterns (genre combinations)
   ✅ Works well with sparse features (many zeros in one-hot encoding)
   ✅ Range [-1, 1] is intuitive (1=identical, 0=orthogonal, -1=opposite)

📊 REAL EXAMPLE - TOY STORY RECOMMENDATIONS:
   Input: Toy Story [Animation=3, Comedy=3, Family=3, ...]
   
   Good matches (high cosine similarity):
   • Shrek [Animation=3, Comedy=3, Family=3, ...] → 0.95 similarity
   • Finding Nemo [Animation=3, Family=3, ...] → 0.89 similarity
   
   Poor matches (low cosine similarity):
   • The Conjuring [Horror=3, Thriller=3, ...] → 0.12 similarity
   • Titanic [Romance=3, Drama=3, ...] → 0.08 similarity
""")

def show_step_by_step_example():
    """Show a concrete step-by-step example"""
    
    print("\n" + "="*70)
    print("🔍 STEP-BY-STEP EXAMPLE: TOY STORY vs SHREK")
    print("="*70)
    
    print("""
🎬 TOY STORY:
   Text: "cowboy doll spaceman toy" → TF-IDF: [0.2, 0.0, 0.3, 0.4, ...]
   Genres: Animation=1, Comedy=1, Family=1 → [1,0,1,1,0,0,0,...] → ×3.0 → [3,0,3,3,0,0,0,...]
   Language: English=1 → [1,0,0,...] → ×0.5 → [0.5,0,0,...]
   Numerical: budget=0.3, adult=0 → scaled → [-0.8, -0.5] → ×0.5 → [-0.4, -0.25]
   
   Final vector: [0.2, 0.0, 0.3, 0.4, ..., 3, 0, 3, 3, 0, ..., 0.5, 0, ..., -0.4, -0.25]

🎬 SHREK:
   Text: "ogre princess fairy tale" → TF-IDF: [0.0, 0.1, 0.0, 0.2, ...]
   Genres: Animation=1, Comedy=1, Family=1 → [1,0,1,1,0,0,0,...] → ×3.0 → [3,0,3,3,0,0,0,...]
   Language: English=1 → [1,0,0,...] → ×0.5 → [0.5,0,0,...]
   Numerical: budget=0.6, adult=0 → scaled → [0.2, -0.5] → ×0.5 → [0.1, -0.25]
   
   Final vector: [0.0, 0.1, 0.0, 0.2, ..., 3, 0, 3, 3, 0, ..., 0.5, 0, ..., 0.1, -0.25]

🔢 COSINE SIMILARITY CALCULATION:
   Key insight: Both have [3, 0, 3, 3, 0, ...] for genres (weighted)
   Even though text features differ, the large genre values (3.0) dominate
   
   Dot product ≈ 0.2×0.0 + 0.0×0.1 + ... + 3×3 + 0×0 + 3×3 + 3×3 + ... ≈ 27
   (The genre similarities contribute most to the dot product)
   
   Result: High similarity (~0.95) because genres match perfectly!
""")

if __name__ == "__main__":
    visualize_feature_combination()
    show_step_by_step_example()
    
    print(f"\n💡 SUMMARY:")
    print("1. All feature types become numbers in one big vector")
    print("2. Genres get 3x weight because they're most important")
    print("3. Cosine similarity finds movies with similar 'patterns'")
    print("4. Genre matching dominates the similarity calculation")
    print("5. This is why Toy Story gets recommended other animated family films!")