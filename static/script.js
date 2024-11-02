document.addEventListener('DOMContentLoaded', function () {
    const bookForm = document.getElementById('bookForm');
    const bookListDiv = document.getElementById('bookList');
    const sendButton = document.getElementById('sendButton');
    const userMessageInput = document.getElementById('userMessage');
    const chatBox = document.getElementById('chatBox');
    
    // Function to fetch books from the server
    function fetchBooks() {
        fetch('/get_books')
            .then(response => response.json())
            .then(books => {
                bookListDiv.innerHTML = '';
                books.forEach(book => {
                    const bookDiv = document.createElement('div');
                    bookDiv.className = 'book-item';
                    bookDiv.innerHTML = `
                        <h5>${book.title}</h5>
                        <a href="/uploads/${book.pdf}" target="_blank">Download PDF</a>
                        <button class="btn btn-danger btn-sm delete-button" data-id="${book._id}">Delete</button>
                    `;
                    bookListDiv.appendChild(bookDiv);
                });
            });
    }

    // Event listener for form submission
    bookForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const formData = new FormData(bookForm);
        fetch('/add_book', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            fetchBooks(); // Refresh book list
            bookForm.reset(); // Clear the form
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Event listener for deleting books
    bookListDiv.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-button')) {
            const bookId = event.target.getAttribute('data-id');
            fetch(`/delete_book/${bookId}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    fetchBooks(); // Refresh book list
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    });

    // Function to handle chatbot interactions
    function respondToUser(input) {
        const userMessage = input.toLowerCase();
        let response = "I'm not sure how to respond to that.";

        // Basic keyword matching for responses
        if (userMessage.includes("hello") || userMessage.includes("hi")) {
            response = "Hello! How can I help you today?";
        } else if (userMessage.includes("books") || userMessage.includes("library")) {
            response = "We have a great collection of books. What do you want to know?";
        } else if (userMessage.includes("help")) {
            response = "You can ask me about the books available or how to register.";
        } else if (userMessage.includes("register")) {
            response = "You can register by clicking on the register link on the login page.";
        }

        // Return the response
        return response;
    }

    // Event listener for sending messages in the chatbot
    sendButton.addEventListener('click', function () {
        const userMessage = userMessageInput.value.trim();
        if (userMessage) {
            // Display user message in chat box
            chatBox.innerHTML += `<div><strong>You:</strong> ${userMessage}</div>`;

            // Get bot response
            const botResponse = respondToUser(userMessage);
            chatBox.innerHTML += `<div><strong>LibraryBot:</strong> ${botResponse}</div>`;

            // Clear the input field
            userMessageInput.value = '';
            chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
        }
    });
    
    // Fetch initial book list
    fetchBooks();
});
