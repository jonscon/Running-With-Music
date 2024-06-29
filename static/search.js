const searchBoxes = document.querySelectorAll('.artist-form-control'); // search bar
const suggestions = document.querySelectorAll('.suggestions'); // suggestions container
const x = document.querySelectorAll('.x-button'); // buttons to delete artist
const musicForm = document.querySelector('#music-form'); // music button

// input.value = ""; // Clear search box on page load

/* --------- Search Box Functions --------- */

function callbackFunc(response, input) {
	// Suggestions container for the specific input box
	let suggestionsContainer = input.nextElementSibling.nextElementSibling;

	// Clear the suggestions UL
	suggestionsContainer.firstElementChild.innerHTML = ""

	// if search bar is empty, don't return anything
	if (!input.value) {
		response = [];
		suggestionsContainer.classList.add("hidden");
	}
	else {
		suggestionsContainer.classList.remove("hidden");
		for (let i = 0; i < response.length; i++) {
			let listItem = document.createElement("LI");
			listItem.innerHTML = response[i];
			// Append to the suggestions UL
			suggestionsContainer.firstElementChild.append(listItem);
		}
	}
}


/* Add clicked suggestion to the artist box */
function addSuggestion(e) {
	// Hide suggestions container
	let suggestionsContainer = e.target.parentElement.parentElement;
	suggestionsContainer.classList.add("hidden");

	// Add clicked result into search box
	let artistInput = e.target.parentElement.parentElement.parentElement.firstElementChild;
	artistInput.value = e.target.innerText;
	suggestionsContainer.firstElementChild.innerHTML = "";
}

/* Remove artist from the artist box */
function removeArtist(e) {
	// Remove artist from search box
	let artist = e.target.previousElementSibling;
	artist.value = "";
	let suggestionsContainer = e.target.nextElementSibling;
	suggestionsContainer.classList.add("hidden");
}


/* Ensure that the artist boxes are not empty */
function checkInputs(e) {
	let top3ArtistsArray = []
	let isEmpty = false;
	let isDuplicate = false;

	// Ensure that artist boxes are not empty
	for (let i = 0; i < 3; i++) {
		if (searchBoxes[i].value === "") {
			isEmpty = true;
			break;
		}
		top3ArtistsArray.push(searchBoxes[i].value);
	}

	// Ensure that no duplicate artists are added ONLY after confirming all artists have been entered
	if (!isEmpty) {
		if (top3ArtistsArray[0] === top3ArtistsArray[1] || top3ArtistsArray[0] === top3ArtistsArray[2] || top3ArtistsArray[1] === top3ArtistsArray[2]) {
			isDuplicate = true;
		}
	}

	if (isEmpty) {
		e.preventDefault();
		alert("Please make sure you add three artists!");
	}
	else if (isDuplicate) {
		e.preventDefault();
		alert("You entered duplicate artists! Please enter unique artists.");
	}
}

/* --------- Event Listeners --------- */
// Triggers every time the user types into a search box
Array.from(searchBoxes).forEach(input => {
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
				callbackFunc(response, e.target);
			}
		});
	}))
})

// Triggers everytime a user clicks a suggested artist name
Array.from(suggestions).forEach(suggestionsBox => {
	suggestionsBox.addEventListener('click', addSuggestion); // Triggers on suggestion selection
});

// Triggers on delete button click
for (let i = 0; i < x.length; i++) {
	x[i].addEventListener('click', removeArtist);
} 

musicForm.addEventListener('submit', checkInputs)