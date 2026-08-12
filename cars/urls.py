from django.urls import path

from . import views


urlpatterns = [

    # =================================================
    # HOME
    # =================================================

    path(
        "",
        views.home,
        name="home"
    ),

    # =================================================
    # CAR DETAIL
    # =================================================

    path(
        "car/<int:car_id>/",
        views.car_detail,
        name="car_detail"
    ),

    # =================================================
    # BOOK CAR
    # =================================================

    path(
        "book/<int:car_id>/",
        views.book_car,
        name="book_car"
    ),

    # =================================================
    # BOOKING SUCCESS
    # =================================================

    path(
        "booking-success/<str:booking_id>/",
        views.booking_success,
        name="booking_success"
    ),

    # =================================================
    # MY BOOKINGS
    # =================================================

    path(
        "my-bookings/",
        views.my_bookings,
        name="my_bookings"
    ),

    # =================================================
    # CANCEL BOOKING
    # =================================================

    path(
        "cancel-booking/<str:booking_id>/",
        views.cancel_booking,
        name="cancel_booking"
    ),

    # =================================================
    # BOOKING DETAILS
    # =================================================

    path(
        "booking/<str:booking_id>/",
        views.booking_detail,
        name="booking_detail"
    ),

    # =================================================
    # REGISTER
    # =================================================

    path(
        "register/",
        views.register,
        name="register"
    ),

    # =================================================
    # LOGIN
    # =================================================

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    # =================================================
    # LOGOUT
    # =================================================

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # =================================================
    # USER DASHBOARD
    # =================================================

    path(
        "user-dashboard/",
        views.user_dashboard,
        name="user_dashboard"
    ),

    # =================================================
    # ADMIN DASHBOARD
    # =================================================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    # =================================================
    # UPDATE BOOKING STATUS
    # =================================================

    path(
        "update-booking-status/<str:booking_id>/",
        views.update_booking_status,
        name="update_booking_status"
    ),

    # =================================================
    # ADD CAR
    # =================================================

    path(
        "add-car/",
        views.add_car,
        name="add_car"
    ),

    # =================================================
    # EDIT CAR
    # =================================================

    path(
        "edit-car/<int:car_id>/",
        views.edit_car,
        name="edit_car"
    ),

    # =================================================
    # DELETE CAR
    # =================================================

    path(
        "delete-car/<int:car_id>/",
        views.delete_car,
        name="delete_car"
    ),

    # =================================================
    # ADD REVIEW
    # =================================================

    path(
        "car/<int:car_id>/review/",
        views.add_review,
        name="add_review"
    ),

]