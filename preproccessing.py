import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, MinMaxScaler

print("Starting preprocessing...")

# Load raw data
print("Loading CSV data...")
movies = pd.read_csv('movies_metadata.csv', low_memory=False)
print(f"Loaded {len(movies)} movies")

# Flatten genres from list of dicts to list of names
def extract_genre_names(genres_list):
    if isinstance(genres_list, str):
        import ast
        genres_list = ast.literal_eval(genres_list)
    if isinstance(genres_list, list):
        return [g['name'] for g in genres_list]
    return []

movies['genres_list'] = movies['genres'].apply(extract_genre_names)

# Handle missing data and convert budget to numeric
movies['budget'] = pd.to_numeric(movies['budget'], errors='coerce').fillna(0)
movies['adult'] = movies['adult'].fillna(False)

# Handle missing values in other key columns
movies['original_language'] = movies['original_language'].fillna('unknown')
movies['overview'] = movies['overview'].fillna('')

# One-hot encoding genres
mlb = MultiLabelBinarizer()
genre_features = mlb.fit_transform(movies['genres_list'])
genre_df = pd.DataFrame(genre_features, columns=mlb.classes_)

# Reset index to ensure proper alignment
movies = movies.reset_index(drop=True)
genre_df = genre_df.reset_index(drop=True)

# One-hot encoding original language
ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
language_features = ohe.fit_transform(movies[['original_language']])
# Convert column names to strings to avoid mixed type issues
language_columns = [str(col) for col in ohe.categories_[0]]
language_df = pd.DataFrame(language_features, columns=language_columns)
language_df = language_df.reset_index(drop=True)

# Normalize budget
scaler = MinMaxScaler()
movies['budget_norm'] = scaler.fit_transform(movies[['budget']])

# Combine features into a DataFrame
processed_df = pd.concat([
    movies[['id', 'original_title', 'overview', 'budget_norm', 'adult']], 
    genre_df,
    language_df
], axis=1)

# Save preprocessed data for Day 2
print("Saving preprocessed data...")
processed_df.to_csv('movies_preprocessed.csv', index=False)
print("Preprocessing complete! Data saved to movies_preprocessed.csv")

# —— Visualizations for Day 1 —— #
print("Creating visualizations...")

try:
    # Genre distribution bar plot
    genre_counts = processed_df[mlb.classes_].sum().sort_values(ascending=False)
    genre_counts.plot(kind='bar', figsize=(12,6), color='skyblue')
    plt.title('Movie Genre Distribution')
    plt.xlabel('Genre')
    plt.ylabel('Number of Movies')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Language distribution bar plot
    language_counts = processed_df[language_columns].sum()
    # Convert to numeric for proper sorting, then sort
    language_counts = language_counts.astype(float).sort_values(ascending=False)
    # Show only top 15 languages for better readability
    language_counts.head(15).plot(kind='bar', figsize=(12,5), color='salmon')
    plt.title('Top 15 Original Language Distribution')
    plt.xlabel('Language')
    plt.ylabel('Number of Movies')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Budget histogram
    plt.hist(processed_df['budget_norm'], bins=30, color='lightgreen')
    plt.title('Normalized Movie Budget Distribution')
    plt.xlabel('Normalized Budget')
    plt.ylabel('Frequency')
    plt.show()

    # Adult movies count plot
    processed_df['adult'].value_counts().plot(kind='bar', color='orange')
    plt.title('Adult Movie Count')
    plt.xlabel('Adult')
    plt.ylabel('Count')
    plt.xticks([0,1], ['False', 'True'], rotation=0)
    plt.show()
    
    print("Visualizations created successfully!")
    
except Exception as e:
    print(f"Note: Visualizations could not be displayed (this is normal in some environments): {e}")
    print("Data processing completed successfully - visualizations can be generated separately if needed.")
