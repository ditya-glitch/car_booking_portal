from datetime import date

from .models import Car, Booking, Review

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect


# =====================================================
# HOME
# =====================================================

def home(request):

    search = request.GET.get("search", "").strip()
    category = request.GET.get("category", "").strip()
    fuel_type = request.GET.get("fuel_type", "").strip()
    transmission = request.GET.get("transmission", "").strip()
    location = request.GET.get("location", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    sort = request.GET.get("sort", "").strip()

    cars = Car.objects.all()

    # SEARCH
    if search:
        cars = cars.filter(
            Q(car_name__icontains=search)
            | Q(brand__icontains=search)
            | Q(model__icontains=search)
        )

    # CATEGORY
    if category:
        cars = cars.filter(category=category)

    # FUEL
    if fuel_type:
        cars = cars.filter(fuel_type=fuel_type)

    # TRANSMISSION
    if transmission:
        cars = cars.filter(transmission=transmission)

    # LOCATION
    if location:
        cars = cars.filter(location__icontains=location)

    # MIN PRICE
    if min_price:
        try:
            cars = cars.filter(price_per_day__gte=min_price)
        except (ValueError, TypeError):
            pass

    # MAX PRICE
    if max_price:
        try:
            cars = cars.filter(price_per_day__lte=max_price)
        except (ValueError, TypeError):
            pass

    # SORTING
    if sort == "price_low":
        cars = cars.order_by("price_per_day")

    elif sort == "price_high":
        cars = cars.order_by("-price_per_day")

    elif sort == "name":
        cars = cars.order_by("car_name")

    elif sort == "newest":
        cars = cars.order_by("-created_at")

    else:
        cars = cars.order_by("-created_at")

    context = {
        "cars": cars,
        "categories": Car.CATEGORY_CHOICES,
        "fuel_types": Car.FUEL_CHOICES,
        "transmissions": Car.TRANSMISSION_CHOICES,

        "search": search,
        "selected_category": category,
        "selected_fuel": fuel_type,
        "selected_transmission": transmission,
        "selected_location": location,

        "min_price": min_price,
        "max_price": max_price,
        "sort": sort,
    }

    return render(
        request,
        "home.html",
        context
    )


# =====================================================
# CAR DETAIL
# =====================================================

def car_detail(request, car_id):

    car = get_object_or_404(
        Car,
        id=car_id
    )

    return render(
        request,
        "car_detail.html",
        {
            "car": car
        }
    )


# =====================================================
# BOOK CAR
# =====================================================
@login_required
def book_car(request, car_id):

    car = get_object_or_404(
        Car,
        id=car_id
    )

    # CHECK CAR AVAILABILITY

    if not car.available:

        messages.error(
            request,
            "Sorry, this car is currently unavailable."
        )

        return redirect(
            "car_detail",
            car_id=car.id
        )

    # POST

    if request.method == "POST":

        customer_name = request.POST.get(
            "customer_name",
            ""
        ).strip()

        customer_email = request.POST.get(
            "customer_email",
            ""
        ).strip()

        customer_phone = request.POST.get(
            "customer_phone",
            ""
        ).strip()

        pickup_date = request.POST.get(
            "pickup_date",
            ""
        ).strip()

        return_date = request.POST.get(
            "return_date",
            ""
        ).strip()

        # CUSTOMER DETAILS

        if not customer_name:

            messages.error(
                request,
                "Please enter your name."
            )

            return render(
                request,
                "booking.html",
                {"car": car}
            )

        if not customer_email:

            messages.error(
                request,
                "Please enter your email."
            )

            return render(
                request,
                "booking.html",
                {"car": car}
            )

        if not customer_phone:

            messages.error(
                request,
                "Please enter your phone number."
            )

            return render(
                request,
                "booking.html",
                {"car": car}
            )

        if not pickup_date or not return_date:

            messages.error(
                request,
                "Please select pickup and return dates."
            )

            return render(
                request,
                "booking.html",
                {"car": car}
            )

        # CONVERT DATE

        try:

            pickup = date.fromisoformat(
                pickup_date
            )

            returning = date.fromisoformat(
                return_date
            )

        except (ValueError, TypeError):

            messages.error(
                request,
                "Please enter valid pickup and return dates."
            )

            return render(
                request,
                "booking.html",
                {"car": car}
            )

        # PAST DATE

        if pickup < date.today():

            messages.error(
                request,
                "Pickup date cannot be in the past."
            )

            return render(
                request,
                "booking.html",
                {"car": car}
            )

        # DATE ORDER

        total_days = (
            returning - pickup
        ).days

        if total_days <= 0:

            messages.error(
                request,
                "Return date must be after pickup date."
            )

            return render(
                request,
                "booking.html",
                {"car": car}
            )

        # DOUBLE BOOKING

        existing_booking = Booking.objects.filter(
            car=car,
            pickup_date__lt=returning,
            return_date__gt=pickup,
            status__in=[
                "Pending",
                "Confirmed"
            ]
        ).first()

        if existing_booking:

            messages.error(
                request,
                "Sorry, this car is already booked for the selected dates."
            )

            return render(
                request,
                "booking.html",
                {
                    "car": car,
                    "error": "This car is already booked for the selected dates."
                }
            )

        # PRICE

        total_price = (
            total_days *
            car.price_per_day
        )

        # CREATE BOOKING

        booking = Booking.objects.create(

            car=car,

            customer_name=customer_name,

            customer_email=customer_email,

            customer_phone=customer_phone,

            pickup_date=pickup,

            return_date=returning,

            total_days=total_days,

            total_price=total_price,

            status="Pending"
        )

        messages.success(
            request,
            "Your booking has been submitted successfully."
        )

        return redirect(
            "booking_success",
            booking_id=booking.booking_id
        )

    return render(
        request,
        "booking.html",
        {
            "car": car
        }
    )


# =====================================================
# BOOKING SUCCESS
# =====================================================

def booking_success(request, booking_id):

    booking = get_object_or_404(
        Booking,
        booking_id=booking_id
    )

    return render(
        request,
        "booking_success.html",
        {
            "booking": booking
        }
    )


# =====================================================
# MY BOOKINGS
# =====================================================

def my_bookings(request):

    bookings = []

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip()

        bookings = Booking.objects.filter(
            customer_email=email
        ).select_related(
            "car"
        ).order_by(
            "-created_at"
        )

    return render(
        request,
        "my_bookings.html",
        {
            "bookings": bookings
        }
    )


# =====================================================
# REGISTER
# =====================================================

def register(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        email = request.POST.get(
            "email"
        )

        password = request.POST.get(
            "password"
        )

        confirm_password = request.POST.get(
            "confirm_password"
        )

        # PASSWORD CHECK

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect(
                "register"
            )

        # USERNAME CHECK

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect(
                "register"
            )

        # EMAIL CHECK

        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "Email is already registered."
            )

            return redirect(
                "register"
            )

        # CREATE USER

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password
        )

        user.save()

        messages.success(
            request,
            "Registration successful. You can now login."
        )

        return redirect(
            "login"
        )

    return render(
        request,
        "register.html"
    )


