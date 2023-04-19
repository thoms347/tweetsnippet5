document.getElementById("login-form").addEventListener("submit", function(event) {
    event.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    // Validate the username and password
    if (username === "your-username" && password === "your-password") {
      alert("Login successful!");
      // Redirect to the dashboard or any other page
      window.location.href = "dashboard.html";
    } else {
        alert("Incorrect username or password.");
      }
    });