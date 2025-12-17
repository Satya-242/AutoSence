from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings
from .forms import SignUpForm, CarForm, PredictForm, PurchaseForm
from .models import Car, Purchase
from django.db.models import Avg, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

import os
import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from .forms import PredictForm 
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Notification, Car
@login_required
@ensure_csrf_cookie
def home(request):
    # Show landing page with a few featured approved cars
    cars = Car.objects.filter(status="APPROVED").order_by("-id")[:6]
    return render(request, "landing.html", {"cars": cars})

# ---------- Auth ----------
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful! You can now login.")
            return redirect("login")
        else:
            # Get the first error message from the form
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
                    break  # Only show the first error
                break
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def all_notifications(request):
    notifications = request.user.notifications.select_related('car').order_by('-created_at')
    return render(request, 'notifications/all.html', {'notifications': notifications})

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})
##-----------------------------------------------------------
@login_required
def mark_all_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def get_unread_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).select_related('car').order_by('-created_at')[:10]
    
    return JsonResponse({
        'notifications': [{
            'id': n.id,
            'message': n.message,
            'type': n.notification_type,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
            'car_id': n.car_id,
            'is_read': n.is_read
        } for n in notifications]
    })

# ---------- Cars ----------
@login_required
def car_list(request):
    # Buyers see only approved cars; admins see all
    if request.user.is_authenticated and request.user.is_superuser:
        cars = Car.objects.all()
    else:
        cars = Car.objects.filter(status="APPROVED")
    return render(request, "cars/car_list.html", {"cars": cars})

@login_required
def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if car.status != "APPROVED" and not (request.user.is_authenticated and (request.user == car.seller or request.user.is_superuser)):
        messages.error(request, "This listing is not available.")
        return redirect("car_list")
    return render(request, "cars/car_detail.html", {"car": car})

@login_required
def upload_car(request):
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.seller = request.user
            car.status = "PENDING"     # require admin approval
            car.save()
            messages.info(request, "Car submitted. Awaiting admin approval.")
            return redirect("my_listings")
    else:
        form = CarForm()
    return render(request, "cars/upload_car.html", {"form": form})

@login_required
def my_listings(request):
    cars = Car.objects.filter(seller=request.user)
    return render(request, "cars/my_listings.html", {"cars": cars})

# ----- Admin moderation -----

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def approve_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    car.status = "APPROVED"
    car.save()
    
    # Create notification
    Notification.objects.create(
        user=car.seller,
        car=car,
        notification_type='APPROVED',
        message=f'Your car listing "{car.name}" has been approved and is now visible to buyers.'
    )
    
    messages.success(request, "Car approved successfully.")
    return redirect("admin_dashboard")  # Changed from "dashboard" to "admin_dashboard"

@login_required
@user_passes_test(is_admin)
def reject_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    car.status = "REJECTED"
    car.save()
    
    # Create notification
    Notification.objects.create(
        user=car.seller,
        car=car,
        notification_type='REJECTED',
        message=f'Your car listing "{car.name}" has been rejected. Please check the listing for details.'
    )
    
    messages.success(request, "Car rejected.")
    return redirect("admin_dashboard")

@user_passes_test(is_admin)
def approve_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    car.status = "APPROVED"
    car.save()
    messages.success(request, "Listing approved.")
    return redirect("car_detail", pk=pk)

@user_passes_test(is_admin)
def reject_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    car.status = "REJECTED"
    car.save()
    messages.warning(request, "Listing rejected.")
    return redirect("car_detail", pk=pk)

@user_passes_test(is_admin)
def delete_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    car.delete()
    messages.success(request, "Listing deleted.")
    return redirect("car_list")

@user_passes_test(is_admin)
def edit_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, "Listing updated.")
            return redirect("car_detail", pk=pk)
    else:
        form = CarForm(instance=car)
    return render(request, "cars/upload_car.html", {"form": form})



# ---------- Dashboards ----------
@user_passes_test(is_admin)
def admin_dashboard(request):
    pending_cars = Car.objects.filter(status="PENDING").order_by("-created_at")[:10]
    pending_count = Car.objects.filter(status="PENDING").count()
    approved_count = Car.objects.filter(status="APPROVED").count()
    seller_count = Car.objects.values("seller").distinct().count()
    total_cars = Car.objects.count()
    avg_expected = Car.objects.aggregate(avg=Avg("expected_price")).get("avg") or 0
    newest_car = Car.objects.order_by("-created_at").first()
    top_fuel = Car.objects.values("fuel").annotate(c=Count("id")).order_by("-c").first()
    context = {
        "pending_cars": pending_cars,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "seller_count": seller_count,
        "total_cars": total_cars,
        "avg_expected": avg_expected,
        "newest_car": newest_car or {"name": "—"},
        "top_fuel": (top_fuel or {}).get("fuel", "—"),
    }
    return render(request, "admin/dashboard.html", context)

