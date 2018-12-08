$(function () {
    $('#btnSignUp').click(function () {

        $.ajax({
            url: '/signUp',
            data: $('form').serialize(),
            type: 'POST',
            success: function (response) {
                console.log(response);
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
});
$(document).ready(function () {
    $(".menu-icon").on("click", function () {
        $("nav ul").toggleClass("showing");
    });
});

// Scrolling Effect

$(window).on("scroll", function () {
    if ($(window).scrollTop()) {
        $('nav').addClass('black');
    }

    else {
        $('nav').removeClass('black');
    }
})