import pandas as pd
import numpy as np

def test_original_model():
    """Test if the original model.py runs without errors"""
    print("🧪 Testing Original Model (model.py)")
    print("=" * 40)
    
    try:
        print("Running original model training...")
        
        # This will run the model.py script
        import subprocess
        result = subprocess.run(['python', 'model.py'], 
                              capture_output=True, 
                              text=True, 
                              timeout=60)
        
        if result.returncode == 0:
            print("✅ Original model trained successfully!")
            print("Output:")
            print(result.stdout)
            
            # Check if model files were created
            import os
            if os.path.exists('knn_model.joblib') and os.path.exists('tfidf_vectorizer.joblib'):
                print("✅ Model files created successfully!")
            else:
                print("⚠️  Model files not found")
                
        else:
            print("❌ Original model training failed!")
            print("Error:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Model training timed out (taking too long)")
    except Exception as e:
        print(f"❌ Error testing original model: {e}")

def compare_model_outputs():
    """Compare the outputs of original vs improved models"""
    print(f"\n📊 COMPARING MODEL OUTPUTS")
    print("=" * 40)
    
    try:
        # Load both models if they exist
        import joblib
        import os
        
        models_to_check = [
            ("Original Model", "knn_model.joblib", "tfidf_vectorizer.joblib"),
            ("Improved Model", "improved_knn_model.joblib", "improved_tfidf_vectorizer.joblib")
        ]
        
        for name, knn_file, tfidf_file in models_to_check:
            if os.path.exists(knn_file) and os.path.exists(tfidf_file):
                knn = joblib.load(knn_file)
                tfidf = joblib.load(tfidf_file)
                
                print(f"\n{name}:")
                print(f"  KNN neighbors: {knn.n_neighbors}")
                print(f"  KNN metric: {knn.metric}")
                print(f"  TF-IDF max features: {tfidf.max_features}")
                print(f"  TF-IDF vocabulary size: {len(tfidf.vocabulary_)}")
                
            else:
                print(f"\n{name}: ❌ Model files not found")
                
    except Exception as e:
        print(f"❌ Error comparing models: {e}")

if __name__ == "__main__":
    test_original_model()
    compare_model_outputs()
    
    print(f"\n💡 SUMMARY:")
    print("The original model.py should now work without the .values error")
    print("You can run both models to see the difference in recommendations:")