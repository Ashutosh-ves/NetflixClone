// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Global variables
let allMovies = [];
let recommendedMovies = [];

// Default placeholder image for movies without posters
const DEFAULT_POSTER = 'https://via.placeholder.com/300x450/333/fff?text=No+Image';

// Load movies from backend on page load
async function loadMovies() {
    try {
        const response = await fetch(`${API_BASE_URL}/movies`);
        const data = await response.json();
        allMovies = data.movies || [];
        
        // Load random recommendations
        await loadRandomRecommendations();
        
    } catch (error) {
        console.error('Error loading movies:', error);
        // Fallback to mock data if backend is not available
        allMovies = getMockMovies();
        recommendedMovies = allMovies.slice(0, 6);
    }
}

// Load random recommendations from backend
async function loadRandomRecommendations() {
    try {
        const response = await fetch(`${API_BASE_URL}/recommend/random`);
        const data = await response.json();
        recommendedMovies = data.recommendations || [];
    } catch (error) {
        console.error('Error loading recommendations:', error);
        recommendedMovies = allMovies.slice(0, 6);
    }
}

// Mock data fallback
function getMockMovies() {
    return [
        { id: 1, title: "Echoes in the Dark", img: "https://m.media-amazon.com/images/M/MV5BYTUxZGIzZjItMTEzNC00YTNlLWEwZTItMzFhNzE4Zjk0YzEwXkEyXkFqcGc@._V1_QL75_UX190_CR0,4,190,281_.jpg", genre: "thriller", year: 2024 },
        { id: 2, title: "Forest of Memories", img: "https://m.media-amazon.com/images/I/71BsiS-OLxL._UF1000,1000_QL80_.jpg", genre: "drama", year: 2023 },
        { id: 3, title: "A Minecraft Movie", img: "https://upload.wikimedia.org/wikipedia/en/6/66/A_Minecraft_Movie_poster.jpg", genre: "action", year: 2025 },
        { id: 4, title: "Beneath the Surface", img: "https://m.media-amazon.com/images/M/MV5BYjZjYmQ1MGMtZjI4ZS00OWVkLWE0MzMtM2I5MTM3YmFkZGRiXkEyXkFqcGc@._V1_.jpg", genre: "thriller", year: 2023 },
        { id: 5, title: "Chainsaw Man – The Movie: Reze Arc", img: "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcSlacjk-N2t0Ool13mp3eZJAHGCfN-ce_J6qt6BsL08mYbzeJetpHS2kTjRzy8kZMVHdP_OnA", genre: "action", year: 2024 },
        { id: 6, title: "The Shawshank Redemption", img: "https://m.media-amazon.com/images/M/MV5BMDAyY2FhYjctNDc5OS00MDNlLThiMGUtY2UxYWVkNGY2ZjljXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg", genre: "drama", year: 1994 }
    ];
}

// Open search page
function openSearchPage() {
    document.body.classList.add('search-active');
    document.getElementById('searchPage').classList.add('active');
    document.getElementById('mainNav').style.display = 'none';
    document.getElementById('searchPageInput').focus();
    displayRecommended();
}

// Go back to home
function goHome() {
    document.body.classList.remove('search-active');
    document.getElementById('searchPage').classList.remove('active');
    document.getElementById('mainNav').style.display = 'flex';
    
    // Clear search
    document.getElementById('searchPageInput').value = '';
    document.getElementById('searchResultsSection').style.display = 'none';
    document.getElementById('noResultsSection').style.display = 'none';
}

// Display recommended movies
function displayRecommended() {
    const container = document.getElementById('recommendedContainer');
    container.innerHTML = '';
    
    recommendedMovies.forEach(movie => {
        const card = createMovieCard(movie);
        container.appendChild(card);
    });
}

// Create movie card element
function createMovieCard(movie) {
    const card = document.createElement('div');
    card.className = 'content-card';
    card.onclick = () => showMovieRecommendations(movie.id, movie.title);
    
    const imgSrc = movie.img || DEFAULT_POSTER;
    card.innerHTML = `
        <img src="${imgSrc}" alt="${movie.title}" onerror="this.src='${DEFAULT_POSTER}'" />
        <div class="content-title">${movie.title}</div>
        <div class="content-year">${movie.year || 'N/A'}</div>
    `;
    return card;
}

