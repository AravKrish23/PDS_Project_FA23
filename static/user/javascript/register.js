function validateRegistration() {
    var name = document.forms["registrationForm"]["username"].value;
    var email = document.forms["registrationForm"]["email"].value;
    var password = document.forms["registrationForm"]["password"].value;
    var phone = document.forms["registrationForm"]["phone"].value;

    // Clear previous error messages
    document.getElementById("nameError").textContent = "";
    document.getElementById("emailError").textContent = "";
    document.getElementById("passwordError").textContent = "";
    document.getElementById("phoneError").textContent = "";
    document.getElementById("errorMessages").textContent = ""; // Clear general error messages

    if (name.trim() === "") {
        showError("nameError", "Please enter your full name.");
        return false;
    }

    if (email.trim() === "") {
        showError("emailError", "Please enter your email address.");
        return false;
    } else if (!validateEmail(email)) {
        showError("emailError", "Invalid email format");
        return false;
    }

    if (password.trim().length < 8) {
        showError("passwordError", "Password must be at least 8 characters long and should not contain spaces");
        return false;
    } 
    

    if (!/^\d+$/.test(phone)) {
        showError("phoneError", "Phone number should contain only digits");
        return false;
    } else if (phone.trim().length < 10 || phone.trim().length > 13) {
        showError("phoneError", "Invalid phone number length");
        return false;
    }
    

    // Assume registration is successful, and redirect to the home page
    redirectToHomePage();

    return true;
}

function showError(id, message) {
    // Display error messages in the HTML
    document.getElementById(id).textContent = message;
}

function redirectToHomePage() {
    // Replace this with the actual URL of your home page
    window.location.href = '/home';
}
