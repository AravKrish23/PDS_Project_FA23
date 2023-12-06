function validateRegistration() {
    var name = document.forms["registrationForm"]["user_name"].value;
    var email = document.forms["registrationForm"]["user_email"].value;
    var password = document.forms["registrationForm"]["password"].value;
    var phone = document.forms["registrationForm"]["user_phone"].value;

    // Simple validation, you may enhance it based on your specific requirements
    if (name.trim() === "") {
        alert("Please enter your full name.");
        return false;
    }

    if (email.trim() === "") {
        alert("Please enter your email address.");
        return false;
    }

    // Add more validation for email format if needed

    if (password.trim() === "") {
        alert("Please enter a password.");
        return false;
    }

    // Add more password strength validation if needed

    if (phone.trim() === "") {
        alert("Please enter your phone number.");
        return false;
    }

    // Add more validation for phone number format if needed

    return true;
}
