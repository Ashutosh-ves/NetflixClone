// Mock movie database
const movies = [
    { id: 1, title: "Echoes in the Dark", icon: "🌙", genre: "thriller", year: 2024 },
    { id: 2, title: "Forest of Memories", icon: "🌲", genre: "drama", year: 2023 },
    { id: 3, title: "The Witness", icon: "👁️", genre: "mystery", year: 2024 },
    { id: 4, title: "Beneath the Surface", icon: "🌊", genre: "thriller", year: 2023 },
    { id: 5, title: "Shadow Play", icon: "🎭", genre: "drama", year: 2024 },
    { id: 6, title: "The Investigation", icon: "🔍", genre: "mystery", year: 2024 },
    { id: 7, title: "Static Dreams", icon: "⚡", genre: "scifi", year: 2023 },
    { id: 8, title: "Lost in the Mist", icon: "🌫️", genre: "horror", year: 2024 },
    { id: 9, title: "The Threshold", icon: "🚪", genre: "thriller", year: 2023 },
    { id: 10, title: "Night Vision", icon: "🌃", genre: "action", year: 2024 },
    { id: 11, title: "The Corporate Maze", icon: "💼", genre: "drama", year: 2024 },
    { id: 12, title: "Beyond the Void", icon: "🌌", genre: "scifi", year: 2023 },
    { id: 13, title: "Castle Chronicles", icon: "🏰", genre: "action", year: 2024 },
    { id: 14, title: "Time Travelers", icon: "⏰", genre: "scifi", year: 2023 },
    { id: 15, title: "Into the Unknown", icon: "🔦", genre: "mystery", year: 2024 },
    { id: 16, title: "The Midnight Horizon", icon: "🌅", genre: "thriller", year: 2024 },
    { id: 17, title: "Dark Secrets", icon: "🕵️", genre: "mystery", year: 2023 },
    { id: 18, title: "Neon Nights", icon: "🌆", genre: "action", year: 2024 },
    { id: 19, title: "The Last Stand", icon: "⚔️", genre: "action", year: 2024 },
    { id: 20, title: "Whispers in the Wind", icon: "🍃", genre: "drama", year: 2023 }
];

// Recommended movies (hardcoded selection)
const recommendedMovies = [
    movies[5], movies[2], movies[8], movies[15], movies[11], movies[7]
];

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
    card.innerHTML = `
        <div class="placeholder-img">${movie.icon}</div>
        <div class="content-title">${movie.title}</div>
    `;
    return card;
}

// Perform search
function performSearch() {
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

    // Filter movies
    let filteredMovies = movies.filter(movie => {
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