# =====================================================
# LOGIN
# =====================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            # ADMIN

            if user.is_staff:

                return redirect(
                    "dashboard"
                )

            # NORMAL USER

            return redirect(
                "user_dashboard"
            )

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "login.html"
    )


# =====================================================
# LOGOUT
# =====================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect(
        "home"
    )


# =====================================================
# CANCEL BOOKING
# =====================================================

def cancel_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        booking_id=booking_id
    )

    if request.method == "POST":

        if booking.status == "Cancelled":

            messages.warning(
                request,
                "This booking is already cancelled."
            )

            return redirect(
                "my_bookings"
            )

        booking.status = "Cancelled"

        booking.save()

        messages.success(
            request,
            "Your booking has been cancelled successfully."
        )

        return redirect(
            "my_bookings"
        )

    return render(
        request,
        "cancel_booking.html",
        {
            "booking": booking
        }
    )


# =====================================================
# ADMIN DASHBOARD
# =====================================================

@login_required
def dashboard(request):

    # ADMIN / STAFF CHECK

    if not request.user.is_staff:

        messages.error(
            request,
            "You are not authorized to access the admin dashboard."
        )

        return redirect(
            "home"
        )

    # DASHBOARD STATISTICS

    total_cars = Car.objects.count()

    cars = Car.objects.all().order_by(
        "-created_at"
    )

    total_bookings = Booking.objects.count()

    pending_bookings = Booking.objects.filter(
        status="Pending"
    ).count()

    confirmed_bookings = Booking.objects.filter(
        status="Confirmed"
    ).count()

    completed_bookings = Booking.objects.filter(
        status="Completed"
    ).count()

    cancelled_bookings = Booking.objects.filter(
        status="Cancelled"
    ).count()

    # RECENT BOOKINGS

    recent_bookings = Booking.objects.select_related(
        "car"
    ).order_by(
        "-created_at"
    )[:10]

    context = {

        "total_cars": total_cars,

        "total_bookings": total_bookings,

        "pending_bookings": pending_bookings,

        "confirmed_bookings": confirmed_bookings,

        "completed_bookings": completed_bookings,

        "cancelled_bookings": cancelled_bookings,

        "recent_bookings": recent_bookings,

        "cars": cars,
    }

    return render(
        request,
        "dashboard.html",
        context
    )