// Show recommendations for a specific movie
async function showMovieRecommendations(movieId, movieTitle) {
    try {
        const response = await fetch(`${API_BASE_URL}/recommend/${movieId}`);
        const data = await response.json();
        
        if (data.recommendations) {
            displayMovieRecommendations(movieTitle, data.recommendations);
        }
    } catch (error) {
        console.error('Error getting recommendations:', error);
        alert('Unable to load recommendations. Please try again.');
    }
}

// Display movie recommendations in a modal or section
function displayMovieRecommendations(movieTitle, recommendations) {
    // Create a simple modal for recommendations
    const modal = document.createElement('div');
    modal.className = 'recommendations-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Recommendations for "${movieTitle}"</h2>
                <button class="close-btn" onclick="closeRecommendationsModal()">&times;</button>
            </div>
            <div class="recommendations-grid">
                ${recommendations.map(movie => `
                    <div class="recommendation-card">
                        <img src="${movie.img || DEFAULT_POSTER}" alt="${movie.title}" onerror="this.src='${DEFAULT_POSTER}'" />
                        <div class="recommendation-info">
                            <h3>${movie.title}</h3>
                            <p class="recommendation-year">${movie.year}</p>
                            <p class="recommendation-overview">${movie.overview}</p>
                            ${movie.similarity_score ? `<p class="similarity-score">Match: ${(movie.similarity_score * 100).toFixed(1)}%</p>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
}

// Close recommendations modal
function closeRecommendationsModal() {
    const modal = document.querySelector('.recommendations-modal');
    if (modal) {
        modal.remove();
    }
}

// Perform search
async function performSearch() {
    const searchTerm = document.getElementById('searchPageInput').value.trim().toLowerCase();
    const filterGenre = document.getElementById('filterDropdown').value;
    
    const resultsContainer = document.getElementById('searchResultsContainer');
    const resultsSection = document.getElementById('searchResultsSection');
    const noResultsSection = document.getElementById('noResultsSection');
    const resultsCount = document.getElementById('resultsCount');
    
    resultsContainer.innerHTML = '';

    if (searchTerm === '') {
        resultsSection.style.display = 'none';
        noResultsSection.style.display = 'none';
        return;
    }

    try {
        // Search using backend API
        const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(searchTerm)}`);
        const data = await response.json();
        let filteredMovies = data.movies || [];
        
        // Apply genre filter if needed
        if (filterGenre !== 'all') {
            filteredMovies = filteredMovies.filter(movie => movie.genre === filterGenre);
        }

        if (filteredMovies.length === 0) {
            resultsSection.style.display = 'none';
            noResultsSection.style.display = 'block';
        } else {
            noResultsSection.style.display = 'none';
            resultsSection.style.display = 'block';
            resultsCount.textContent = `Found ${filteredMovies.length} result${filteredMovies.length !== 1 ? 's' : ''} for "${searchTerm}"`;
            
            filteredMovies.forEach(movie => {
                const card = createMovieCard(movie);
                resultsContainer.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Search error:', error);
        // Fallback to local search
        let filteredMovies = allMovies.filter(movie => {
            const matchesSearch = movie.title.toLowerCase().includes(searchTerm);
            const matchesGenre = filterGenre === 'all' || movie.genre === filterGenre;
            return matchesSearch && matchesGenre;
        });

        if (filteredMovies.length === 0) {
            resultsSection.style.display = 'none';
            noResultsSection.style.display = 'block';
        } else {
            noResultsSection.style.display = 'none';
            resultsSection.style.display = 'block';
            resultsCount.textContent = `Found ${filteredMovies.length} result${filteredMovies.length !== 1 ? 's' : ''} for "${searchTerm}"`;
            
            filteredMovies.forEach(movie => {
                const card = createMovieCard(movie);
                resultsContainer.appendChild(card);
            });
        }
    }
}

// Allow search on Enter key
document.getElementById('searchPageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        performSearch();
    }
});

// Real-time search as user types (optional)
document.getElementById('searchPageInput').addEventListener('input', function() {
    performSearch();
});

// Filter change triggers new search
document.getElementById('filterDropdown').addEventListener('change', function() {
    performSearch();
});

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    loadMovies();
});