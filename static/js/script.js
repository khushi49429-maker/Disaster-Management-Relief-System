document.addEventListener("DOMContentLoaded", function () {

    console.log("ResQNow Website Loaded Successfully");

    const emergencyForm = document.querySelector(
        "#emergencyForm"
    );

    if (emergencyForm) {

        emergencyForm.addEventListener("submit", function(event) {

            const location = document.querySelector(
                "[name='location']"
            ).value.trim();

            if (location === "") {

                event.preventDefault();

                alert("Please enter your location.");

            }

        });

    }

});