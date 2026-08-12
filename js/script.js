// =====================================================
// BLOSSOM FLOWER SHOP
// MAIN JAVASCRIPT
// =====================================================


// =====================================================
// API URL
// =====================================================

// IMPORTANT:
// Same Flask server par API call hogi.
// Localhost ya Render URL hard-code nahi karna.
const API_URL = "";


// =====================================================
// WELCOME MESSAGE
// =====================================================

function showMessage() {

    alert(
        "Welcome to Blossom Flower Shop 🌸"
    );

}


// =====================================================
// GET CURRENT USER
// =====================================================

function getCurrentUser() {

    try {

        const userData =
            localStorage.getItem(
                "currentUser"
            );

        if (!userData) {

            return null;

        }

        return JSON.parse(
            userData
        );

    }

    catch (error) {

        console.error(
            "Current user error:",
            error
        );

        return null;

    }

}


// =====================================================
// FLOWERS DATA
// =====================================================

const flowers = [

    {
        id: 1,

        name: "Red Rose Bouquet",

        price: 499,

        category: "Rose",

        image:
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTN0u_f6epoFsPf9lCYk16g4BjX0t_t905M1fXeKoFoLA&s=10"
    },

    {
        id: 2,

        name: "White Lily",

        price: 599,

        category: "Lily",

        image:
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR3NXBjVReLYS9wxPhwSR0Mre8DXZrahLrNJdcLPfvUJJWEldbDsy6EQJb4&s=10"
    },

    {
        id: 3,

        name: "Pink Tulip",

        price: 699,

        category: "Tulip",

        image:
            "https://i.pinimg.com/474x/e3/f2/fd/e3f2fd17277183a52572a8bd8748611c.jpg"
    },

    {
        id: 4,

        name: "Sunflower Bouquet",

        price: 399,

        category: "Sunflower",

        image:
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQeOYVih7e5H88rQD_fDzEN_Y29_L-OpWQ_Qimd-qPiCnOFgBtbX-heVM1S&s=10"
    }

];


// =====================================================
// FLOWER CONTAINER
// =====================================================

const container =
    document.getElementById(
        "flowerContainer"
    );


// =====================================================
// DISPLAY FLOWERS
// =====================================================

function displayFlowers(list) {

    if (!container) {

        return;

    }

    container.innerHTML = "";


    if (
        !list ||
        list.length === 0
    ) {

        container.innerHTML = `

            <div
                style="
                    text-align:center;
                    width:100%;
                    padding:40px;
                "
            >

                <h2>
                    🌸 No Flowers Found
                </h2>

                <p>
                    Try another flower name.
                </p>

            </div>

        `;

        return;

    }


    list.forEach(
        function(flower) {

            container.innerHTML += `

                <div class="flower-card">

                    <img
                        src="${flower.image}"
                        alt="${flower.name}"
                    >

                    <h3>
                        ${flower.name}
                    </h3>

                    <p>
                        ₹${flower.price}
                    </p>

                    <button
                        onclick="addToCart(${flower.id})"
                    >
                        Add to Cart
                    </button>

                </div>

            `;

        }
    );

}


// =====================================================
// SEARCH FLOWERS
// =====================================================

function searchFlower() {

    const searchInput =
        document.getElementById(
            "search"
        );


    if (!searchInput) {

        return;

    }


    const input =
        searchInput.value
            .trim()
            .toUpperCase();


    const cards =
        document.querySelectorAll(
            ".card"
        );


    cards.forEach(
        function(card) {

            const heading =
                card.querySelector(
                    "h3"
                );


            if (!heading) {

                return;

            }


            const name =
                heading.innerText
                    .toUpperCase();


            if (
                name.includes(input)
            ) {

                card.style.display =
                    "block";

            }

            else {

                card.style.display =
                    "none";

            }

        }
    );

}


// =====================================================
// SEARCH BOX
// =====================================================

const searchBox =
    document.getElementById(
        "searchBox"
    );


if (searchBox) {

    searchBox.addEventListener(
        "keyup",
        function() {

            const value =
                this.value
                    .toLowerCase()
                    .trim();


            const filtered =
                flowers.filter(
                    function(flower) {

                        return flower.name
                            .toLowerCase()
                            .includes(value);

                    }
                );


            displayFlowers(
                filtered
            );

        }
    );

}


// =====================================================
// FILTER FLOWERS
// =====================================================

function filterFlowers(
    category
) {

    if (
        category === "All"
    ) {

        displayFlowers(
            flowers
        );

        return;

    }


    const filtered =
        flowers.filter(
            function(flower) {

                return (
                    flower.category ===
                    category
                );

            }
        );


    displayFlowers(
        filtered
    );

}


// =====================================================
// ADD TO CART
// =====================================================

async function addToCart(
    flowerId
) {

    // ---------------------------------------------
    // CHECK LOGIN
    // ---------------------------------------------

    if (
        localStorage.getItem(
            "loggedIn"
        ) !== "true"
    ) {

        alert(
            "🌸 Please Login First!"
        );

        window.location.href =
            "/login";

        return;

    }


    // ---------------------------------------------
    // GET CURRENT USER
    // ---------------------------------------------

    const currentUser =
        getCurrentUser();


    if (
        !currentUser ||
        !currentUser.id
    ) {

        alert(
            "🌸 Please Login First!"
        );

        window.location.href =
            "/login";

        return;

    }


    // ---------------------------------------------
    // FIND FLOWER
    // ---------------------------------------------

    const flower =
        flowers.find(
            function(item) {

                return (
                    Number(item.id) ===
                    Number(flowerId)
                );

            }
        );


    if (!flower) {

        alert(
            "Flower not found!"
        );

        return;

    }


    // ---------------------------------------------
    // SEND TO FLASK DATABASE
    // ---------------------------------------------

    try {

        const response =
            await fetch(
                `${API_URL}/api/cart`,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            user_id:
                                currentUser.id,

                            flower_id:
                                flower.id,

                            quantity:
                                1

                        })

                }
            );


        const data =
            await response.json();


        console.log(
            "Add Cart Response:",
            data
        );


        // -----------------------------------------
        // SUCCESS
        // -----------------------------------------

        if (
            response.ok &&
            data.success
        ) {

            alert(
                flower.name +
                " Added To Cart 🛒🌸"
            );

            return;

        }


        // -----------------------------------------
        // ERROR
        // -----------------------------------------

        alert(
            data.message ||
            "Unable to add flower to cart."
        );

    }

    catch (error) {

        console.error(
            "Add Cart Error:",
            error
        );

        alert(
            "Unable to connect to Flask server."
        );

    }

}


// =====================================================
// OLD addCart FUNCTION
// =====================================================

async function addCart(
    name,
    price
) {

    const flower =
        flowers.find(
            function(item) {

                return (
                    item.name === name
                );

            }
        );


    if (flower) {

        await addToCart(
            flower.id
        );

        return;

    }


    alert(
        "Flower not found!"
    );

}


// =====================================================
// CONTACT FORM
// =====================================================

const contactForm =
    document.getElementById(
        "contactForm"
    );


if (contactForm) {

    contactForm.addEventListener(
        "submit",
        function(event) {

            event.preventDefault();


            alert(
                "Thank you! Your message has been sent successfully 🌸"
            );


            contactForm.reset();

        }
    );

}


// =====================================================
// INITIALIZE FLOWERS
// =====================================================

if (container) {

    displayFlowers(
        flowers
    );

}