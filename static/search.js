const input = document.querySelector('#search-box'); // search bar
const suggestions = document.querySelector('.suggestions ul'); // suggestions list
const suggestionsContainer = document.querySelector('.suggestions') // suggestions container
const x = document.querySelectorAll('.x-button'); // buttons to delete artist
const musicForm = document.querySelector('#music-form'); // music button

input.value = ""; // Clear search box on page load

/* --------- Search Box Functions --------- */

function callbackFunc(response, input) {
	suggestions.innerHTML = ""
	// if search bar is empty, don't return anything
	if (!input) {
		response = [];
		suggestionsContainer.classList.add("hidden");
	}
	else {
		suggestionsContainer.classList.remove("hidden");
		for (let i = 0; i < response.length; i++) {
			let listItem = document.createElement("LI");
			listItem.innerHTML = response[i];
			suggestions.append(listItem);
		}
	}
	
}

let top3ArtistsArray = [];

/* Add clicked suggestion to the artist box */
function addSuggestion(e) {
	// Hide suggestions container
	suggestionsContainer.classList.add("hidden");

	// Add clicked result into search box
	input.value = e.target.innerText;
	suggestions.innerHTML = "";

	top3ArtistsArray.push(e.target.innerText);

	// Add clicked result into artist inputs
	if (top3ArtistsArray.length > 0) {
		let artistSlot = document.querySelector(`#artist_${top3ArtistsArray.length}`)
		artistSlot.value = e.target.innerText;
	}
}

/* Remove artist from the artist box */
function removeArtist(e) {
	// Remove the artist from the array
	let artist = e.target.previousSibling.previousSibling;
	let artistIndex = top3ArtistsArray.indexOf(artist.value);
	if (artistIndex != -1) {
		top3ArtistsArray.splice(artistIndex, 1);
		// Reorganize the artists
		for (let i = 0; i < 3; i++) {
			let artistSlot = document.querySelector(`#artist_${i + 1}`);
			if (top3ArtistsArray[i] === undefined) {
				artistSlot.value = "";
			}
			else {
				artistSlot.value = top3ArtistsArray[i];
			}
		}
	}
}

/* Ensure that the artist boxes are not empty */
function checkInputs(e) {
	for (let i = 0; i < 3; i++) {
		let artistSlot = document.querySelector(`#artist_${i + 1}`);
		if (artistSlot.value === "") {
			e.preventDefault();
			alert("Please make sure you add three artists!");
			return;
		}
	}
}

/* --------- Event Listeners --------- */
// Triggers every time the user types into the search box
input.addEventListener('keyup', (function(e) {
	e.preventDefault();

	// Set up dictionary with the input value and stringify it
	const dict = {'query' : e.target.value}
	const s = JSON.stringify(dict)

	// Send an AJAX request to app.py to retrieve an array of 10 artists from Spotify based on query
	$.ajax({
		url: '/artist-suggestions',
		type: 'POST',
		contentType: 'application/json',
		data: JSON.stringify(s),
		success: function(response) {
			callbackFunc(response, e.target.value);
		}
	});
}))

suggestionsContainer.addEventListener('click', addSuggestion); // Triggers on suggestion selection

// Triggers on delete button click
for (let i = 0; i < x.length; i++) {
	x[i].addEventListener('click', removeArtist);
} 

musicForm.addEventListener('submit', checkInputs)