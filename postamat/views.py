import json

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
import secrets
import string
from django.contrib.auth.models import User, Group
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Postamat, Order
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .services import PostamatService



def admin_login_redirect(request):
    return redirect('/accounts/login/?next=/admin/')


def user_in_groups(user, group_names):
    from django.contrib.auth.models import Group
    for name in group_names:
        group, created = Group.objects.get_or_create(name=name)
        if user.groups.filter(name=name).exists():
            return True
    return False


def verify_code(request, postamat_id):
    """Verify code endpoint to redirect user to a register form"""
    if request.method == 'POST':
        receive_code = request.POST.get('receive_code')
        if not receive_code:
            return render(request, 'postamat/verify_code.html', {
                'postamat_id': postamat_id,
                'error': 'Enter a code'
            })
        try:
            service = PostamatService(postamat_id)
            result = service.get_order(receive_code)
            request.session['pending_order'] = {
                'order_id': result['order_id'],
                'cell_number': result['cell_number'],
            }
            return redirect('postamat:register_for_order', postamat_id=postamat_id)
        except Exception as e:
            return render(request, 'postamat/verify_code.html', {
                'postamat_id': postamat_id,
                'error': str(e)
            })
    return render(request, 'postamat/verify_code.html', {'postamat_id': postamat_id})


def register_for_order(request, postamat_id):
    """Register form and order get."""
    if 'pending_order' not in request.session:
        return redirect('postamat:verify_code', postamat_id=postamat_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        errors = {}
        if not username:
            errors['username'] = 'Login required'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'User with this username already exists'

        if email and User.objects.filter(email=email).exists():
            errors['email'] = 'User with this email already exists'

        if not password:
            errors['password'] = 'Enter password'
        elif len(password) < 6:
            errors['password'] = 'Password cannot be less than 6'
        elif password != confirm_password:
            errors['password'] = 'Password does not match'

        if errors:
            return render(request, 'postamat/register_for_order.html', {
                'postamat_id': postamat_id,
                'errors': errors,
                'username': username,
                'email': email,
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        users_group, _ = Group.objects.get_or_create(name='Users')
        user.groups.add(users_group)

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        order_data = request.session.pop('pending_order', None)
        if order_data:
            context = {
                'success': f"Order {order_data['order_id']} received! Cell {order_data['cell_number']}.",
                'order_id': order_data['order_id'],
                'cell_number': order_data['cell_number'],
            }
        else:
            context = {'error': 'Error: order data cannot be found'}
        return render(request, 'postamat/register_for_order.html', context)

    return render(request, 'postamat/register_for_order.html', {'postamat_id': postamat_id})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def place_order(request, postamat_id) -> HttpResponseForbidden | JsonResponse:
    """Endpoint to create an order for courier.

    :param request: Http request object. Expects json like: {"order_id": "123", "user_phone": "+79991234567"}
    :param postamat_id: string with postamat id
    :return: JsonResponse with 200 status
    :rtype: JsonResponse
    :raises Http404: If postamat id is not valid or can't be found.
    :raises Http400: If unknown error occurs.
    :raises HttpResponseForbidden: If user does not have permission to place order.
    """
    if not user_in_groups(request.user, ['Couriers', 'Admins']):
        return HttpResponseForbidden("Only couriers and administrators can place orders")

    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        user_phone = data.get('user_phone')
        if not order_id or not user_phone:
            return JsonResponse({'error': 'Missing order_id or user_phone'}, status=400)

        service = PostamatService(postamat_id)
        result = service.place_order(order_id, user_phone)
        return JsonResponse(result, status=200)

    except Postamat.DoesNotExist:
        return JsonResponse({'error': 'Postamat not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def get_order(request, postamat_id) -> HttpResponseForbidden | JsonResponse:
    """Endpoint to get an order from courier.

    :param request: Http request object. Expects json like: {"receive_code": "123456"}
    :param postamat_id: string with postamat id
    :return: JsonResponse with 200 status
    :rtype: JsonResponse
    :raises Http404: If postamat id is not valid or can't be found.
    :raises Http400: If unknown error occurs.
    :raises HttpResponseForbidden: If user does not have permission to get order.
    """
    if not user_in_groups(request.user, ['Users', 'Admins']):
        return HttpResponseForbidden("Only users and administrators can get orders")

    try:
        data = json.loads(request.body)
        receive_code = data.get('receive_code')
        if not receive_code:
            return JsonResponse({'error': 'Missing receive_code'}, status=400)

        service = PostamatService(postamat_id)
        result = service.get_order(receive_code)
        return JsonResponse(result, status=200)

    except Postamat.DoesNotExist:
        return JsonResponse({'error': 'Postamat not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def index(request):
    return render(request, 'postamat/index.html')


@login_required
def place_order_ui(request, postamat_id):
    if not user_in_groups(request.user, ['Couriers', 'Admins']):
        return HttpResponseForbidden("You don't have enough rights to place orders")

    context = {'postamat_id': postamat_id}
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        user_phone = request.POST.get('user_phone')
        if not order_id or not user_phone:
            context['result'] = {'error': 'All fields needs to be filled'}
        else:
            try:
                service = PostamatService(postamat_id)
                result = service.place_order(order_id, user_phone)
                context['result'] = {
                    'success': f"Order {result['order_id']} placed in cell {result['cell_number']}. Code for user: {result['receive_code']}"
                }
            except ValidationError as e:
                context['result'] = {'error': str(e)}
            except Exception as e:
                context['result'] = {'error': f'Error: {e}'}
    return render(request, 'postamat/place_order.html', context)


@login_required
def get_order_ui(request, postamat_id):
    if not user_in_groups(request.user, ['Users', 'Admins']):
        return HttpResponseForbidden("You don't have enough rights to get orders")

    context = {'postamat_id': postamat_id}
    if request.method == 'POST':
        receive_code = request.POST.get('receive_code')
        if not receive_code:
            context['result'] = {'error': 'Enter a code'}
        else:
            try:
                service = PostamatService(postamat_id)
                result = service.get_order(receive_code)
                context['result'] = {
                    'success': f"Your order {result['order_id']} is in a cell {result['cell_number']} is gived to you."
                }
            except ValidationError as e:
                context['result'] = {'error': str(e)}
            except Exception as e:
                context['result'] = {'error': f'Error: {e}'}
    return render(request, 'postamat/get_order.html', context)