# =====================================================
# USER DASHBOARD
# =====================================================

@login_required
def user_dashboard(request):

    bookings = Booking.objects.filter(
        customer_email=request.user.email
    ).select_related(
        "car"
    ).order_by(
        "-created_at"
    )

    # COUNTS

    total_bookings = bookings.count()

    pending_bookings = bookings.filter(
        status="Pending"
    ).count()

    confirmed_bookings = bookings.filter(
        status="Confirmed"
    ).count()

    completed_bookings = bookings.filter(
        status="Completed"
    ).count()

    cancelled_bookings = bookings.filter(
        status="Cancelled"
    ).count()

    # RECENT BOOKINGS

    recent_bookings = bookings[:5]

    context = {

        "total_bookings": total_bookings,

        "pending_bookings": pending_bookings,

        "confirmed_bookings": confirmed_bookings,

        "completed_bookings": completed_bookings,

        "cancelled_bookings": cancelled_bookings,

        "recent_bookings": recent_bookings,
    }

    return render(
        request,
        "user_dashboard.html",
        context
    )


# =====================================================
# UPDATE BOOKING STATUS
# =====================================================

@login_required
def update_booking_status(request, booking_id):

    # ADMIN CHECK

    if not request.user.is_staff:

        messages.error(
            request,
            "You are not authorized to perform this action."
        )

        return redirect(
            "home"
        )

    # GET BOOKING

    booking = get_object_or_404(
        Booking,
        booking_id=booking_id
    )

    # UPDATE STATUS

    if request.method == "POST":

        new_status = request.POST.get(
            "status"
        )

        allowed_statuses = [
            "Pending",
            "Confirmed",
            "Completed",
            "Cancelled",
        ]

        if new_status not in allowed_statuses:

            messages.error(
                request,
                "Invalid booking status."
            )

            return redirect(
                "dashboard"
            )

        booking.status = new_status

        booking.save()

        messages.success(
            request,
            f"Booking {booking.booking_id} status updated successfully."
        )

    return redirect(
        "dashboard"
    )


# =====================================================
# BOOKING DETAILS
# =====================================================

@login_required
def booking_detail(request, booking_id):

    booking = get_object_or_404(
        Booking.objects.select_related(
            "car"
        ),
        booking_id=booking_id
    )

    # NORMAL USER CAN SEE ONLY OWN BOOKING

    if not request.user.is_staff:

        if booking.customer_email != request.user.email:

            messages.error(
                request,
                "You are not authorized to view this booking."
            )

            return redirect(
                "user_dashboard"
            )

    return render(
        request,
        "booking_detail.html",
        {
            "booking": booking
        }
    )


# =====================================================
# ADD CAR
# =====================================================

@login_required
def add_car(request):

    # ADMIN CHECK

    if not request.user.is_staff:

        messages.error(
            request,
            "You are not authorized to add cars."
        )

        return redirect(
            "home"
        )

    # POST

    if request.method == "POST":

        car_name = request.POST.get(
            "car_name",
            ""
        ).strip()

        brand = request.POST.get(
            "brand",
            ""
        ).strip()

        model = request.POST.get(
            "model",
            ""
        ).strip()

        category = request.POST.get(
            "category",
            ""
        ).strip()

        fuel_type = request.POST.get(
            "fuel_type",
            ""
        ).strip()

        transmission = request.POST.get(
            "transmission",
            ""
        ).strip()

        seats = request.POST.get(
            "seats",
            ""
        ).strip()

        price_per_day = request.POST.get(
            "price_per_day",
            ""
        ).strip()

        location = request.POST.get(
            "location",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        car_image = request.FILES.get(
            "car_image"
        )

        # VALIDATION

        if not car_name:

            messages.error(
                request,
                "Please enter car name."
            )

            return redirect(
                "add_car"
            )

        if not brand:

            messages.error(
                request,
                "Please enter brand."
            )

            return redirect(
                "add_car"
            )

        if not model:

            messages.error(
                request,
                "Please enter model."
            )

            return redirect(
                "add_car"
            )

        if not category:

            messages.error(
                request,
                "Please select category."
            )

            return redirect(
                "add_car"
            )

        if not fuel_type:

            messages.error(
                request,
                "Please select fuel type."
            )

            return redirect(
                "add_car"
            )

        if not transmission:

            messages.error(
                request,
                "Please select transmission."
            )

            return redirect(
                "add_car"
            )

        if not seats:

            messages.error(
                request,
                "Please enter number of seats."
            )

            return redirect(
                "add_car"
            )

        if not price_per_day:

            messages.error(
                request,
                "Please enter price per day."
            )

            return redirect(
                "add_car"
            )

        if not location:

            messages.error(
                request,
                "Please enter location."
            )

            return redirect(
                "add_car"
            )

        if not description:

            messages.error(
                request,
                "Please enter description."
            )

            return redirect(
                "add_car"
            )

        # CREATE CAR

        Car.objects.create(

            car_name=car_name,

            brand=brand,

            model=model,

            category=category,

            fuel_type=fuel_type,

            transmission=transmission,

            seats=seats,

            price_per_day=price_per_day,

            location=location,

            description=description,

            car_image=car_image,

            available=True
        )

        messages.success(
            request,
            "Car added successfully."
        )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "add_car.html"
    )


