// Mock movie database
const movies = [
    { id: 1, title: "Echoes in the Dark", img: "https://m.media-amazon.com/images/M/MV5BYTUxZGIzZjItMTEzNC00YTNlLWEwZTItMzFhNzE4Zjk0YzEwXkEyXkFqcGc@._V1_QL75_UX190_CR0,4,190,281_.jpg", genre: "thriller", year: 2024 },
    { id: 2, title: "Forest of Memories", img: "https://m.media-amazon.com/images/I/71BsiS-OLxL._UF1000,1000_QL80_.jpg", genre: "drama", year: 2023 },
    { id: 3, title: "A Minecraft Movie", img: "https://upload.wikimedia.org/wikipedia/en/6/66/A_Minecraft_Movie_poster.jpg", genre: "action", year: 2025 },
    { id: 4, title: "Beneath the Surface", img: "https://m.media-amazon.com/images/M/MV5BYjZjYmQ1MGMtZjI4ZS00OWVkLWE0MzMtM2I5MTM3YmFkZGRiXkEyXkFqcGc@._V1_.jpg", genre: "thriller", year: 2023 },
    { id: 5, title: "Chainsaw Man – The Movie: Reze Arc", img: "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcSlacjk-N2t0Ool13mp3eZJAHGCfN-ce_J6qt6BsL08mYbzeJetpHS2kTjRzy8kZMVHdP_OnA", genre: "action", year: 2024 },
    
    { id: 6, title: "The Shawshank Redemption", img: "https://m.media-amazon.com/images/M/MV5BMDAyY2FhYjctNDc5OS00MDNlLThiMGUtY2UxYWVkNGY2ZjljXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg", genre: "drama", year: 1994 },
    { id: 7, title: "The Godfather", img: "https://m.media-amazon.com/images/M/MV5BNGEwYjgwOGQtYjg5ZS00Njc1LTk2ZGEtM2QwZWQ2NjdhZTE5XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg", genre: "drama", year: 1972 },
    { id: 8, title: "Dune", img: "https://upload.wikimedia.org/wikipedia/en/thumb/8/8e/Dune_%282021_film%29.jpg/250px-Dune_%282021_film%29.jpg", genre: "scifi", year: 2021 },
    { id: 9, title: "The Matrix", img: "https://upload.wikimedia.org/wikipedia/en/thumb/d/db/The_Matrix.png/250px-The_Matrix.png", genre: "scifi", year: 1999 },
    { id: 10, title: "Alita: Battle Angel", img: "https://m.media-amazon.com/images/M/MV5BYmZhZGQzM2MtMWEyZC00YTU1LTk4YTQtMTg3ZjEzM2U1NTkxXkEyXkFqcGc@._V1_.jpg", genre: "scifi", year: 2019 },

    { id: 11, title: "Jurassic World Rebirth", img: "https://m.media-amazon.com/images/M/MV5BMGM3ZmI3NzQtNzU5Yi00ZWI1LTg3YTAtNmNmNWIyMWFjZTBkXkEyXkFqcGc@._V1_.jpg", genre: "action", year: 2025 },
    { id: 12, title: "F1", img: "https://images.fandango.com/ImageRenderer/0/0/redesign/static/img/default_poster--dark-mode.png/0/images/masterrepository/Fandango/236966/F1MOVIE_VERT_Sunset_2764x4096_DOM.jpg", genre: "drama", year: 2025 },
    { id: 13, title: "Superman", img: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxGnS5AO1k3OpZnSm3tRpSE6QMwI6nD1wZAcbPrTsNa9FZQcBttmU_WNWdTX2IpZu2Dmca9g", genre: "action", year: 2025 },
    { id: 14, title: "Final Destination Bloodlines", img: "https://upload.wikimedia.org/wikipedia/en/thumb/a/ab/Final_Destination_Bloodlines_%282025%29_poster.jpg/250px-Final_Destination_Bloodlines_%282025%29_poster.jpg", genre: "horror", year: 2025 },
    { id: 15, title: "28 Years Later", img: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSE81vHnn-JyOKeU5eyAkaqEmY5zzv5MjZNetgS8dFFCIqwjLPYgbnhGJ_bjoUf97WP_URR", genre: "horror", year: 2025 }
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
        <img src="${movie.img}" alt="${movie.title}" />
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