@login_required
def customer_dashboard(request):
    my_cars = Car.objects.filter(seller=request.user).order_by("-created_at")
    return render(request, "customers/dashboard.html", {"my_cars": my_cars})

# ---------- Purchase flow ----------
@login_required
def purchase_view(request, pk):
    car = get_object_or_404(Car, pk=pk, status="APPROVED")
    if request.method == "POST":
        form = PurchaseForm(request.POST)
        if form.is_valid():
            if car.status != "APPROVED":
                messages.error(request, "This car is no longer available.")
                return redirect("car_detail", pk=pk)
            purchase = Purchase.objects.create(
                car=car,
                buyer=request.user,
                full_name=form.cleaned_data["full_name"],
                email=form.cleaned_data["email"],
                phone=form.cleaned_data["phone"],
                address=form.cleaned_data["address"],
                agreed_terms=form.cleaned_data["agreed_terms"],
            )
            car.status = "SOLD"
            car.save()
            messages.success(request, "Purchase completed successfully.")
            return render(request, "cars/purchase_success.html", {"car": car, "purchase": purchase})
    else:
        form = PurchaseForm()
    return render(request, "cars/purchase_form.html", {"car": car, "form": form})

@require_http_methods(["POST"])
@login_required
def api_purchase(request, pk):
    car = get_object_or_404(Car, pk=pk, status="APPROVED")
    try:
        payload = request.POST.dict() if request.POST else json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = {}
    form = PurchaseForm(payload)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    purchase = Purchase.objects.create(
        car=car,
        buyer=request.user,
        full_name=form.cleaned_data["full_name"],
        email=form.cleaned_data["email"],
        phone=form.cleaned_data["phone"],
        address=form.cleaned_data["address"],
        agreed_terms=form.cleaned_data["agreed_terms"],
    )
    car.status = "SOLD"
    car.save()
    return JsonResponse({"ok": True, "purchase_id": purchase.id})

# ---------- API (JSON) ----------
def car_to_dict(car: Car):
    return {
        "id": car.id,
        "name": car.name,
        "year": car.year,
        "fuel": car.fuel,
        "transmission": car.transmission,
        "expected_price": car.expected_price,
        "predicted_price": car.predicted_price,
        "status": car.status,
        "image": car.image.url if car.image else None,
        "seller": car.seller.username,
        "created_at": car.created_at.isoformat(),
    }

@require_http_methods(["GET"])
@login_required
def api_cars(request):
    qs = Car.objects.filter(status="APPROVED")
    data = [car_to_dict(c) for c in qs]
    return JsonResponse({"results": data})

@require_http_methods(["GET"])
@user_passes_test(is_admin)
def api_cars_pending(request):
    qs = Car.objects.filter(status="PENDING").order_by("-created_at")
    data = [car_to_dict(c) for c in qs]
    return JsonResponse({"results": data})

@require_http_methods(["GET"])
@login_required
def api_stats(request):
    return JsonResponse({
        "total": Car.objects.count(),
        "approved": Car.objects.filter(status="APPROVED").count(),
        "pending": Car.objects.filter(status="PENDING").count(),
    })

@require_http_methods(["GET"])
@login_required
def api_my_cars(request):
    qs = Car.objects.filter(seller=request.user).order_by("-created_at")
    return JsonResponse({"results": [car_to_dict(c) for c in qs]})

@require_http_methods(["POST"])
@user_passes_test(is_admin)
def api_car_approve(request, pk):
    car = get_object_or_404(Car, pk=pk)
    car.status = "APPROVED"
    car.save()
    return JsonResponse({"ok": True, "car": car_to_dict(car)})

@require_http_methods(["POST"])
@user_passes_test(is_admin)
def api_car_reject(request, pk):
    car = get_object_or_404(Car, pk=pk)
    car.status = "REJECTED"
    car.save()
    return JsonResponse({"ok": True, "car": car_to_dict(car)})

# ---------- Price Prediction (optional) ----------
MODEL_PATH = os.path.join(settings.BASE_DIR, 'market', 'car_price_predictor.joblib')
MODEL = joblib.load("C:/Users/itssa/OneDrive/Desktop/carhub/market/car_price_predictor.joblib")
# if you make a details.html
@login_required
def predict_view(request):
    prediction = None

    if request.method == 'POST':
        form = PredictForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Arrange in the same order as during training
            features = np.array([[
               
                data['km_driven'],
                data['fuel'], 
                data['seller_type'],
                data['transmission'],
                data['owner'],
                data['mileage'],
                data['engine'],
                data['max_power'],
                data['torque'],
                data['seats'],
                data['Age']      # already numeric
        
            ]])

            # Predict
            y_pred = MODEL.predict(features)[0]
            prediction = round(float(y_pred), 2)

    else:
        form = PredictForm()

    return render(request, 'cars/predict.html', {'form': form, 'prediction': prediction})