# =====================================================
# EDIT CAR
# =====================================================

@login_required
def edit_car(request, car_id):

    # ADMIN CHECK

    if not request.user.is_staff:

        messages.error(
            request,
            "You are not authorized to edit cars."
        )

        return redirect(
            "home"
        )

    # GET CAR

    car = get_object_or_404(
        Car,
        id=car_id
    )

    # POST

    if request.method == "POST":

        car.car_name = request.POST.get(
            "car_name",
            ""
        ).strip()

        car.brand = request.POST.get(
            "brand",
            ""
        ).strip()

        car.model = request.POST.get(
            "model",
            ""
        ).strip()

        car.category = request.POST.get(
            "category",
            ""
        ).strip()

        car.fuel_type = request.POST.get(
            "fuel_type",
            ""
        ).strip()

        car.transmission = request.POST.get(
            "transmission",
            ""
        ).strip()

        car.seats = request.POST.get(
            "seats",
            ""
        ).strip()

        car.price_per_day = request.POST.get(
            "price_per_day",
            ""
        ).strip()

        car.location = request.POST.get(
            "location",
            ""
        ).strip()

        car.description = request.POST.get(
            "description",
            ""
        ).strip()

        car.available = (
            "available"
            in request.POST
        )

        car_image = request.FILES.get(
            "car_image"
        )

        if car_image:

            car.car_image = car_image

        car.save()

        messages.success(
            request,
            "Car updated successfully."
        )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "edit_car.html",
        {
            "car": car
        }
    )


# =====================================================
# DELETE CAR
# =====================================================

@login_required
def delete_car(request, car_id):

    # ADMIN CHECK

    if not request.user.is_staff:

        messages.error(
            request,
            "You are not authorized to delete cars."
        )

        return redirect(
            "home"
        )

    # GET CAR

    car = get_object_or_404(
        Car,
        id=car_id
    )

    # DELETE ONLY ON POST

    if request.method == "POST":

        car_name = car.car_name

        car.delete()

        messages.success(
            request,
            f"{car_name} has been deleted successfully."
        )

        return redirect(
            "dashboard"
        )

    # CONFIRMATION PAGE

    return render(
        request,
        "delete_car.html",
        {
            "car": car
        }
    )


# =====================================================
# ADD REVIEW
# =====================================================

@login_required
def add_review(request, car_id):

    car = get_object_or_404(
        Car,
        id=car_id
    )

    if request.method == "POST":

        rating = request.POST.get(
            "rating"
        )

        comment = request.POST.get(
            "comment",
            ""
        ).strip()

        # ---------------------------------------------
        # RATING REQUIRED
        # ---------------------------------------------

        if not rating:

            messages.error(
                request,
                "Please select a rating."
            )

            return redirect(
                "car_detail",
                car_id=car.id
            )

        # ---------------------------------------------
        # CONVERT RATING TO INTEGER
        # ---------------------------------------------

        try:

            rating = int(rating)

        except (ValueError, TypeError):

            messages.error(
                request,
                "Invalid rating."
            )

            return redirect(
                "car_detail",
                car_id=car.id
            )

        # ---------------------------------------------
        # RATING RANGE
        # ---------------------------------------------

        if rating < 1 or rating > 5:

            messages.error(
                request,
                "Rating must be between 1 and 5."
            )

            return redirect(
                "car_detail",
                car_id=car.id
            )

        # ---------------------------------------------
        # COMMENT
        # ---------------------------------------------

        if not comment:

            messages.error(
                request,
                "Please write a review."
            )

            return redirect(
                "car_detail",
                car_id=car.id
            )

        # ---------------------------------------------
        # CREATE REVIEW
        # ---------------------------------------------

        Review.objects.create(

            car=car,

            customer_name=(
                request.user.get_full_name()
                or request.user.username
            ),

            customer_email=request.user.email,

            rating=rating,

            comment=comment
        )

        messages.success(
            request,
            "Your review has been submitted successfully."
        )

    return redirect(
        "car_detail",
        car_id=car.id
    )