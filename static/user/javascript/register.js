function validateRegistration() {
    var name = document.forms["registrationForm"]["username"].value;
    var email = document.forms["registrationForm"]["email"].value;
    var password = document.forms["registrationForm"]["password"].value;
    var phone = document.forms["registrationForm"]["phone"].value;

    // Clear previous error messages
    document.getElementById("emailError").innerText = "";
    document.getElementById("passwordError").innerText = "";
    document.getElementById("phoneError").innerText = "";
    document.getElementById("errorMessages").innerText = ""; // Clear general error messages

    if (name.trim() === "") {
        showError("Please enter your full name.");
        return false;
    }

    if (email.trim() === "") {
        showError("Please enter your email address.");
        return false;
    } else if (!validateEmail(email)) {
        showError("Invalid email format");
        return false;
    }

    if (password.trim().length < 8 || /\s/.test(password)) {
        showError("Password must be at least 8 characters long and should not contain spaces");
        return false;
    } else if (!validatePassword(password)) {
        showError("Password must have 1 uppercase, 1 lowercase, 1 digit, and 1 special character");
        return false;
    }

    if (!/^[0-9()+-]+$/.test(phone)) {
        showError("Phone number should contain only digits and valid characters (+, -, (, ))");
        return false;
    } else if (phone.trim().length < 10 || phone.trim().length > 13) {
        showError("Invalid phone number length");
        return false;
    }

    return true;
}

function validateEmail(email) {
    var emailRegex = /\S+@\S+\.\S+/;
    return emailRegex.test(email);
}

function validatePassword(password) {
    var passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
}

function showError(message) {
    // Display error messages in the HTML
    document.getElementById("errorMessages").innerText = message;
}
