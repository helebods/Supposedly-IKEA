function togglePassword(eye, inputId) {
    const pass = document.getElementById(inputId);
    if (pass.type === "password") {
        pass.type = "text";
        eye.src = "static/assets/eye-open.png";
    } else {
        pass.type = "password";
        eye.src = "static/assets/eye-close.png";
    }
}

function showSignUp() {
        document.getElementById("container").classList.add("active");
    }

function showSignIn() {
    document.getElementById("container").classList.remove("active");
}