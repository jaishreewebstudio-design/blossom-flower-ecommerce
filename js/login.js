// =====================================================
// BLOSSOM FLOWER SHOP
// LOGIN JAVASCRIPT
// =====================================================

const API_URL = "http://127.0.0.1:5000";

// =====================================================
// LOGIN FORM
// =====================================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function(event) {

        // IMPORTANT:
        // Stop normal form submission.
        // This prevents page refresh.
        event.preventDefault();

        console.log("LOGIN FORM SUBMITTED");

        // =================================================
        // GET INPUTS
        // =================================================

        const emailInput =
            document.getElementById("email");

        const passwordInput =
            document.getElementById("password");

        if (!emailInput || !passwordInput) {

            console.error(
                "Email or password input not found"
            );

            alert(
                "Login form fields not found."
            );

            return;
        }

        const email =
            emailInput.value.trim().toLowerCase();

        const password =
            passwordInput.value;

        // =================================================
        // VALIDATION
        // =================================================

        if (!email) {

            alert("Please enter your email.");

            emailInput.focus();

            return;
        }

        if (!password) {

            alert("Please enter your password.");

            passwordInput.focus();

            return;
        }

        // =================================================
        // DISABLE BUTTON
        // =================================================

        const loginButton =
            loginForm.querySelector(
                'button[type="submit"]'
            );

        if (loginButton) {

            loginButton.disabled = true;

            loginButton.innerText =
                "Logging in...";
        }

        // =================================================
        // SEND LOGIN REQUEST
        // =================================================

        try {

            console.log(
                "Sending login request..."
            );

            const response =
                await fetch(
                    `${API_URL}/api/login`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        credentials: "include",

                        body: JSON.stringify({

                            email: email,

                            password: password

                        })
                    }
                );

            // =================================================
            // GET RESPONSE
            // =================================================

            const data =
                await response.json();

            console.log(
                "Login response:",
                data
            );

            // =================================================
            // LOGIN SUCCESS
            // =================================================

            if (
                response.ok &&
                data.success
            ) {

                // ---------------------------------------------
                // SAVE LOGIN STATUS
                // ---------------------------------------------

                localStorage.setItem(
                    "loggedIn",
                    "true"
                );

                // ---------------------------------------------
                // SAVE CURRENT USER
                // ---------------------------------------------

                if (data.user) {

                    localStorage.setItem(
                        "currentUser",
                        JSON.stringify(
                            data.user
                        )
                    );
                }

                console.log(
                    "Login successful"
                );

                // ---------------------------------------------
                // REDIRECT TO DASHBOARD
                // ---------------------------------------------

                window.location.href =
                    "/dashboard";

                return;
            }

            // =================================================
            // USER NOT REGISTERED
            // =================================================

            if (
                response.status === 404 &&
                data.registered === false
            ) {

                alert(
                    data.message ||
                    "Please register first."
                );

                return;
            }

            // =================================================
            // WRONG PASSWORD
            // =================================================

            if (
                response.status === 401
            ) {

                alert(
                    data.message ||
                    "Incorrect password."
                );

                passwordInput.focus();

                return;
            }

            // =================================================
            // OTHER ERROR
            // =================================================

            alert(
                data.message ||
                "Login failed. Please try again."
            );

        } catch (error) {

            console.error(
                "Login error:",
                error
            );

            alert(
                "Unable to connect to Flask server."
            );

        } finally {

            // =================================================
            // ENABLE BUTTON AGAIN
            // =================================================

            if (loginButton) {

                loginButton.disabled = false;

                loginButton.innerText =
                    "Login";
            }
        }

    });

}